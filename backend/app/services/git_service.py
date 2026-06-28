import os
import git
from typing import Dict, Any, List

def clone_repository(repo_url: str, local_path: str) -> Dict[str, Any]:
    """
    Clones a public GitHub repository.
    Returns metadata about the cloned repository.
    """
    if os.path.exists(local_path) and os.listdir(local_path):
        # Already cloned (or directory exists)
        repo = git.Repo(local_path)
    else:
        # Clone repo with a shallow clone (depth=1) for speed and resource efficiency
        repo = git.Repo.clone_from(repo_url, local_path, depth=1)
        
    commit = repo.head.commit
    metadata = {
        "repo_name": repo_url.split("/")[-1].replace(".git", ""),
        "commit_hash": commit.hexsha,
        "commit_message": commit.message,
        "author": commit.author.name,
        "authored_datetime": commit.authored_datetime.isoformat(),
        "default_branch": repo.active_branch.name if not repo.head.is_detached else "detached"
    }
    return metadata

def generate_tree_structure(local_path: str, current_path: str = None, max_depth: int = 4, depth: int = 0) -> Dict[str, Any]:
    """
    Generates a nested directory tree structure for the frontend UI.
    Excludes standard build and config directories.
    """
    if current_path is None:
        current_path = local_path
        
    ignored_names = {
        ".git", "node_modules", "venv", "env", "__pycache__", 
        "dist", "build", ".next", ".nuxt", "target", "out",
        ".idea", ".vscode", "pnpm-lock.yaml", "package-lock.json",
        "yarn.lock", "poetry.lock", "Gemfile.lock",
        "assets", "static", "images", "media", "public"
    }
    
    basename = os.path.basename(current_path)
    if not basename and current_path == local_path:
        basename = "root"
        
    result: Dict[str, Any] = {
        "name": basename,
        "path": os.path.relpath(current_path, local_path),
        "type": "directory",
        "children": []
    }
    
    if depth > max_depth:
        return result
        
    try:
        items = os.listdir(current_path)
        for item in sorted(items):
            if item in ignored_names:
                continue
                
            full_path = os.path.join(current_path, item)
            if os.path.isdir(full_path):
                child_dir = generate_tree_structure(local_path, full_path, max_depth, depth + 1)
                result["children"].append(child_dir)
            else:
                result["children"].append({
                    "name": item,
                    "path": os.path.relpath(full_path, local_path),
                    "type": "file",
                    "size": os.path.getsize(full_path)
                })
    except Exception as e:
        # Permission denied or other error
        pass
        
    return result

def list_all_files(local_path: str) -> List[str]:
    """
    Lists all non-binary, non-ignored file paths relative to the local_path.
    """
    ignored_names = {
        ".git", "node_modules", "venv", "env", "__pycache__", 
        "dist", "build", ".next", ".nuxt", "target", "out",
        ".idea", ".vscode", "assets", "static", "images", "media", "public"
    }
    
    # Common binary file extensions
    binary_extensions = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", 
        ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so", 
        ".bin", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4",
        ".svg"
    }
    
    file_list = []
    for root, dirs, files in os.walk(local_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_names]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in binary_extensions or file in ignored_names:
                continue
            
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, local_path)
            file_list.append(rel_path)
            
    return file_list
