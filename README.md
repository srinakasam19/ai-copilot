# AI Engineering Copilot

A production-ready engineering copilot platform that clones public repositories, generates files tree maps, automatically detects technology stacks, analyzes structural patterns, maps security flaws via Bandit/Semgrep, calculates complexity scores, and embeds files into FAISS using BAAI/bge-small-en-v1.5 embeddings to allow RAG-based context-rich developer queries.

---

## Key Features

1. **Repository Cloning**: clones codebases and represents directories recursively.
2. **Tech Stack Agent**: identifies languages, frameworks, configurations, and databases.
3. **Architecture Mapping**: reverse engineers MVC/Clean layouts, design patterns, and scalability enhancements.
4. **Security Auditing**: runs `Bandit`, `Semgrep`, and custom fallback AST scanners to find SQL injection vulnerabilities and hardcoded tokens.
5. **Code Complexity Agent**: identifies bloated functions, line counts, and duplicate lines.
6. **Master Documentation**: writes READMEs, developer onboarding guide, API logs, and architecture reports.
7. **Interview Bank Creator**: creates difficulty-graded interviews with questions and answers.
8. **RAG Q&A Chatbot**: performs similarity keyword and vector queries on FAISS indices using `BAAI/bge-small-en-v1.5` embeddings.

---

## Tech Stack

* **Backend**: FastAPI, SQLAlchemy, LangGraph, GitPython, FAISS, Sentence-Transformers.
* **Frontend**: React (Vite), Tailwind CSS, Lucide Icons.
* **Models**: Qwen2.5-Coder (via Ollama).
* **Database**: PostgreSQL 15.

---

## Quick Start (Docker Orchestration)

### Prerequisites
- Install **Docker** and **Docker Compose**.

### Step 1: Clone and Boot the Stack
Navigate to the root directory and run:
```bash
docker-compose up --build -d
```
This builds and spawns:
* `copilot_db`: PostgreSQL container (port 5432).
* `copilot_ollama`: Ollama server (port 11434).
* `copilot_backend`: FastAPI app (port 8000).
* `copilot_frontend`: Nginx web server serving React dashboard (port 80).

### Step 2: Download Ollama LLM
Before starting the analysis, ensure the Ollama model is downloaded:
```bash
docker exec -it copilot_ollama ollama pull qwen2.5-coder:3b
```

### Step 3: Access the Application
Open your browser and navigate to:
* **Dashboard**: [http://localhost](http://localhost)
* **FastAPI Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Manual Local Setup (Without Docker)

### Backend
1. Python 3.10 is required. Create and activate a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment in `.env` (refer to `.env.template`):
   ```bash
   cp .env.template .env
   ```
4. Run FastAPI app:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend
1. Ensure Node.js 18+ is installed.
2. Install node dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Start local development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:5173](http://localhost:5173) in your browser.
