import os
import logging
from typing import List, Dict, Any, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.services.git_service import list_all_files
from app.services.llm import query_llm

logger = logging.getLogger(__name__)

# Cache embeddings model to avoid reloading on every query
_embeddings_instance = None

# Cache loaded FAISS databases in memory to avoid reading from disk on every query
_faiss_db_cache = {}

def get_faiss_db(index_path: str, embeddings) -> FAISS:
    global _faiss_db_cache
    if index_path not in _faiss_db_cache:
        logger.info(f"Loading FAISS index from disk for {index_path}...")
        _faiss_db_cache[index_path] = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return _faiss_db_cache[index_path]

def clear_faiss_cache(analysis_id: str):
    """
    Clears the cached FAISS instance for a specific analysis run if it is re-indexed.
    """
    global _faiss_db_cache
    index_path = os.path.join(settings.FAISS_DIR, analysis_id)
    if index_path in _faiss_db_cache:
        del _faiss_db_cache[index_path]
        logger.info(f"Cleared FAISS cache for analysis {analysis_id}")

def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        try:
            logger.info("Initializing HuggingFaceEmbeddings with BAAI/bge-small-en-v1.5...")
            _embeddings_instance = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            logger.error(f"Failed to load HuggingFaceEmbeddings: {e}")
            raise e
    return _embeddings_instance

def index_repository(repo_path: str, analysis_id: str) -> bool:
    """
    Splits all repo source files into chunks, calculates BGE embeddings,
    and indexes them inside a local FAISS index file.
    """
    try:
        files = list_all_files(repo_path)
        documents: List[Document] = []
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\nclass ", "\ndef ", "\nfunction ", "\n\n", "\n", " ", ""]
        )
        
        for file in files:
            full_path = os.path.join(repo_path, file)
            if not os.path.exists(full_path):
                continue
                
            try:
                # Skip large files (>150 KB) to prevent CPU-bound embedding bottlenecks
                if os.path.getsize(full_path) > 150 * 1024:
                    logger.info(f"Skipping large file {file} ({os.path.getsize(full_path)} bytes) for indexing")
                    continue

                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                if not content.strip():
                    continue
                    
                chunks = splitter.split_text(content)
                for idx, chunk in enumerate(chunks):
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            "source": file,
                            "chunk_id": idx
                        }
                    ))
            except Exception as fe:
                logger.warning(f"Failed to read file {file} for RAG: {fe}")
                
        if not documents:
            logger.warning("No documents found to index for RAG.")
            return False
            
        # Try creating FAISS index
        try:
            embeddings = get_embeddings()
            db = FAISS.from_documents(documents, embeddings)
            index_path = os.path.join(settings.FAISS_DIR, analysis_id)
            db.save_local(index_path)
            logger.info(f"FAISS index successfully saved for analysis {analysis_id}")
            clear_faiss_cache(analysis_id)
            return True
        except Exception as embed_err:
            logger.error(f"Failed to create FAISS index, saving plaintext fallback file: {embed_err}")
            # Save raw chunks as a JSON fallback so keyword search can read them
            fallback_dir = os.path.join(settings.FAISS_DIR, analysis_id)
            os.makedirs(fallback_dir, exist_ok=True)
            fallback_path = os.path.join(fallback_dir, "fallback_chunks.json")
            
            chunks_data = [
                {"content": doc.page_content, "source": doc.metadata["source"]}
                for doc in documents
            ]
            import json
            with open(fallback_path, "w", encoding="utf-8") as f:
                json.dump(chunks_data, f)
            return True # Consider successful since fallback is ready
            
    except Exception as e:
        logger.error(f"Critical error in index_repository: {e}")
        return False

def query_repository_rag(analysis_id: str, query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Searches the FAISS vector database (or fallback text file) for relevant context
    and uses Ollama to answer the developer query.
    """
    if chat_history is None:
        chat_history = []
        
    index_path = os.path.join(settings.FAISS_DIR, analysis_id)
    fallback_path = os.path.join(index_path, "fallback_chunks.json")
    
    retrieved_docs: List[Tuple[str, str]] = [] # list of (source_file, text_content)
    
    # 1. Attempt Vector Search
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        try:
            embeddings = get_embeddings()
            db = get_faiss_db(index_path, embeddings)
            search_results = db.similarity_search(query, k=5)
            for doc in search_results:
                retrieved_docs.append((doc.metadata.get("source", "unknown"), doc.page_content))
        except Exception as e:
            logger.warning(f"Vector search failed, attempting fallback keyword search: {e}")
            
    # 2. Fallback Keyword Search
    if not retrieved_docs and os.path.exists(fallback_path):
        try:
            import json
            with open(fallback_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
                
            # Score chunks by keyword matches
            query_words = set(query.lower().split())
            scored_chunks = []
            for chunk in chunks:
                content = chunk["content"]
                score = sum(1 for word in query_words if word in content.lower())
                if score > 0:
                    scored_chunks.append((score, chunk))
                    
            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            for score, chunk in scored_chunks[:5]:
                retrieved_docs.append((chunk["source"], chunk["content"]))
        except Exception as e:
            logger.error(f"Fallback keyword search failed: {e}")
            
    # 3. Assemble LLM prompt
    context_blocks = []
    sources = []
    seen_sources = set()
    
    for file, content in retrieved_docs:
        context_blocks.append(f"--- File: {file} ---\n{content}\n")
        if file not in seen_sources:
            sources.append({
                "file": file,
                "snippet": content[:300] + "..." if len(content) > 300 else content
            })
            seen_sources.add(file)
            
    context_str = "\n".join(context_blocks)
    
    # Compile conversation history
    history_str = ""
    for msg in chat_history[-6:]: # last 6 messages
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"
        
    prompt = f"""
    You are an expert software engineering assistant. Use the codebase snippets below to answer the user's question.
    
    Codebase Context:
    {context_str}
    
    Conversation History:
    {history_str}
    
    Question: {query}
    
    Guidelines:
    1. Base your answer strictly on the provided codebase context when possible.
    2. If the context doesn't contain the answer, use your general knowledge but clearly state that it is not in the repository files.
    3. Include code examples or configuration adjustments if relevant.
    """
    
    system_prompt = "You are a senior developer helping a colleague understand the codebase."
    reply = query_llm(prompt, system_prompt=system_prompt)
    
    return {
        "reply": reply,
        "sources": sources
    }
