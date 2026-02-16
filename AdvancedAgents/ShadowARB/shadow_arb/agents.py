"""
Specialized AI agents for code review.
Each agent analyzes the PR diff from a specific architectural perspective.
"""

from typing import List
import json
from litellm import completion
from pydantic import BaseModel, Field

from .state import AgentState
from .config import Config
from .prompts import (
    SECURITY_AGENT_PROMPT,
    SCALE_AGENT_PROMPT,
    CLEAN_CODE_AGENT_PROMPT,
    CHAIRPERSON_PROMPT,
)


class FindingsResponse(BaseModel):
    """Structured response model for agent findings."""
    findings: List[str] = Field(
        default_factory=list,
        description="List of specific issues found during review"
    )


def _call_llm_with_structured_output(
    system_prompt: str,
    user_message: str,
    response_model: type[BaseModel] = FindingsResponse
) -> BaseModel:
    """
    Call LLM with structured output using LiteLLM.
    
    Args:
        system_prompt: The system prompt defining agent expertise
        user_message: The user message (typically the PR diff)
        response_model: Pydantic model for structured response
        
    Returns:
        Parsed Pydantic model instance
    """
    response = completion(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    
    # Extract JSON from response
    content = response.choices[0].message.content
    parsed_json = json.loads(content)
    
    # Handle cases where the model returns the findings directly or wrapped
    if isinstance(parsed_json, list):
        return response_model(findings=parsed_json)
    elif "findings" in parsed_json:
        return response_model(**parsed_json)
    else:
        # Try to extract any list from the response
        for value in parsed_json.values():
            if isinstance(value, list):
                return response_model(findings=value)
        return response_model(findings=[])


def security_agent(state: AgentState) -> AgentState:
    """
    Security Agent: Reviews code for security vulnerabilities.
    
    Args:
        state: Current workflow state containing pr_diff
        
    Returns:
        Updated state with security_findings populated
    """
    pr_diff = state.get("pr_diff", "")
    
    if not pr_diff:
        state["security_findings"] = []
        return state
    
    user_message = f"Review the following code changes for security issues:\n\n{pr_diff}"
    
    response = _call_llm_with_structured_output(
        system_prompt=SECURITY_AGENT_PROMPT,
        user_message=user_message
    )
    
    state["security_findings"] = response.findings
    return state


def scale_agent(state: AgentState) -> AgentState:
    """
    Scale Agent: Reviews code for performance and scalability issues.
    
    Args:
        state: Current workflow state containing pr_diff
        
    Returns:
        Updated state with scale_findings populated
    """
    pr_diff = state.get("pr_diff", "")
    
    if not pr_diff:
        state["scale_findings"] = []
        return state
    
    user_message = f"Review the following code changes for scalability and performance issues:\n\n{pr_diff}"
    
    response = _call_llm_with_structured_output(
        system_prompt=SCALE_AGENT_PROMPT,
        user_message=user_message
    )
    
    state["scale_findings"] = response.findings
    return state


def clean_code_agent(state: AgentState) -> AgentState:
    """
    Clean Code Agent: Reviews code for maintainability and best practices.
    
    Args:
        state: Current workflow state containing pr_diff
        
    Returns:
        Updated state with clean_code_findings populated
    """
    pr_diff = state.get("pr_diff", "")
    
    if not pr_diff:
        state["clean_code_findings"] = []
        return state
    
    user_message = f"Review the following code changes for code quality and maintainability:\n\n{pr_diff}"
    
    response = _call_llm_with_structured_output(
        system_prompt=CLEAN_CODE_AGENT_PROMPT,
        user_message=user_message
    )
    
    state["clean_code_findings"] = response.findings
    return state


def chairperson_agent(state: AgentState) -> AgentState:
    """
    Chairperson Agent: Synthesizes all findings into a final review.
    
    Args:
        state: Current workflow state with all agent findings
        
    Returns:
        Updated state with final_verdict populated
    """
    security_findings = state.get("security_findings", [])
    scale_findings = state.get("scale_findings", [])
    clean_code_findings = state.get("clean_code_findings", [])
    
    # Prepare synthesis input
    synthesis_input = f"""
**Security Findings ({len(security_findings)}):**
{json.dumps(security_findings, indent=2) if security_findings else "None"}

**Scalability Findings ({len(scale_findings)}):**
{json.dumps(scale_findings, indent=2) if scale_findings else "None"}

**Code Quality Findings ({len(clean_code_findings)}):**
{json.dumps(clean_code_findings, indent=2) if clean_code_findings else "None"}
"""
    
    # Call LLM to synthesize findings
    response = completion(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": CHAIRPERSON_PROMPT},
            {"role": "user", "content": synthesis_input}
        ],
        temperature=0.5,
    )
    
    final_verdict = response.choices[0].message.content
    state["final_verdict"] = final_verdict
    
    return state
