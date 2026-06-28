import os
import re
from typing import Dict, Any, List

from app.agents.state import AgentState
from app.services.llm import query_llm_json

def analyze_code_quality(state: AgentState) -> Dict[str, Any]:
    """
    Scans files to locate large files, finds functions spanning many lines,
    identifies basic code duplication, and requests quality refactoring suggestions from Ollama.
    """
    repo_path = state["repo_path"]
    files_list = state["files_list"]
    
    # 1. Analyze file sizes
    file_sizes = []
    scannable_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".cs", ".cpp"}
    
    for f in files_list:
        _, ext = os.path.splitext(f)
        if ext.lower() in scannable_exts:
            full_path = os.path.join(repo_path, f)
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handler:
                        lines = file_handler.readlines()
                    file_sizes.append({
                        "file": f,
                        "line_count": len(lines),
                        "size_bytes": os.path.getsize(full_path)
                    })
                except Exception:
                    pass
                    
    # Sort files by line count descending
    file_sizes.sort(key=lambda x: x["line_count"], reverse=True)
    largest_files = file_sizes[:5]
    
    # 2. Heuristic for large functions and complexity
    # We will look for "def " / "function " and count lines until indentation decreases or a new function starts.
    large_functions = []
    
    # Let's check python files first as a representative sample
    py_files = [f["file"] for f in file_sizes if f["file"].endswith(".py")]
    for pf in py_files[:3]:  # Scan top 3 largest python files for large functions
        full_path = os.path.join(repo_path, pf)
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handler:
                lines = file_handler.readlines()
            
            current_func = None
            func_start_line = 0
            indent_level = 0
            
            for idx, line in enumerate(lines, 1):
                # Search for function declaration
                match = re.match(r"^(\s*)(?:def|async def)\s+(\w+)\(", line)
                if match:
                    if current_func:
                        # Close previous function
                        duration = idx - func_start_line
                        if duration > 60:  # Large function threshold: 60 lines
                            large_functions.append({
                                "file": pf,
                                "name": current_func,
                                "line_count": duration,
                                "start_line": func_start_line
                            })
                    indent_level = len(match.group(1))
                    current_func = match.group(2)
                    func_start_line = idx
                elif current_func and line.strip():
                    # Check if indentation level is back to start or outer level (closing function)
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level and not line.startswith(("#", ")", "]", "}")):
                        duration = idx - func_start_line
                        if duration > 60:
                            large_functions.append({
                                "file": pf,
                                "name": current_func,
                                "line_count": duration,
                                "start_line": func_start_line
                            })
                        current_func = None
        except Exception:
            pass

    # 3. Simple duplication detector
    # Find identical lines of size > 6 lines across files
    line_blocks = {}
    duplicates = []
    
    # Check a subset of files to keep execution quick
    for f_info in file_sizes[:10]:
        f = f_info["file"]
        full_path = os.path.join(repo_path, f)
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handler:
                lines = [l.strip() for l in file_handler.readlines() if l.strip()]
            
            # Check windows of 6 lines
            window_size = 6
            for i in range(len(lines) - window_size + 1):
                block = "\n".join(lines[i:i+window_size])
                # Skip trivial structures like imports or headers
                if len(block) < 60 or "import " in block or "from " in block:
                    continue
                    
                if block in line_blocks:
                    other_file, other_line = line_blocks[block]
                    if other_file != f:
                        duplicates.append({
                            "block": block[:150] + "...",
                            "file_a": other_file,
                            "line_a": other_line,
                            "file_b": f,
                            "line_b": i + 1
                        })
                else:
                    line_blocks[block] = (f, i + 1)
        except Exception:
            pass

    # Limit duplicates count
    duplicates = duplicates[:5]
    
    # 4. Generate LLM suggestions
    prompt = f"""
    Analyze the code quality parameters of the repository.
    
    Largest Files (by line count):
    {json_dumps(largest_files)}
    
    Large Functions Detected:
    {json_dumps(large_functions[:5])}
    
    Duplicate Blocks Detected:
    {json_dumps(duplicates)}
    
    Provide the output in JSON format with the following keys:
    - code_quality_score: an overall score between 0 and 100
    - maintainability_issues: list of dicts with keys "file", "issue_type" (e.g. Bloated Function, Duplication, High Complexity), and "description"
    - refactoring_suggestions: list of dicts with keys "description", "benefit", and "priority" ("HIGH", "MEDIUM", "LOW")
    
    Return ONLY valid JSON. Do not include markdown codeblocks or extra text.
    """
    
    system_prompt = "You are a Senior Quality Assurance Architect reviewing software complexity."
    quality_report = query_llm_json(prompt, system_prompt=system_prompt)
    
    if not quality_report:
        quality_report = {
            "code_quality_score": 70,
            "maintainability_issues": [],
            "refactoring_suggestions": [
                {"description": "Break down large functions into separate helpers.", "benefit": "Improves readability.", "priority": "HIGH"}
            ]
        }
        
    # Append the raw analytics
    quality_report["largest_files"] = largest_files
    quality_report["large_functions"] = large_functions
    quality_report["duplicates"] = duplicates
    
    return {"code_quality": quality_report}

def json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, indent=2)
