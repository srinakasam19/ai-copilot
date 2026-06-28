from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm import query_llm_json

def generate_documentation(state: AgentState) -> Dict[str, Any]:
    """
    Compiles documentation for the repository: README, Architecture,
    API Reference, and Developer Onboarding guides.
    """
    tech_stack = state.get("tech_stack", {})
    architecture = state.get("architecture", {})
    tree = state.get("tree_structure", {})
    
    # We query the LLM to write these documents in markdown format
    # Because of context window size, we combine inputs in a unified prompt and ask for a JSON payload containing all four guides.
    prompt = f"""
    Based on the analyzed repository, generate detailed development documentation.
    
    Tech Stack Summary:
    {tech_stack.get('summary', 'Unknown')}
    
    Primary Architecture Pattern:
    {architecture.get('architecture_pattern', 'Monolithic')}
    
    Folder Organization Rating:
    {architecture.get('folder_organization', {}).get('explanation', 'Standard layout')}
    
    Provide the output in JSON format with the following keys:
    - readme: A comprehensive, production-ready master README.md containing project title, description, features, tech stack, directory structure map, local installation commands, and run commands.
    - architecture: A detailed Architecture Guide explaining the components, data flow, design patterns, and scaling strategies used.
    - api_reference: API documentation (endpoints for web servers, or class/library method tables for packages).
    - onboarding: Step-by-step setup guides, environment variables, local debugging, and coding guidelines for new developers.
    
    Each value MUST be a string formatted in valid GitHub Markdown.
    Return ONLY valid JSON. Do not include markdown codeblocks or extra text.
    """
    
    system_prompt = "You are a Technical Writer and Developer Advocate generating professional software documentation."
    docs = query_llm_json(prompt, system_prompt=system_prompt)
    
    if not docs:
        docs = {
            "readme": "# Project README\nSetup details are loading.",
            "architecture": "# Architecture Guide\nComponent overview is pending.",
            "api_reference": "# API Documentation\nNo endpoints detected.",
            "onboarding": "# Onboarding Guide\nLocal dependencies install guide."
        }
        
    return {"documentation": docs}
