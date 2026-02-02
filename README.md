# AmazingAgents

A personal collection of AI agents that I thought of and created because it was fun to build them.

## Folder Structure

```
AmazingAgents/
├── BasicAgents/           # Simple, single-purpose agents
│   ├── dailyFinanceGuide/
│   ├── CorpVal/
│   └── CompEval/
├── AdvancedAgents/        # Complex, multi-capability agents
│   ├── LegacyBridge-SQL-AI/
│   └── rag-docs-query/
└── README.md
```

## Agents

### BasicAgents

| Agent | Description |
|-------|-------------|
| **dailyFinanceGuide** | AI-powered stock analysis agent using Gemini that provides real-time market data, fundamentals, and news insights. |
| **CorpVal** | Warren - Claude-powered M&A valuation expert for company valuation, deal structuring, financial modeling, and M&A strategy. |
| **CompEval** | Financial analysis tool project with Claude-based personas for AI-powered analysis and intelligent insights. |

### AdvancedAgents

| Agent | Description |
|-------|-------------|
| **LegacyBridge-SQL-AI** | MCP server that bridges LLMs with legacy SQL databases, enabling natural language queries against databases without knowing SQL. Features schema discovery, read-only access, and connection pooling. |
| **rag-docs-query** | Contextual retrieval system implementing Anthropic's technique for improved document search. Combines contextual embeddings with hybrid search (vector + BM25) for up to 67% improvement in retrieval accuracy. |
