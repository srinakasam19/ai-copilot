from typing import Dict, Any
from app.agents.state import AgentState
from app.services.security_service import run_security_analysis
from app.services.llm import query_llm

def review_security(state: AgentState) -> Dict[str, Any]:
    """
    Executes security scanners on the cloned repository, compiles findings,
    and queries the LLM for a descriptive security report.
    """
    repo_path = state["repo_path"]
    
    # 1. Run static scanners and fallbacks
    scan_results = run_security_analysis(repo_path)
    vulnerabilities = scan_results["vulnerabilities"]
    summary_stats = scan_results["summary"]
    
    # 2. Summarize top findings for LLM review (limit size of context)
    top_findings = []
    for idx, v in enumerate(vulnerabilities[:15]): # top 15 findings
        top_findings.append(
            f"Finding #{idx+1}: {v['type']} ({v['severity']})\n"
            f"File: {v['file']}:{v['line']}\n"
            f"Code Context: {v['code']}\n"
            f"Issue: {v['message']}\n"
        )
        
    findings_str = "\n".join(top_findings) if top_findings else "No critical/high/medium security findings detected by static analyzers."
    
    prompt = f"""
    Review the security audit results of the repository.
    
    Summary of findings:
    Total Vulnerabilities: {summary_stats['total']}
    Critical: {summary_stats['critical']}
    High: {summary_stats['high']}
    Medium: {summary_stats['medium']}
    Low: {summary_stats['low']}
    
    Sample Details:
    {findings_str}
    
    Write a comprehensive Security Report in Markdown format. The report should contain:
    1. Executive Summary of the security posture.
    2. Vulnerability analysis: discuss why the flagged vulnerabilities (like SQL injections, hardcoded secrets, or eval calls) are risky.
    3. Remediation roadmap: step-by-step actions the development team must take to secure this codebase.
    
    Keep the report professional and concise.
    """
    
    system_prompt = "You are a Senior Application Security Engineer (AppSec) writing an audit report."
    markdown_summary = query_llm(prompt, system_prompt=system_prompt)
    
    # Save both raw vulnerability logs and the LLM summarized report
    security_report = {
        "vulnerabilities": vulnerabilities,
        "summary_stats": summary_stats,
        "report_markdown": markdown_summary
    }
    
    return {"security": security_report}
