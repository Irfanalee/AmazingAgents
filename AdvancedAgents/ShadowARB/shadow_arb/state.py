"""
State management for the Shadow ARB workflow.
Defines the shared state structure used across all agent nodes.
"""

from typing import TypedDict, List


class AgentState(TypedDict):
    """
    The shared state object passed between workflow nodes.
    
    Attributes:
        pr_diff: Raw code changes from the GitHub Pull Request
        security_findings: List of security issues identified by the security agent
        scale_findings: List of scalability issues identified by the scale agent
        clean_code_findings: List of code quality issues identified by the clean code agent
        final_verdict: Synthesized markdown review posted to GitHub
    """
    pr_diff: str
    security_findings: List[str]
    scale_findings: List[str]
    clean_code_findings: List[str]
    final_verdict: str
