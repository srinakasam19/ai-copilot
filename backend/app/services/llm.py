import re
import json
import logging
import requests
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from app.config import settings

logger = logging.getLogger(__name__)

def query_llm(prompt: str, json_mode: bool = False, system_prompt: Optional[str] = None) -> str:
    """
    Queries Ollama.
    Tries LangChain's ChatOllama first, and falls back to raw HTTP requests to ensure robustness.
    """
    # 1. Attempt using LangChain
    try:
        format_val = "json" if json_mode else None
        # Initialize ChatOllama
        llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            format=format_val,
            temperature=0.2
        )
        
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("user", prompt))
        
        response = llm.invoke(messages)
        return response.content
    except Exception as lc_err:
        logger.warning(f"LangChain ChatOllama failed, trying direct HTTP request. Error: {lc_err}")
        
    # 2. Fallback to direct HTTP request to Ollama API
    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        if json_mode:
            payload["format"] = "json"
            
        res = requests.post(url, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data.get("message", {}).get("content", "")
    except Exception as http_err:
        logger.error(f"Ollama direct HTTP query failed: {http_err}")
        # Return fallback mock JSON if json_mode, or text
        if json_mode:
            return "{}"
        return "LLM service unavailable. Detailed report could not be generated."

def query_llm_json(prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper to query LLM and safely parse the output into a dictionary.
    """
    raw_response = query_llm(prompt, json_mode=True, system_prompt=system_prompt)
    try:
        # Strip codeblock wrappers if any exist
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Failed to parse JSON response: '{raw_response}'. Error: {e}")
        # Try finding json object inside text
        try:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return {}
