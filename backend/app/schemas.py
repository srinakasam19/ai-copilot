from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

class AnalysisCreate(BaseModel):
    repo_url: str

class AnalysisResponse(BaseModel):
    id: str
    repo_url: str
    repo_name: Optional[str] = None
    commit_hash: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    tree_structure: Optional[Dict[str, Any]] = None
    tech_stack: Optional[Dict[str, Any]] = None
    architecture: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    code_quality: Optional[Dict[str, Any]] = None
    documentation: Optional[Dict[str, Any]] = None
    interview_questions: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class SourceInfo(BaseModel):
    file: str
    snippet: str

class ChatResponse(BaseModel):
    reply: str
    sources: List[SourceInfo]

class ChatHistoryMessage(BaseModel):
    id: str
    analysis_id: str
    sender: str
    message: str
    sources: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReadmeResponse(BaseModel):
    readme: str

class SecurityResponse(BaseModel):
    security: Dict[str, Any]

class InterviewResponse(BaseModel):
    questions: Dict[str, Any]

class AnalysisTriggerRequest(BaseModel):
    analysis_id: str
