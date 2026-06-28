import sys
import os
import time
import json

# Ensure backend path is in Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.git_service import list_all_files, generate_tree_structure
from app.agents.tech_stack import detect_tech_stack
from app.agents.architecture import analyze_architecture
from app.agents.security import review_security
from app.agents.code_quality import analyze_code_quality
from app.agents.documentation import generate_documentation
from app.agents.interview import generate_interview_questions
from app.agents.workflow import clone_node, rag_indexing_node

def test_pipeline():
    repo_url = "https://github.com/Brahme27/Complete-Neural-Network-Regression-With-Tensorflow2keras"
    analysis_id = "test_analysis_run"
    repo_path = "backend/temp_repos/c9ec6c99-6d44-4139-9307-c7c58d9cebaa" # use already cloned folder
    
    print("Gathering files and structure...")
    files_list = list_all_files(repo_path)
    tree_structure = generate_tree_structure(repo_path)
    print(f"Total files: {len(files_list)}")
    
    state = {
        "analysis_id": analysis_id,
        "repo_url": repo_url,
        "repo_path": repo_path,
        "files_list": files_list,
        "tree_structure": tree_structure,
        "tech_stack": {},
        "architecture": {},
        "security": {},
        "code_quality": {},
        "documentation": {},
        "interview_questions": {},
        "rag_indexed": False,
        "status": "pending",
        "error_message": ""
    }
    
    # Run tech_stack
    print("\n--- Running tech_stack node ---")
    t0 = time.time()
    res = detect_tech_stack(state)
    print(f"tech_stack done in {time.time()-t0:.2f}s")
    print(json.dumps(res, indent=2))
    
    # Run architecture
    print("\n--- Running architecture node ---")
    t0 = time.time()
    res_arch = analyze_architecture(state)
    print(f"architecture done in {time.time()-t0:.2f}s")
    print(json.dumps(res_arch, indent=2))
    
    # Run security
    print("\n--- Running security node ---")
    t0 = time.time()
    res_sec = review_security(state)
    print(f"security done in {time.time()-t0:.2f}s")
    print(f"Vulnerabilities found: {len(res_sec['security']['vulnerabilities'])}")
    
    # Run code_quality
    print("\n--- Running code_quality node ---")
    t0 = time.time()
    res_cq = analyze_code_quality(state)
    print(f"code_quality done in {time.time()-t0:.2f}s")
    print(json.dumps(res_cq['code_quality'].get('code_quality_score'), indent=2))
    
    # Update state with tech_stack and architecture for documentation and interview nodes
    state["tech_stack"] = res["tech_stack"]
    state["architecture"] = res_arch["architecture"]
    
    # Run documentation
    print("\n--- Running documentation node ---")
    t0 = time.time()
    res_doc = generate_documentation(state)
    print(f"documentation done in {time.time()-t0:.2f}s")
    
    # Run interview
    print("\n--- Running interview node ---")
    t0 = time.time()
    res_int = generate_interview_questions(state)
    print(f"interview done in {time.time()-t0:.2f}s")
    
    # Run rag_indexing
    print("\n--- Running rag_indexing node ---")
    t0 = time.time()
    res_rag = rag_indexing_node(state)
    print(f"rag_indexing done in {time.time()-t0:.2f}s")
    print(res_rag)

if __name__ == "__main__":
    test_pipeline()
