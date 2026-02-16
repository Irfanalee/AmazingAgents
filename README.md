# AmazingAgents

A personal collection of AI agents that I thought of and created because it was fun to build them.

## Folder Structure

```
AmazingAgents/
├── BasicAgents/           # Simple, single-purpose agents
│   ├── dailyFinanceGuide/
│   ├── CorpVal/
│   ├── CompEval/
│   ├── LyricsGenerator/
│   └── tech_term_transl/
├── AdvancedAgents/        # Complex, multi-capability agents
│   ├── LegacyBridge-SQL-AI/
│   ├── rag-docs-query/
│   ├── InvestmentCommitte/
│   ├── Security-Auditor/
│   ├── ShadowARB/
│   └── SocialMediaVideoEdit-Gem/
└── README.md
```

## Agents

### [BasicAgents](./BasicAgents)

| Agent | Description |
|-------|-------------|
| [**dailyFinanceGuide**](./BasicAgents/dailyFinanceGuide) | AI-powered stock analysis agent using Gemini that provides real-time market data, fundamentals, and news insights. |
| [**CorpVal**](./BasicAgents/CorpVal) | Warren - Claude-powered M&A valuation expert for company valuation, deal structuring, financial modeling, and M&A strategy. |
| [**CompEval**](./BasicAgents/CompEval) | Financial analysis tool project with Claude-based personas for AI-powered analysis and intelligent insights. |
| [**LyricsGenerator**](./BasicAgents/LyricsGenerator) | Streamlit app that generates original song lyrics using OpenAI's GPT model with genre and mood selection. |
| [**tech_term_transl**](./BasicAgents/tech_term_transl) | Streamlit app that translates complex technical and business terms into plain English using an AI agent with structured breakdowns. |

### [AdvancedAgents](./AdvancedAgents)

| Agent | Description |
|-------|-------------|
| [**LegacyBridge-SQL-AI**](./AdvancedAgents/LegacyBridge-SQL-AI) | MCP server that bridges LLMs with legacy SQL databases, enabling natural language queries against databases without knowing SQL. Features schema discovery, read-only access, and connection pooling. |
| [**rag-docs-query**](./AdvancedAgents/rag-docs-query) | Contextual retrieval system implementing Anthropic's technique for improved document search. Combines contextual embeddings with hybrid search (vector + BM25) for up to 67% improvement in retrieval accuracy. |
| [**InvestmentCommitte**](./AdvancedAgents/InvestmentCommitte) | Multi-agent system where three AI agents (Bull, Bear, Portfolio Manager) debate stock investments using real-time financial data. |
| [**Security-Auditor**](./AdvancedAgents/Security-Auditor) | Security auditing tool that analyzes software dependencies for known CVE vulnerabilities using the NIST National Vulnerability Database API. |
| [**ShadowARB**](./AdvancedAgents/ShadowARB) | Automated code review system using three specialized AI agents that review GitHub Pull Requests in parallel and post consolidated findings. |
| [**SocialMediaVideoEdit-Gem**](./AdvancedAgents/SocialMediaVideoEdit-Gem) | AI-powered video editing tool that automatically analyzes videos, extracts engaging highlights, and creates social media-ready teasers with manual clipping support. |
