import os
import tempfile
import pytest
from app.services.security_service import run_fallback_scanner
from app.services.git_service import list_all_files

def test_fallback_security_scanner():
    """
    Tests that the fallback security scanner correctly identifies
    hardcoded secrets, SQL injections, and eval statements.
    """
    # Create a temporary directory and dummy file with vulnerabilities
    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_file = os.path.join(tmpdir, "app.py")
        with open(dummy_file, "w", encoding="utf-8") as f:
            f.write("""
# Vulnerable App
AWS_KEY = "AKIA1234567890123456"
db_password = 'my_super_secret_password_1234'

def get_user(user_id):
    db.execute(f"SELECT * FROM users WHERE id = {user_id}")
    
    # Insecure eval
    eval("x + 1")
    
    # Unsafe process call
    import subprocess
    subprocess.run("echo test", shell=True)
            """)
            
        findings = run_fallback_scanner(tmpdir)
        
        # Verify findings
        finding_types = [f["type"] for f in findings]
        assert "AWS API Key/Secret" in finding_types
        assert "Generic Secret/Password Assignment" in finding_types
        assert "SQL Injection Risk (Python)" in finding_types
        assert "Insecure Eval Usage" in finding_types
        assert "Unsafe Shell Execution" in finding_types
        assert len(findings) >= 5

def test_list_all_files():
    """
    Verifies that the git file lister lists files correctly while excluding binaries.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create text file
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("print('hello')")
            
        # Create ignored folder/files
        os.makedirs(os.path.join(tmpdir, "node_modules"))
        with open(os.path.join(tmpdir, "node_modules", "package.json"), "w") as f:
            f.write("{}")
            
        # Create binary file
        with open(os.path.join(tmpdir, "logo.png"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00")
            
        files = list_all_files(tmpdir)
        
        # main.py should be included, png and node_modules ignored
        assert "main.py" in files
        assert "logo.png" not in files
        assert "node_modules/package.json" not in files
        assert len(files) == 1
