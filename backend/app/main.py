import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers.analysis import router as analysis_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Engineering Copilot API",
    description="Backend API for technology stack analysis, security audits, architecture mapping, and RAG chat.",
    version="1.0.0"
)

# Enable CORS for frontend interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include analysis routes
app.include_router(analysis_router)

@app.get("/")
def read_root():
    return {"status": "AI Engineering Copilot API is running"}
