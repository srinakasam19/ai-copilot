import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Analysis, ChatMessage
from app.schemas import (
    AnalysisCreate, AnalysisResponse, ChatRequest, ChatResponse,
    ChatHistoryMessage, ReadmeResponse, SecurityResponse, InterviewResponse,
    AnalysisTriggerRequest
)
from app.agents.workflow import build_workflow
from app.services.rag_service import query_repository_rag
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

def run_analysis_pipeline_in_background(analysis_id: str, repo_url: str, db_session_factory):
    """
    Background worker running the LangGraph analysis pipeline and saving output to DB.
    """
    db: Session = db_session_factory()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found in DB.")
            return

        analysis.status = "analyzing"
        db.commit()

        repo_path = f"{settings.WORKSPACE_DIR}/{analysis_id}"
        
        # Initial agent state
        initial_state = {
            "analysis_id": analysis_id,
            "repo_url": repo_url,
            "repo_path": repo_path,
            "files_list": [],
            "tree_structure": {},
            "tech_stack": {},
            "architecture": {},
            "security": {},
            "code_quality": {},
            "documentation": {},
            "interview_questions": {},
            "rag_indexed": False,
            "status": "pending",
            "error_message": ""
        }

        # Build and execute the graph
        logger.info(f"Starting LangGraph workflow for analysis {analysis_id}...")
        graph = build_workflow()
        final_state = graph.invoke(initial_state)

        # Update database with results
        analysis.repo_name = final_state.get("repo_name", repo_url.split("/")[-1].replace(".git", ""))
        analysis.commit_hash = final_state.get("commit_hash", "")
        analysis.tree_structure = final_state.get("tree_structure")
        analysis.tech_stack = final_state.get("tech_stack")
        analysis.architecture = final_state.get("architecture")
        analysis.security = final_state.get("security")
        analysis.code_quality = final_state.get("code_quality")
        analysis.documentation = final_state.get("documentation")
        analysis.interview_questions = final_state.get("interview_questions")
        analysis.status = "completed"
        analysis.completed_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"LangGraph analysis {analysis_id} completed successfully.")

    except Exception as e:
        logger.error(f"Error analyzing repository {repo_url}: {e}", exc_info=True)
        # Re-fetch analysis in case session has issues
        try:
            db.rollback()
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                analysis.completed_at = datetime.utcnow()
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to save error status to database: {db_err}")
    finally:
        db.close()


@router.post("/analyze-repository", response_model=AnalysisResponse)
def analyze_repository(
    request: AnalysisCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Creates a new analysis, clones the repository, and triggers the analysis pipeline in the background.
    """
    # Create empty database record
    analysis = Analysis(
        repo_url=request.repo_url,
        status="pending"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Use a lambda session factory to get fresh DB connections inside the background thread
    from app.database import SessionLocal
    background_tasks.add_task(
        run_analysis_pipeline_in_background,
        analysis.id,
        analysis.repo_url,
        SessionLocal
    )

    return analysis


@router.get("/analysis/{id}", response_model=AnalysisResponse)
def get_analysis(id: str, db: Session = Depends(get_db)):
    """
    Retrieves the status and generated reports for a specific analysis run.
    """
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.post("/generate-readme", response_model=ReadmeResponse)
def generate_readme(request: AnalysisTriggerRequest, db: Session = Depends(get_db)):
    """
    Fetches the generated README documentation for an analysis.
    """
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet")
        
    doc_payload = analysis.documentation or {}
    readme = doc_payload.get("readme", "# No README generated")
    return ReadmeResponse(readme=readme)


@router.post("/security-review", response_model=SecurityResponse)
def security_review(request: AnalysisTriggerRequest, db: Session = Depends(get_db)):
    """
    Fetches the static analysis security report.
    """
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet")
        
    security = analysis.security or {}
    return SecurityResponse(security=security)


@router.post("/generate-interview-questions", response_model=InterviewResponse)
def generate_interview_questions_api(request: AnalysisTriggerRequest, db: Session = Depends(get_db)):
    """
    Fetches the generated interview prep questions.
    """
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not completed yet")
        
    questions = analysis.interview_questions or {}
    return InterviewResponse(questions=questions)


@router.post("/analysis/{id}/chat", response_model=ChatResponse)
def chat_with_codebase(id: str, request: ChatRequest, db: Session = Depends(get_db)):
    """
    Interact with the cloned codebase index using context-augmented RAG questions.
    """
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # 1. Fetch chat history and compile list of messages for RAG context
    # Let's compile list of messages for RAG context
    history = []
    for msg in db.query(ChatMessage).filter(ChatMessage.analysis_id == id).order_by(ChatMessage.created_at.asc()).all():
        history.append({"role": msg.sender, "content": msg.message})
        
    # 2. Query RAG engine
    rag_result = query_repository_rag(id, request.message, history)
    
    # 3. Store conversation in database
    user_msg = ChatMessage(
        analysis_id=id,
        sender="user",
        message=request.message
    )
    assistant_msg = ChatMessage(
        analysis_id=id,
        sender="assistant",
        message=rag_result["reply"],
        sources=rag_result["sources"]
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    
    return ChatResponse(
        reply=rag_result["reply"],
        sources=rag_result["sources"]
    )


@router.get("/analysis/{id}/chat/history", response_model=List[ChatHistoryMessage])
def get_chat_history(id: str, db: Session = Depends(get_db)):
    """
    Retrieves the complete message history for an analysis chatbot session.
    """
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    messages = db.query(ChatMessage).filter(ChatMessage.analysis_id == id).order_by(ChatMessage.created_at.asc()).all()
    return messages
