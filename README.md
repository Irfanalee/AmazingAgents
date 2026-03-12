# AmazingAgents

A personal collection of AI agents that I thought of and created because it was fun to build them.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_AI-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

## Folder Structure

```
AmazingAgents/
├── BasicAgents/           # Simple, single-purpose agents
│   ├── dailyFinanceGuide/
│   ├── CorpVal/
│   ├── CompEval/
│   ├── LyricsGenerator/
│   ├── SongMaker/
│   └── tech_term_transl/
├── AdvancedAgents/        # Complex, multi-capability agents
│   ├── LegacyBridge-SQL-AI/
│   ├── rag-docs-query/
│   ├── InvestmentCommitte/
│   ├── Security-Auditor/
│   ├── ShadowARB/
│   ├── SocialMediaVideoEdit-Gem/
│   └── McK-Consutlancy/
├── SovereignAgents/       # Autonomous, self-directed agents
│   └── invoice_processor/
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
| [**SongMaker**](./BasicAgents/SongMaker) | AI agent that turns lyrics into a full song (vocals + music) using the Suno API, with in-browser playback and MP3 download. |
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
| [**McK-Consutlancy**](./AdvancedAgents/McK-Consutlancy) | AI-powered consulting toolkit that runs 12 McKinsey-grade strategic frameworks against a user's business using Claude AI. Features streaming analysis, response caching, session management, and DOCX/PDF export. |

### [SovereignAgents](./SovereignAgents)

| Agent | Description |
|-------|-------------|
| [**invoice_processor**](./SovereignAgents/invoice_processor) | Automated invoice and receipt processing pipeline using a local `doc-intel` model via Ollama. Supports PDF, PNG, and JPG uploads with OCR extraction, structured data parsing, SQLite storage, and a Gradio web interface. |
