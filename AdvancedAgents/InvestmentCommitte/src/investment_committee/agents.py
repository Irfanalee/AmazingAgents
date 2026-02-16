"""
Agent Layer: Bull, Bear, and Portfolio Manager AI Agents
"""

import os
from enum import Enum

from pydantic import BaseModel


class AgentRole(str, Enum):
    """Agent role definitions"""

    BULL = "bull"
    BEAR = "bear"
    PORTFOLIO_MANAGER = "portfolio_manager"


class AgentResponse(BaseModel):
    """Structured response from an agent"""

    role: AgentRole
    content: str
    raw_response: str


class Decision(str, Enum):
    """Portfolio Manager decision options"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class PortfolioDecision(BaseModel):
    """Final decision from Portfolio Manager"""

    decision: Decision
    justification: str
    confidence: str | None = None


class Agent:
    """Base Agent class for Investment Committee"""

    SYSTEM_PROMPTS = {
        AgentRole.BULL: """You are a growth-focused aggressive investor known as "The Bull".

Your mandate:
- Look for potential, innovation, and market expansion opportunities
- Focus on long-term growth catalysts and competitive advantages
- Ignore short-term risks and market noise
- Be optimistic about future earnings potential
- Highlight technological breakthroughs and market disruptions

You MUST output your analysis in this EXACT structure:

<key_points>
- [3-5 bullet points summarizing your strongest arguments]
</key_points>

<bull_thesis>
[Your detailed analysis covering:]
1. Key growth drivers
2. Competitive advantages
3. Market opportunity size
4. Why current concerns are overblown
</bull_thesis>

Be persuasive and confident in your bullish stance.""",
        AgentRole.BEAR: """You are a risk-averse, skeptical investor known as "The Bear".

Your mandate:
- Look for overvaluation, excessive hype, and unsustainable growth
- Identify regulatory hurdles, competitive threats, and macroeconomic headwinds
- Focus on downside risks and what could go wrong
- Challenge optimistic assumptions with hard data
- Highlight valuation concerns and market saturation

You MUST output your analysis in this EXACT structure:

<key_points>
- [3-5 bullet points summarizing your strongest arguments]
</key_points>

<bear_thesis>
[Your detailed analysis covering:]
1. Valuation concerns
2. Competitive threats and market risks
3. Regulatory or macroeconomic headwinds
4. Why the bulls are wrong
</bear_thesis>

Be critical and rigorous in your bearish stance.""",
        AgentRole.PORTFOLIO_MANAGER: """You are an experienced Portfolio Manager and the final decision maker.

Your mandate:
- Read and analyze both the Bull and Bear key points carefully
- Weigh the evidence objectively without bias
- Consider both upside potential and downside risks
- Make a clear, decisive recommendation

You MUST output your decision in this exact format:
<decision>BUY</decision> or <decision>SELL</decision> or <decision>HOLD</decision>

Followed by:
<justification>
Your reasoning here (2-3 paragraphs explaining why you chose this decision,
which arguments were most compelling, and what factors tipped the scale)
</justification>

