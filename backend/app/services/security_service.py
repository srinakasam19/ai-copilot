import os
import re
import json
import subprocess
from typing import Dict, Any, List

def run_security_analysis(local_path: str) -> Dict[str, Any]:
    """
    Runs Bandit and Semgrep on the repository if available,
    and runs a custom regex-based fallback security scanner to guarantee findings.
    """
    vulnerabilities = []
    
    # 1. Run Bandit (Python security analysis)
    try:
        # Run bandit on python files
        res = subprocess.run(
            ["bandit", "-r", local_path, "-f", "json", "-q"],
            capture_output=True,
            text=True,
            shell=True
        )
        if res.returncode in [0, 1] and res.stdout:
            data = json.loads(res.stdout)
            for result in data.get("results", []):
                rel_file = os.path.relpath(result["filename"], local_path)
                vulnerabilities.append({
                    "file": rel_file,
                    "line": result.get("line_number", 1),
                    "severity": result.get("issue_severity", "MEDIUM"),
                    "type": result.get("test_name", "Bandit Finding"),
                    "message": result.get("issue_text", ""),
                    "code": result.get("code", "").strip(),
                    "tool": "Bandit"
                })
    except Exception as e:
        # Bandit failed or not installed, fallback logic will cover it
        pass

    # 2. Run Semgrep (General multi-language security analysis)
    try:
        res = subprocess.run(
            ["semgrep", "scan", "--config=auto", "--json", local_path],
            capture_output=True,
            text=True,
            shell=True
        )
        if res.returncode in [0, 1] and res.stdout:
            data = json.loads(res.stdout)
            for result in data.get("results", []):
                rel_file = os.path.relpath(result["path"], local_path)
                vulnerabilities.append({
                    "file": rel_file,
                    "line": result.get("start", {}).get("line", 1),
                    "severity": "HIGH" if result.get("extra", {}).get("severity") == "ERROR" else "MEDIUM",
                    "type": result.get("check_id", "Semgrep Finding"),
                    "message": result.get("extra", {}).get("message", ""),
                    "code": result.get("extra", {}).get("lines", "").strip(),
                    "tool": "Semgrep"
                })
    except Exception as e:
        # Semgrep failed or not installed, fallback logic will cover it
        pass

    # 3. Always run the Fallback Scanner to ensure we capture secrets and common mistakes
    fallback_findings = run_fallback_scanner(local_path)
    
    # Merge findings, avoiding duplicates based on (file, line, type)
    seen = set()
    for v in vulnerabilities:
        seen.add((v["file"], v["line"], v["type"]))
        
    for f in fallback_findings:
        if (f["file"], f["line"], f["type"]) not in seen:
            vulnerabilities.append(f)
            seen.add((f["file"], f["line"], f["type"]))

    # Sort vulnerabilities by severity (HIGH -> MEDIUM -> LOW)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    vulnerabilities.sort(key=lambda x: severity_order.get(x["severity"], 4))

    return {
        "vulnerabilities": vulnerabilities,
        "summary": {
            "critical": sum(1 for v in vulnerabilities if v["severity"] == "CRITICAL"),
            "high": sum(1 for v in vulnerabilities if v["severity"] == "HIGH"),
            "medium": sum(1 for v in vulnerabilities if v["severity"] == "MEDIUM"),
            "low": sum(1 for v in vulnerabilities if v["severity"] == "LOW"),
            "total": len(vulnerabilities)
        }
    }

FALLBACK_SCAN_PATTERNS = {
    "AWS API Key/Secret": (
        re.compile(r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}', re.IGNORECASE),
        "HIGH",
        "Potential hardcoded AWS Access Key detected."
    ),
    "Generic Secret/Password Assignment": (
        re.compile(r'(?:password|passwd|secret|api_key|apikey|token|private_key)\s*=\s*[\'"]([a-zA-Z0-9_\-+=/]{16,})[\'"]', re.IGNORECASE),
        "HIGH",
        "Potential hardcoded secret or API token assigned to variable."
    ),
    "Slack Webhook URL": (
        re.compile(r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}'),
        "HIGH",
        "Slack Webhook URL detected directly in source code."
    ),
    "SQL Injection Risk (Python)": (
        re.compile(r'\.execute\(\s*f[\'"].*\{\w+\}.*[\'"]\s*\)|\.execute\(\s*[\'"].*[\'"]\s*\+\s*\w+\s*\)'),
        "HIGH",
        "Direct string concatenation/interpolation in query execution. Risk of SQL Injection."
    ),
    "SQL Injection Risk (JS/TS)": (
        re.compile(r'\.query\(\s*`.*\$\{.*\}.*`\s*\)|\.query\(\s*[\'"].*[\'"]\s*\+\s*\w+\s*\)'),
        "HIGH",
        "Dynamic SQL query construction detected. Risk of SQL Injection."
    ),
    "Insecure Eval Usage": (
        re.compile(r'\beval\([^)]+\)'),
        "MEDIUM",
        "Use of eval() function. This executes string content as code and is highly insecure."
    ),
    "Unsafe Shell Execution": (
        re.compile(r'subprocess\.(Popen|run|call)\(.*shell\s*=\s*True.*\)|\bos\.system\('),
        "HIGH",
        "Running sub-processes with shell=True or using os.system. High risk of shell injection if parameters are untrusted."
    ),
    "Insecure Deserialization": (
        re.compile(r'pickle\.loads\(|yaml\.load\(\s*[^,]+,\s*Loader\s*=\s*(?!SafeLoader)'),
        "HIGH",
        "Insecure deserialization using pickle or unsafe yaml loaders. Can lead to Remote Code Execution."
    )
}

def run_fallback_scanner(local_path: str) -> List[Dict[str, Any]]:
    """
    Regex-based code scanner for hardcoded secrets, SQL injection vectors,
    and unsafe operations.
    """
    findings = []
    ignored_dirs = {".git", "node_modules", "venv", "env", "__pycache__", "dist", "build"}
    scannable_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".cs", ".php", ".rb"}

    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() not in scannable_exts:
                continue
                
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, local_path)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    
                for line_idx, line in enumerate(lines, 1):
                    for label, (pattern, severity, message) in FALLBACK_SCAN_PATTERNS.items():
                        match = pattern.search(line)
                        if match:
                            findings.append({
                                "file": rel_file_path,
                                "line": line_idx,
                                "severity": severity,
                                "type": label,
                                "message": message,
                                "code": line.strip(),
                                "tool": "FallbackScanner"
                            })
            except Exception:
                # Silently skip unreadable files
                pass
                
    return findings
