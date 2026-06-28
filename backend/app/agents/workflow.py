import os
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.tech_stack import detect_tech_stack
from app.agents.architecture import analyze_architecture
from app.agents.security import review_security
from app.agents.code_quality import analyze_code_quality
from app.agents.documentation import generate_documentation
from app.agents.interview import generate_interview_questions
from app.services.git_service import clone_repository, generate_tree_structure, list_all_files
from app.services.rag_service import index_repository

def clone_node(state: AgentState) -> dict:
    """
    Clones the repository and populates metadata, file lists, and tree structures.
    """
    repo_url = state["repo_url"]
    repo_path = state["repo_path"]
    
    # 1. Clone repository
    metadata = clone_repository(repo_url, repo_path)
    
    # 2. List all files
    files_list = list_all_files(repo_path)
    
    # 3. Generate directory tree representation
    tree_structure = generate_tree_structure(repo_path)
    
    return {
        "repo_name": metadata["repo_name"],
        "files_list": files_list,
        "tree_structure": tree_structure,
        "status": "cloned"
    }

def rag_indexing_node(state: AgentState) -> dict:
    """
    Chunks repository files and generates a local FAISS index for Q&A.
    """
    repo_path = state["repo_path"]
    analysis_id = state["analysis_id"]
    
    # Run the indexer
    success = index_repository(repo_path, analysis_id)
    
    return {
        "rag_indexed": success,
        "status": "indexed"
    }

def build_workflow():
    """
    Assembles and compiles the LangGraph StateGraph workflow.
    """
    # Initialize state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("clone", clone_node)
    workflow.add_node("tech_stack", detect_tech_stack)
    workflow.add_node("architecture", analyze_architecture)
    workflow.add_node("security", review_security)
    workflow.add_node("code_quality", analyze_code_quality)
    workflow.add_node("documentation", generate_documentation)
    workflow.add_node("interview", generate_interview_questions)
    workflow.add_node("rag_indexing", rag_indexing_node)
    
    # Set concurrent and sequential edges for optimized execution speed
    workflow.set_entry_point("clone")
    
    # Fan-out from clone to all independent nodes
    workflow.add_edge("clone", "tech_stack")
    workflow.add_edge("clone", "architecture")
    workflow.add_edge("clone", "security")
    workflow.add_edge("clone", "code_quality")
    
    # documentation and interview depend on tech_stack and architecture
    workflow.add_edge("tech_stack", "documentation")
    workflow.add_edge("architecture", "documentation")
    workflow.add_edge("tech_stack", "interview")
    workflow.add_edge("architecture", "interview")
    
    # Connect everything to the final RAG indexing node (wait barrier)
    workflow.add_edge("security", "rag_indexing")
    workflow.add_edge("code_quality", "rag_indexing")
    workflow.add_edge("documentation", "rag_indexing")
    workflow.add_edge("interview", "rag_indexing")
    
    workflow.add_edge("rag_indexing", END)
    
    return workflow.compile()