Be balanced but decisive. Don't hedge excessively.""",
    }

    def __init__(self, role: AgentRole, llm_provider: str = "anthropic"):
        """
        Initialize an agent with a specific role.

        Args:
            role: The agent's role (BULL, BEAR, or PORTFOLIO_MANAGER)
            llm_provider: "openai" or "anthropic"
        """
        self.role = role
        self.system_prompt = self.SYSTEM_PROMPTS[role]
        self.llm_provider = llm_provider
        self._client = None
        self._conversation_history: list[dict] = []  # For multi-turn conversations

    def _get_client(self):
        """Lazy load the LLM client"""
        if self._client is None:
            if self.llm_provider == "openai":
                from openai import OpenAI

                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            elif self.llm_provider == "anthropic":
                from anthropic import Anthropic

                self._client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
        return self._client

    def _call_openai(self, messages: list[dict]) -> str:
        """Call OpenAI API with conversation history"""
        client = self._get_client()
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        response = client.chat.completions.create(
            model=model, messages=full_messages, temperature=0.7, max_tokens=2000
        )
        return response.choices[0].message.content

    def _call_anthropic(self, messages: list[dict]) -> str:
        """Call Anthropic API with conversation history"""
        client = self._get_client()
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

        response = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.7,
            system=self.system_prompt,
            messages=messages,
        )
        return response.content[0].text

    def reset_conversation(self):
        """Clear conversation history for a fresh session"""
        self._conversation_history = []

    def invoke(self, user_message: str, continue_conversation: bool = False) -> AgentResponse:
        """
        Invoke the agent with a message.

        Args:
            user_message: The prompt/data to send to the agent
            continue_conversation: If True, append to existing conversation history
                                   If False, start fresh (default for backwards compatibility)

        Returns:
            AgentResponse with structured output
        """
        if not continue_conversation:
            self._conversation_history = []

        # Add user message to history
        self._conversation_history.append({"role": "user", "content": user_message})

        # Make API call with full conversation history
        if self.llm_provider == "openai":
            raw_response = self._call_openai(self._conversation_history)
        else:
            raw_response = self._call_anthropic(self._conversation_history)

        # Add assistant response to history
        self._conversation_history.append({"role": "assistant", "content": raw_response})

        return AgentResponse(role=self.role, content=raw_response, raw_response=raw_response)


