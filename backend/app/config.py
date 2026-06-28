import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./copilot.db"
    )
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    WORKSPACE_DIR: str = os.getenv("WORKSPACE_DIR", "./temp_repos")
    FAISS_DIR: str = os.getenv("FAISS_DIR", "./faiss_indices")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.WORKSPACE_DIR, exist_ok=True)
os.makedirs(settings.FAISS_DIR, exist_ok=True)
