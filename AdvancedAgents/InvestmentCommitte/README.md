# The Investment Committee

A Multi-Agent System where three AI agents (Bull, Bear, Portfolio Manager) debate stock investments using real-time data.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env and add your API keys

# 3. Run
python main.py
```

### Docker

```bash
# Build
docker build -t investment-committee .

# Run
docker run -it --env-file .env investment-committee

# Or with docker-compose
docker-compose run --rm investment-committee
```

## Features

- **Real-time Data**: Live stock prices, P/E ratios, 52-week ranges, news headlines
- **Multi-Agent Debate**: Bull vs Bear analysis with rebuttals
- **Mixed LLM Support**: Use different providers per agent (Anthropic + OpenAI)
- **International Stocks**: Auto-correction for Swedish stocks (e.g., SAAB-B → SAAB-B.ST)
- **Beautiful UI**: Rich terminal interface with side-by-side debate view
- **Docker Support**: Containerized for consistent deployment

## Architecture

```
User Input (AAPL) → yfinance Data → Bull Agent (Anthropic) ⟍
                                                            → Portfolio Manager (OpenAI) → BUY/SELL/HOLD
                                     Bear Agent (Anthropic) ⟋
                                     (+ Rebuttal Phase)
```

## Configuration

Edit `.env`:

```env
# Per-Agent LLM Configuration
BULL_PROVIDER=anthropic
BEAR_PROVIDER=anthropic
PM_PROVIDER=openai

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx

# Models
ANTHROPIC_MODEL=claude-3-haiku-20240307
OPENAI_MODEL=gpt-4-turbo-preview
```

## Usage Examples

```bash
# US Stocks
python main.py
> AAPL

# Swedish Stocks (auto-corrects)
> SAAB-B

# Invalid ticker shows helpful error
> FAKESTOCK
⚠️  Stock Not Found
✗ Ticker 'FAKESTOCK' not found.
```

## Project Structure

```
InvestmentCommitte/
├── main.py                      # Entry point + UI orchestration
├── src/
│   └── investment_committee/    # Core package
│       ├── __init__.py          # Package exports
│       ├── agents.py            # Bull, Bear, PM agents
│       ├── tools.py             # yfinance data layer
│       └── config.py            # Environment config
├── tests/                       # Unit tests
│   ├── conftest.py              # Shared fixtures
│   ├── test_agents.py           # Agent tests
│   ├── test_config.py           # Config tests
│   └── test_tools.py            # Tools tests
├── requirements.txt             # Dependencies
├── pyproject.toml               # Ruff & pytest config
├── Dockerfile                   # Container build
├── docker-compose.yml           # Container orchestration
└── .env                         # API keys (gitignored)
```

## Development

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_agents.py -v
```

### Linting

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

## How It Works

1. **Data Fetch**: Get live stock data from Yahoo Finance
2. **Initial Analysis**: Bull and Bear analyze simultaneously
3. **Rebuttal**: Each agent counters the other's arguments
4. **Decision**: Portfolio Manager weighs both sides → BUY/SELL/HOLD

## Troubleshooting

**Invalid ticker**: System shows helpful error with suggestions
**API errors**: Check `.env` file has correct API keys
**Missing modules**: Run `pip install -r requirements.txt`

## Future Enhancements

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for roadmap:
- Session history storage
- Agent memory across analyses
- Performance tracking & backtesting
- Async execution
- Web interface

## Disclaimer

Educational tool only. Not financial advice. Consult licensed advisors before investing.

---

Built with [Claude](https://anthropic.com), [OpenAI](https://openai.com), [yfinance](https://github.com/ranaroussi/yfinance), and [Rich](https://github.com/Textualize/rich)
