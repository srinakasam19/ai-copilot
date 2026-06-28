import json
from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm import query_llm_json

def analyze_architecture(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes the structure and design patterns of the codebase.
    Suggests scalability improvements.
    """
    tree = state["tree_structure"]
    files_list = state["files_list"]
    
    # Generate a summarized list of top directories and files for context
    top_level_items = []
    for f in files_list:
        parts = f.split(chr(47)) # slash /
        if len(parts) <= 3: # include files up to 3 levels deep for structural context
            top_level_items.append(f)
            
    top_level_str = "\n".join(top_level_items[:100]) # Limit to 100 files for structure
    
    prompt = f"""
    Analyze the project layout and directory tree to understand its architecture.
    
    Top-level Directories and Files:
    {top_level_str}
    
    Provide the output in JSON format with the following keys:
    - architecture_pattern: Name of primary architecture pattern (e.g., Layered, MVC, Clean Architecture, Microservices)
    - design_patterns: list of detected design patterns (e.g., Repository, Singleton, Factory, Dependency Injection)
    - folder_organization: rating ("Good", "Fair", "Needs Improvement") and explanation of how folders are organized
    - summary: detailed description of how modules interact and how the app is structured
    - scalability_suggestions: list of specific actionable suggestions to make the application more scalable (e.g., caching, message queues, db indexing)
    
    Return ONLY valid JSON. Do not include markdown codeblocks or extra text.
    """
    
    system_prompt = "You are a Principal Software Architect who specializes in reverse-engineering project architectures from code structures."
    arch_report = query_llm_json(prompt, system_prompt=system_prompt)
    
    if not arch_report:
        arch_report = {
            "architecture_pattern": "Undetected Monolith",
            "design_patterns": [],
            "folder_organization": {"rating": "Fair", "explanation": "Unable to verify organization structure."},
            "summary": "Architecture analysis could not be completed.",
            "scalability_suggestions": ["Perform standard code auditing and modular scaling."]
        }
        
    return {"architecture": arch_report}
