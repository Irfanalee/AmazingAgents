import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.utils.logger import setup_logger
from src.agents.monitor import MetricUpdate
from src.mcp.mcp_config import get_mcp_config

class SREDecision(BaseModel):
    """The structured reasoning result from Lead-SRE's decision loop."""
    analysis: str = Field(description="The thought process of the Lead-SRE.")
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

    def analyze_situation(self, metrics: MetricUpdate) -> SREDecision:
        """Use advanced reasoning to decide on the next course of action."""
        self.logger.info("analyzing_metrics", resource=metrics.resource_id, cpu=metrics.cpu_percent)

        if not self.llm:
            return self._mock_reasoning(metrics)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Senior Principal SRE. Analyze the given metrics and decide if any action is needed.
            
Available sub-agents to delegate to:
- Monitor-Agent: For fetching live container/host metrics.
- Debugger-Agent: For root-cause analysis in logs and source code.
- Janitor-Agent: For executing remediation commands (e.g., restarts, cleanup).
- Sargent-Agent: For vulnerability scanning and security audits (CVE scans).

Use these agents to resolve the incident effectively. Always provide a clear analysis and task description."""),
            ("user", "Current Metrics: {metrics}\n\n{format_instructions}")
        ])

        chain = prompt | self.llm | self.parser
        
        try:
            decision_data = chain.invoke({
                "metrics": metrics.model_dump_json(),
                "format_instructions": self.parser.get_format_instructions()
            })
            self.logger.info("decision_made", decision=decision_data)
            return SREDecision(**decision_data)
        except Exception as e:
            self.logger.error("reasoning_failed", error=str(e))
            return self._mock_reasoning(metrics)

    def _mock_reasoning(self, metrics: MetricUpdate) -> SREDecision:
        """Fallback logic if LLM is unavailable or for testing."""
        if metrics.cpu_percent > 80:
            return SREDecision(
                analysis="CPU usage is critically high (Mock). Triggering Debugger for root cause analysis.",
                action_required=True,
                target_agent="Debugger-Agent",
                task_description="Analyze process list and logs for high CPU usage."
            )
        return SREDecision(analysis="All metrics within normal range (Mock).", action_required=False)

if __name__ == "__main__":
    # Test with a mock CPU spike
    orchestrator = LeadSRE()
    mock_metrics = MetricUpdate(
        resource_id="server-99", 
        cpu_percent=92.1, 
        memory_percent=40.0, 
        status="running", 
        timestamp="2026-04-13T12:00:00"
    )
    decision = orchestrator.analyze_situation(mock_metrics)
    print(f"\nLead-SRE Analysis:\n{decision.analysis}")
    print(f"Action Required: {decision.action_required} -> {decision.target_agent}")
