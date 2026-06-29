# 🚀 AI Engineering Copilot

> **An AI-powered engineering assistant that analyzes Git repositories, detects technologies, reverse engineers software architecture, identifies security vulnerabilities, generates developer documentation, and enables intelligent repository Q&A using Retrieval-Augmented Generation (RAG).**

AI Engineering Copilot helps developers understand unfamiliar codebases in minutes instead of hours by combining **multi-agent analysis**, **static code analysis**, **vector search**, and **local Large Language Models** into a single platform.

---

## ✨ Key Features

### 📂 Repository Analysis
- Clone and analyze public Git repositories.
- Generate recursive file tree representations.
- Extract repository metadata and project structure.

### 🛠️ Tech Stack Detection
- Detect programming languages.
- Identify frameworks and libraries.
- Discover databases and configuration files.
- Analyze project dependencies.

### 🏛️ Architecture Analysis
- Reverse engineer repository architecture.
- Identify MVC, Layered, and Clean Architecture patterns.
- Detect design patterns and structural relationships.
- Generate architecture summaries.

### 🔒 Security Analysis
- Scan code using **Bandit** and **Semgrep**.
- Detect SQL Injection vulnerabilities.
- Identify hardcoded secrets and API keys.
- Perform fallback AST-based security analysis.

### 📊 Code Quality Analysis
- Detect large and complex functions.
- Measure code complexity.
- Identify duplicate code.
- Highlight maintainability issues.

### 📘 AI Documentation Generator
Automatically generates:

- README documentation
- Architecture reports
- API documentation
- Developer onboarding guides

### 🎯 AI Interview Generator
Generate repository-specific interview questions with difficulty levels and model answers.

### 🤖 AI Repository Chat
Build a semantic knowledge base using **FAISS** and **sentence-transformers/all-MiniLM-L6-v2** embeddings, enabling developers to ask natural language questions about the repository using Retrieval-Augmented Generation (RAG).

---

# 🏗️ System Architecture

> *(Insert your architecture diagram here)*

<p align="center">
<img src="docs/architecture.png" width="100%">
</p>

---

# ⚙️ Tech Stack

| Layer | Technologies |
|---------|-------------|
| **Backend** | FastAPI, SQLAlchemy, LangGraph |
| **Frontend** | React (Vite), Tailwind CSS, Lucide Icons |
| **LLM** | Qwen2.5-Coder (Ollama) |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |
| **Vector Database** | FAISS |
| **Database** | PostgreSQL 15 |
| **Repository Analysis** | GitPython |
| **Security** | Bandit, Semgrep |
| **Containerization** | Docker & Docker Compose |

---

# 🔄 Workflow

```text
Developer
      │
      ▼
React Dashboard
      │
      ▼
FastAPI Backend
      │
      ▼
Repository Cloning
      │
      ▼
LangGraph Multi-Agent Pipeline
      │
      ├── Tech Stack Detection
      ├── Architecture Analysis
      ├── Security Scanning
      ├── Complexity Analysis
      └── Documentation Generation
      │
      ▼
Source Code Chunking
      │
      ▼
Sentence Transformers
(all-MiniLM-L6-v2)
      │
      ▼
FAISS Vector Store
      │
      ▼
Semantic Retrieval
      │
      ▼
Qwen2.5-Coder (Ollama)
      │
      ▼
Repository-Aware AI Answers
```

---

# 🚀 Quick Start (Docker)

## Prerequisites

- Docker
- Docker Compose

## Start the Application

```bash
docker-compose up --build -d
```

The following services will start:

| Service | Port |
|----------|------|
| PostgreSQL | 5432 |
| Ollama | 11434 |
| FastAPI Backend | 8000 |
| React Dashboard | 80 |

---

## Download the Local LLM

```bash
docker exec -it copilot_ollama ollama pull qwen2.5-coder:3b
```

---

## Access the Application

| Component | URL |
|------------|-----|
| Dashboard | http://localhost |
| Swagger API | http://localhost:8000/docs |

---

# 💻 Local Development

## Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

cp .env.template .env

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Open:

```
http://localhost:5173
```

---

# 📌 Future Enhancements

- Repository Health Score
- GitHub Pull Request Review
- Multi-language Repository Support
- Hybrid Search (BM25 + Vector Search)
- AI Code Refactoring Suggestions
- Automatic Unit Test Generation
- CI/CD Integration
- Kubernetes Deployment

---

# 🤝 Contributing

Contributions, feature requests, and suggestions are welcome.

Feel free to fork the repository and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.
