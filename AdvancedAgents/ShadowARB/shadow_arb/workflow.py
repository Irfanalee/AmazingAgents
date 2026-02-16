"""
LangGraph workflow orchestration for Shadow ARB.
Defines the stateful workflow with parallel agent execution and synthesis.
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents import (
    security_agent,
    scale_agent,
    clean_code_agent,
    chairperson_agent,
)


def create_workflow() -> StateGraph:
    """
    Creates the Shadow ARB workflow graph.
    
    Architecture:
        1. START -> [security_agent, scale_agent, clean_code_agent] (PARALLEL)
        2. [All agents] -> chairperson_agent (SYNTHESIS)
        3. chairperson_agent -> END
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the StateGraph with AgentState
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("security_agent", security_agent)
    workflow.add_node("scale_agent", scale_agent)
    workflow.add_node("clean_code_agent", clean_code_agent)
    workflow.add_node("chairperson_agent", chairperson_agent)
    
    # Define the workflow edges
    # All three agents run in parallel from the start
    workflow.set_entry_point("security_agent")
    workflow.set_entry_point("scale_agent")
    workflow.set_entry_point("clean_code_agent")
    
    # All agents feed into the chairperson
    workflow.add_edge("security_agent", "chairperson_agent")
    workflow.add_edge("scale_agent", "chairperson_agent")
    workflow.add_edge("clean_code_agent", "chairperson_agent")
    
    # Chairperson produces the final output
    workflow.add_edge("chairperson_agent", END)
    
    # Compile the workflow
    return workflow.compile()


def run_review(pr_diff: str) -> str:
    """
    Executes the Shadow ARB review workflow.
    
    Args:
        pr_diff: Raw code changes from the GitHub Pull Request
        
    Returns:
        Final synthesized review as markdown string
    """
    # Initialize state
    initial_state: AgentState = {
        "pr_diff": pr_diff,
        "security_findings": [],
        "scale_findings": [],
        "clean_code_findings": [],
        "final_verdict": "",
    }
    
    # Create and run the workflow
    app = create_workflow()
    final_state = app.invoke(initial_state)
    
    return final_state["final_verdict"]
