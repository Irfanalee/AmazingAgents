"""
Financial Analysis Agent powered by Gemini + AgentOS
Real-time stock data with web search capabilities
"""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.os import AgentOS
from agno.storage.sqlite import SqliteStorage

# Agent Instructions
FINANCE_AGENT_INSTRUCTIONS = """
You are a professional financial analyst providing structured market insights.

## Output Rules:
1. **Numerical/Financial Data**: ALWAYS use markdown tables
   - Stock prices, metrics, ratios → Table format
   - Historical data, comparisons → Table format

2. **Text Analysis**: Use bullet points and short paragraphs
   - News summaries → Bullet points
   - Market sentiment → Brief paragraphs (2-3 sentences max)

3. **Keep responses concise** - Less words, more value

## Data Sources:
- **YFinance**: Real-time stock data, financials, historical prices
- **Web Search**: Latest news, LevelFields.ai insights, market events

## Analysis Framework:
When analyzing stocks, cover:
| Category | Metrics |
|----------|---------|
| Price | Current, 52-week high/low, change % |
| Valuation | P/E, P/B, Market Cap |
| Performance | YTD return, 1Y return |
| Fundamentals | Revenue, EPS, Dividend yield |

## LevelFields.ai Integration:
Search for "[stock] site:levelfields.ai" to find:
- AI-detected market events
- Earnings surprises
- Insider trading signals
- Institutional moves
"""

# Initialize Financial Agent
financial_agent = Agent(
    name="Financial Analyst",
    agent_id="finance-analyst-v1",
    model=Gemini(id="gemini-2.0-flash"),
    tools=[
        YFinanceTools(
            stock_price=True,
            stock_fundamentals=True,
            income_statements=True,
            balance_sheets=True,
            cash_flow_statements=True,
            key_financial_ratios=True,
            analyst_recommendations=True,
            company_news=True,
            historical_prices=True,
        ),
        DuckDuckGoTools(
            search=True,
            news=True,
        ),
    ],
    instructions=FINANCE_AGENT_INSTRUCTIONS,
    storage=SqliteStorage(
        table_name="financial_agent_sessions",
        db_file="data/finance_agent.db",
    ),
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,
)

# Initialize AgentOS
agent_os = AgentOS(
    agents=[financial_agent],
    name="Financial Analysis Platform",
    description="AI-powered stock analysis with real-time data and market insights",
)

# Get FastAPI app for deployment
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="financial_agent:app", reload=True)