def extract_key_points(response_content: str) -> str:
    """
    Extract key points from an agent's response.

    Args:
        response_content: Full response content with XML tags

    Returns:
        Extracted key points or abbreviated content if tags not found
    """
    import re

    pattern = r"<key_points>(.*?)</key_points>"
    match = re.search(pattern, response_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: return first 500 chars if no key_points found
    return response_content[:500] + "..." if len(response_content) > 500 else response_content


class BullAgent(Agent):
    """The Bull - Growth-focused aggressive investor"""

    def __init__(self, llm_provider: str = "anthropic"):
        super().__init__(AgentRole.BULL, llm_provider)

    def analyze(
        self, financial_data: str, bear_thesis: str | None = None, use_key_points_only: bool = True
    ) -> AgentResponse:
        """
        Analyze stock data from a bullish perspective (legacy single-call method).

        Args:
            financial_data: Formatted financial metrics
            bear_thesis: Optional bear thesis to counter
            use_key_points_only: If True, extract only key points for rebuttals (saves tokens)

        Returns:
            AgentResponse with bull thesis
        """
        if bear_thesis:
            bear_points = extract_key_points(bear_thesis) if use_key_points_only else bear_thesis
            prompt = f"""Stock: {financial_data.split("|")[0].strip()}

BEAR'S KEY ARGUMENTS TO COUNTER:
{bear_points}

Provide your REBUTTAL addressing these concerns. Reinforce your bullish thesis."""
        else:
            prompt = f"""{financial_data}

Analyze this stock and provide your bullish investment thesis."""

        return self.invoke(prompt)

    def analyze_initial(self, financial_data: str) -> AgentResponse:
        """
        Initial analysis - starts a new conversation.

        Args:
            financial_data: Formatted financial metrics

        Returns:
            AgentResponse with initial bull thesis
        """
        self.reset_conversation()
        prompt = f"""{financial_data}

Analyze this stock and provide your bullish investment thesis."""
        return self.invoke(prompt, continue_conversation=False)

    def analyze_rebuttal(self, bear_thesis: str, use_key_points_only: bool = True) -> AgentResponse:
        """
        Rebuttal analysis - continues the existing conversation (no need to resend financial data).

        Args:
            bear_thesis: The bear's thesis to counter
            use_key_points_only: If True, extract only key points (saves tokens)

        Returns:
            AgentResponse with bull rebuttal
        """
        bear_points = extract_key_points(bear_thesis) if use_key_points_only else bear_thesis

        prompt = f"""The Bear has responded with these concerns:

{bear_points}

Provide your REBUTTAL addressing these concerns. Reinforce your bullish thesis."""

        return self.invoke(prompt, continue_conversation=True)


class BearAgent(Agent):
    """The Bear - Risk-averse skeptical investor"""

    def __init__(self, llm_provider: str = "anthropic"):
        super().__init__(AgentRole.BEAR, llm_provider)

    def analyze(
        self, financial_data: str, bull_thesis: str | None = None, use_key_points_only: bool = True
    ) -> AgentResponse:
        """
        Analyze stock data from a bearish perspective (legacy single-call method).

        Args:
            financial_data: Formatted financial metrics
            bull_thesis: Optional bull thesis to counter
            use_key_points_only: If True, extract only key points for rebuttals (saves tokens)

        Returns:
            AgentResponse with bear thesis
        """
        if bull_thesis:
            bull_points = extract_key_points(bull_thesis) if use_key_points_only else bull_thesis
            prompt = f"""Stock: {financial_data.split("|")[0].strip()}

BULL'S KEY ARGUMENTS TO COUNTER:
{bull_points}

Provide your REBUTTAL addressing this overoptimism. Reinforce your bearish thesis."""
        else:
            prompt = f"""{financial_data}

Analyze this stock and provide your bearish investment thesis."""

        return self.invoke(prompt)

    def analyze_initial(self, financial_data: str) -> AgentResponse:
        """
        Initial analysis - starts a new conversation.

        Args:
            financial_data: Formatted financial metrics

        Returns:
            AgentResponse with initial bear thesis
        """
        self.reset_conversation()
        prompt = f"""{financial_data}

Analyze this stock and provide your bearish investment thesis."""
        return self.invoke(prompt, continue_conversation=False)

    def analyze_rebuttal(self, bull_thesis: str, use_key_points_only: bool = True) -> AgentResponse:
        """
        Rebuttal analysis - continues the existing conversation (no need to resend financial data).

        Args:
            bull_thesis: The bull's thesis to counter
            use_key_points_only: If True, extract only key points (saves tokens)

        Returns:
            AgentResponse with bear rebuttal
        """
        bull_points = extract_key_points(bull_thesis) if use_key_points_only else bull_thesis

        prompt = f"""The Bull has responded with these arguments:

{bull_points}

Provide your REBUTTAL addressing this overoptimism. Reinforce your bearish thesis."""

        return self.invoke(prompt, continue_conversation=True)


class PortfolioManagerAgent(Agent):
    """The Portfolio Manager - Final decision maker"""

    def __init__(self, llm_provider: str = "anthropic"):
        super().__init__(AgentRole.PORTFOLIO_MANAGER, llm_provider)

    def make_decision(
        self,
        financial_data: str,
        bull_thesis: str,
        bear_thesis: str,
        use_key_points_only: bool = True,
    ) -> AgentResponse:
        """
        Make final investment decision based on both theses.

        Args:
            financial_data: Formatted financial metrics
            bull_thesis: The bull's argument
            bear_thesis: The bear's argument
            use_key_points_only: If True, use only key points from theses (saves tokens)

        Returns:
            AgentResponse with final decision
        """
        # Extract key points to reduce token usage
        bull_points = extract_key_points(bull_thesis) if use_key_points_only else bull_thesis
        bear_points = extract_key_points(bear_thesis) if use_key_points_only else bear_thesis

        prompt = f"""{financial_data}

BULL'S KEY ARGUMENTS:
{bull_points}

BEAR'S KEY ARGUMENTS:
{bear_points}

As Portfolio Manager, weigh both arguments and make your final decision: BUY, SELL, or HOLD.
Provide clear justification for your choice."""

        return self.invoke(prompt)

    @staticmethod
    def parse_decision(response: AgentResponse) -> PortfolioDecision:
        """
        Parse the Portfolio Manager's response into structured decision.

        Args:
            response: AgentResponse from Portfolio Manager

        Returns:
            PortfolioDecision object
        """
        content = response.content

        # Extract decision
        decision_str = "HOLD"  # default
        if "<decision>" in content and "</decision>" in content:
            start = content.find("<decision>") + len("<decision>")
            end = content.find("</decision>")
            decision_str = content[start:end].strip().upper()

        # Extract justification
        justification = content
        if "<justification>" in content and "</justification>" in content:
            start = content.find("<justification>") + len("<justification>")
            end = content.find("</justification>")
            justification = content[start:end].strip()

        try:
            decision = Decision[decision_str]
        except KeyError:
            decision = Decision.HOLD

        return PortfolioDecision(decision=decision, justification=justification)
