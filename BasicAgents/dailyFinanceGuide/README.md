# Financial Analysis Agent

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Agno](https://img.shields.io/badge/Agno-FF6B6B?style=for-the-badge&logo=robot&logoColor=white)
![YFinance](https://img.shields.io/badge/YFinance-FFD700?style=for-the-badge&logo=yahoo&logoColor=black)

AI-powered stock analysis agent using Gemini + AgentOS with real-time market data.

## Features

| Feature | Description |
|---------|-------------|
| **Gemini 2.0** | Google's latest AI model for analysis |
| **YFinance** | Real-time stock prices, fundamentals, financials |
| **Web Search** | DuckDuckGo for news and LevelFields.ai insights |
| **AgentOS** | Interactive playground interface |
| **Session Memory** | SQLite-based conversation history |

## Setup

```bash
# Clone and navigate
cd dailyFinanceGuide

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

## Get API Key

- **Gemini**: [Google AI Studio](https://aistudio.google.com/apikey)
- **Agno** (optional): [app.agno.com](https://app.agno.com)

## Run

```bash
python financial_agent.py
```

Open `http://localhost:7777` for the playground interface.

## Usage Examples

| Query | What You Get |
|-------|--------------|
| `Analyze AAPL` | Price, valuation, fundamentals table |
| `Compare MSFT vs GOOGL` | Side-by-side metrics comparison |
| `TSLA news from levelfields.ai` | AI-detected market events |
| `NVDA earnings analysis` | Financial statements + analyst views |

## Data Sources

- **YFinance**: Stock prices, P/E, market cap, revenue, EPS
- **LevelFields.ai**: AI event detection, insider moves, earnings surprises
- **DuckDuckGo**: Latest market news and sentiment

## Output Format

The agent follows strict formatting rules:

- **Numerical data** → Markdown tables
- **Text analysis** → Bullet points
- **Summaries** → Short paragraphs (2-3 sentences)

## Project Structure

```
dailyFinanceGuide/
├── financial_agent.py   # Main agent code
├── requirements.txt     # Dependencies
├── .env.example         # API key template
├── data/                # SQLite storage
└── README.md
```

## License

MIT
