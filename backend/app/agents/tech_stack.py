import os
from typing import Dict, Any, List
from app.agents.state import AgentState
from app.services.llm import query_llm_json

def detect_tech_stack(state: AgentState) -> Dict[str, Any]:
    """
    Detects the repository technology stack including languages, frameworks,
    databases, and deployment technologies.
    """
    repo_path = state["repo_path"]
    files_list = state["files_list"]
    
    # 1. Gather configuration file contents for context
    manifest_files = ["package.json", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "docker-compose.yml", "Dockerfile"]
    manifest_context = []
    
    for f in manifest_files:
        matching_files = [path for path in files_list if path.endswith(f)]
        for path in matching_files[:2]:  # Limit to first 2 to keep context size manageable
            full_path = os.path.join(repo_path, path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handler:
                        content = file_handler.read(1500) # Read first 1500 chars
                        manifest_context.append(f"--- File: {path} ---\n{content}\n")
                except Exception:
                    pass

    context_str = "\n".join(manifest_context)
    file_extensions = list(set(os.path.splitext(f)[1] for f in files_list if os.path.splitext(f)[1]))
    
    prompt = f"""
    Analyze the project files list and configuration/manifest files to detect the tech stack.
    
    File Extensions in Repo: {file_extensions}
    Manifest Files Samples:
    {context_str}
    
    Provide the output in JSON format with the following keys:
    - languages: list of dicts with keys "name", "confidence" (0-100), and "primary" (boolean)
    - frameworks: list of dicts with keys "name", "type" (frontend, backend, utility), and "confidence" (0-100)
    - databases: list of dicts with keys "name", "type" (SQL, NoSQL, Cache), and "confidence" (0-100)
    - deployment: list of dicts with keys "name" (Docker, Kubernetes, AWS, etc.), and "confidence" (0-100)
    - summary: a short paragraph describing the stack and core architectural choices.
    
    Return ONLY valid JSON. Do not include markdown codeblocks or extra text.
    """
    
    system_prompt = "You are an expert AI software architect that analyzes codebase structures and outputs strictly formatted JSON."
    tech_report = query_llm_json(prompt, system_prompt=system_prompt)
    
    # Fallback default structure if JSON query failed
    if not tech_report:
        tech_report = {
            "languages": [{"name": "Unknown", "confidence": 50, "primary": True}],
            "frameworks": [],
            "databases": [],
            "deployment": [],
            "summary": "Auto-detection failed or LLM timed out."
        }
        
    return {"tech_stack": tech_report}
