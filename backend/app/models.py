import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url = Column(String, nullable=False)
    repo_name = Column(String, nullable=True)
    commit_hash = Column(String, nullable=True)
    status = Column(String, default="pending")
    error_message = Column(Text, nullable=True)
    tree_structure = Column(JSON, nullable=True)
    tech_stack = Column(JSON, nullable=True)
    architecture = Column(JSON, nullable=True)
    security = Column(JSON, nullable=True)
    code_quality = Column(JSON, nullable=True)
    documentation = Column(JSON, nullable=True)
    interview_questions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    chat_messages = relationship("ChatMessage", back_populates="analysis", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="chat_messages")
