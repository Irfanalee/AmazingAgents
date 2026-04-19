import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.utils.logger import setup_logger
from src.agents.monitor import MetricUpdate
from src.mcp.mcp_config import get_mcp_config

class ActionHistory(BaseModel):
    """Records an action taken by a sub-agent and its result."""
    agent_name: str
    task: str
    result: str

class IncidentContext(BaseModel):
    """Maintains the state of an ongoing incident investigation."""
    initial_trigger: MetricUpdate
    history: List[ActionHistory] = Field(default_factory=list)
    is_resolved: bool = False

class SREDecision(BaseModel):
    """The structured reasoning result from Lead-SRE's decision loop."""
    analysis: str = Field(description="The thought process of the Lead-SRE based on the current context.")
    action_required: bool = Field(description="Whether a sub-agent needs to be triggered.")
    target_agent: Optional[str] = Field(description="The name of the sub-agent (Monitor, Debugger, Janitor, Sargent).")
    task_description: Optional[str] = Field(description="The specific instruction for the sub-agent.")

class LeadSRE:
    """The Senior Principal SRE Orchestrator using provider-agnostic LangChain logic."""
    def __init__(self):
        self.name = "Lead-SRE"
        self.logger = setup_logger(self.name)
        self.config = get_mcp_config()
        self.llm = self._init_llm()
        self.parser = JsonOutputParser(pydantic_object=SREDecision)

    def _init_llm(self):
        """Initialize the LLM based on configured provider."""
        provider = self.config.AI_PROVIDER.lower()
        model_name = self.config.AI_MODEL
        self.logger.info("initializing_llm", provider=provider, model=model_name)

        try:
            if provider == "google":
                from langchain_google_vertexai import VertexAI
                return VertexAI(model_name=model_name)
            
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model=model_name, api_key=self.config.AI_API_KEY)
            
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(model=model_name, api_key=self.config.AI_API_KEY)
            
            elif provider == "ollama":
                from langchain_ollama import ChatOllama
                return ChatOllama(model=model_name, base_url=self.config.AI_BASE_URL)
            
            else:
                self.logger.error("unsupported_provider", provider=provider)
                return None
        except Exception as e:
            self.logger.warning("llm_init_failed", error=str(e), fallback="mocked_reasoning")
            return None

    def analyze_situation(self, context: IncidentContext) -> SREDecision:
        """Use advanced reasoning to decide on the next course of action based on the incident context."""
        self.logger.info("analyzing_context", resource=context.initial_trigger.resource_id, history_length=len(context.history))

        if not self.llm:
            return self._mock_reasoning(context)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Senior Principal SRE. Your goal is to resolve an incident through a multi-step investigation loop.
            
Review the 'Incident Context' carefully. It contains:
1. The initial trigger (metrics that started the investigation).
2. A history of actions taken so far and their results.

Your decision should:
- Not repeat actions that have already been performed with the same parameters.
- If you have enough information, delegate a fix to the Janitor-Agent.
- If you need more info (logs, security scan, code audit), delegate to the appropriate sub-agent.
- If the issue is resolved or no further action is required, set 'action_required' to False.

Available sub-agents:
- Monitor-Agent: Live metrics.
- Debugger-Agent: Log and source code analysis.
- Janitor-Agent: Execution of fixes/remediations.
- Sargent-Agent: Security and vulnerability audits.

Always provide a clear analysis explaining why you are choosing the next step."""),
            ("user", "Incident Context:\n{context}\n\n{format_instructions}")
        ])

        chain = prompt | self.llm | self.parser
        
        try:
            decision_data = chain.invoke({
                "context": context.model_dump_json(),
                "format_instructions": self.parser.get_format_instructions()
            })
            self.logger.info("decision_made", decision=decision_data)
            return SREDecision(**decision_data)
        except Exception as e:
            self.logger.error("reasoning_failed", error=str(e))
            return self._mock_reasoning(context)

    def _mock_reasoning(self, context: IncidentContext) -> SREDecision:
        """Fallback logic for testing multi-step state transitions."""
        if len(context.history) == 0:
            return SREDecision(
                analysis="Initial CPU spike detected. Delegating to Debugger-Agent for log analysis.",
                action_required=True,
                target_agent="Debugger-Agent",
                task_description="Analyze system logs for CPU-heavy processes."
            )
        elif len(context.history) == 1:
            return SREDecision(
                analysis="Debugger found a high-CPU process (PID 1234). Delegating to Janitor-Agent for remediation.",
                action_required=True,
                target_agent="Janitor-Agent",
                task_description="Kill process 1234 and restart the service."
            )
        else:
            return SREDecision(
                analysis="Incident appears resolved after remediation.",
                action_required=False
            )

if __name__ == "__main__":
    orchestrator = LeadSRE()
    mock_metrics = MetricUpdate(
        resource_id="server-99", 
        cpu_percent=92.1, 
        memory_percent=40.0, 
        status="running", 
        timestamp="2026-04-13T12:00:00"
    )
    
    # Simulate Step 1
    context = IncidentContext(initial_trigger=mock_metrics)
    print("--- STEP 1: Initial Trigger ---")
    decision1 = orchestrator.analyze_situation(context)
    print(f"Decision: {decision1.analysis}\nTarget: {decision1.target_agent}")

    # Simulate Step 2
    context.history.append(ActionHistory(
        agent_name="Debugger-Agent",
        task="Analyze system logs for CPU-heavy processes.",
        result="Found process 'heavy_app' (PID 1234) consuming 90% CPU."
    ))
    print("\n--- STEP 2: After Debugger Finding ---")
    decision2 = orchestrator.analyze_situation(context)
    print(f"Decision: {decision2.analysis}\nTarget: {decision2.target_agent}")
