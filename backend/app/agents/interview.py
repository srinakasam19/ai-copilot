from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm import query_llm_json

def generate_interview_questions(state: AgentState) -> Dict[str, Any]:
    """
    Generates repository-specific interview questions graded by difficulty,
    along with system design discussion points.
    """
    tech_stack = state.get("tech_stack", {})
    architecture = state.get("architecture", {})
    
    prompt = f"""
    Create a technical developer interview question bank tailored to this codebase's tech stack and architecture.
    
    Tech Stack Detected:
    {tech_stack.get('summary', 'Unknown')}
    
    Architecture Detected:
    {architecture.get('summary', 'Unknown')}
    
    Provide the output in JSON format with the following keys:
    - beginner: list of dicts with keys "question", "answer", and "topic" (e.g. CLI usage, route registration)
    - intermediate: list of dicts with keys "question", "answer", and "topic" (e.g. middleware setup, DB schema design, error boundaries)
    - advanced: list of dicts with keys "question", "answer", and "topic" (e.g. connection pool tuning, caching consistency, micro-optimizations)
    - system_design: list of dicts with keys "topic", "discussion_question", and "evaluation_criteria" (evaluating scalability, performance under load, and high availability)
    
    Guidelines for the "answer" field:
    1. Answers must be highly detailed, professional, and comprehensive.
    2. Where appropriate, include clear and optimized code snippets or configuration examples in standard Markdown format (e.g., using ```python or ```javascript).
    3. Detail best practices, common bugs/pitfalls, and security or performance implications of the proposed solution.
    4. Format the answers using readable Markdown (with bullet points, bold/italic highlights, and sub-headers) so they render beautifully in the UI.
    
    Return ONLY valid JSON. Do not include markdown codeblocks or extra text.
    """
    
    system_prompt = "You are a Technical Interviewer and Engineering Manager creating custom hiring evaluation sheets."
    questions = query_llm_json(prompt, system_prompt=system_prompt)
    
    if not questions:
        questions = {
            "beginner": [{"question": "What language is this repository written in?", "answer": "Look at files extension.", "topic": "Tech Stack"}],
            "intermediate": [],
            "advanced": [],
            "system_design": []
        }
        
    return {"interview_questions": questions}
