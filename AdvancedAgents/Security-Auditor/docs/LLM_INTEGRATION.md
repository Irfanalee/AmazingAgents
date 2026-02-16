# LLM/AI Integration Explained

## Overview

The Security Auditor **does NOT use LLMs internally** for its core functionality. Instead, it **exposes its capabilities TO LLMs** through the **Model Context Protocol (MCP)**, allowing AI assistants like Claude to use it as a security analysis tool.

## Architecture

```
┌─────────────────┐
│  AI Assistant   │  ← Claude, ChatGPT, etc.
│  (LLM)          │
└────────┬────────┘
         │ Uses tool via MCP
         │
         ▼
┌─────────────────┐
│  MCP Server     │  ← Security Auditor
│  (This Tool)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NIST NVD API   │  ← Real CVE data
└─────────────────┘
```

## How It Works

### 1. **MCP Server Implementation**

The tool implements an MCP (Model Context Protocol) server that exposes three tools:

**File:** [src/security_auditor/mcp_server.py](../src/security_auditor/mcp_server.py)

```python
class SecurityAuditorMCP:
    def __init__(self):
        self.server = Server("security-auditor")

    def _register_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            # Exposes 3 tools to LLMs:
            # 1. audit_package_file
            # 2. search_cve
            # 3. get_vulnerability_stats
```

### 2. **Tool Definitions**

Each tool has a schema that the LLM can understand:

#### Tool 1: `audit_package_file`
```json
{
  "name": "audit_package_file",
  "description": "Audit a package manifest file for CVE vulnerabilities",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" },
      "severity_filter": { "type": "array" },
      "format": { "enum": ["text", "markdown", "json"] }
    }
  }
}
```

#### Tool 2: `search_cve`
```json
{
  "name": "search_cve",
  "description": "Search for specific CVE vulnerabilities",
  "inputSchema": {
    "cve_id": { "type": "string" },
    "keyword": { "type": "string" },
    "severity": { "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"] }
  }
}
```

#### Tool 3: `get_vulnerability_stats`
```json
{
  "name": "get_vulnerability_stats",
  "description": "Get vulnerability statistics for a package file",
  "inputSchema": {
    "file_path": { "type": "string" }
  }
}
```

### 3. **Communication Flow**

```
User asks Claude:
"Can you audit my package.json for security vulnerabilities?"

     ↓

Claude (LLM) recognizes it needs the security-auditor tool

     ↓

Claude calls MCP tool:
audit_package_file(file_path="package.json", severity_filter=["CRITICAL", "HIGH"])

     ↓

MCP Server receives request

     ↓

Security Auditor executes:
1. Parse package.json
2. Query NVD API for each dependency
3. Analyze vulnerabilities
4. Generate executive summary

     ↓

MCP Server returns results to Claude

     ↓

Claude presents results to user in natural language
```

## Key Points

### ✅ **What the Tool DOES**

1. **Exposes functionality via MCP** - LLMs can call it as a tool
2. **Parses package files** - Extracts dependencies
3. **Queries NIST NVD API** - Gets real CVE data
4. **Analyzes vulnerabilities** - Matches deps to CVEs
5. **Generates reports** - Creates summaries

### ❌ **What the Tool DOESN'T DO**

1. **Does NOT use LLMs internally** - No API calls to OpenAI, Anthropic, etc.
2. **Does NOT generate text with AI** - Uses templates for reports
3. **Does NOT require AI API keys** - Only needs NVD API key
4. **Does NOT use embeddings** - Direct database queries only
5. **Does NOT train models** - Pure data analysis

## Why This Approach?

### Advantages

1. **Deterministic Results** - Same input = same output
2. **No AI Costs** - No LLM API fees
3. **Accurate Data** - Uses official NIST database
4. **Fast** - No LLM inference delays
5. **Privacy** - Data never sent to AI providers
6. **Reliable** - No hallucination risks

### Use Case

The tool is designed to be **used BY** AI assistants to help users with security audits:

```
User → AI Assistant → Security Auditor → NIST NVD
  ↑                                         ↓
  └──────── Results ─────────────────────────┘
```

## MCP Protocol Details

### Server Setup

**File:** [src/security_auditor/mcp_server.py](../src/security_auditor/mcp_server.py)

```python
async def run(self):
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await self.server.run(
            read_stream,
            write_stream,
            self.server.create_initialization_options()
        )
```

### Communication Protocol

- **Transport:** stdio (standard input/output)
- **Format:** JSON-RPC 2.0
- **Messages:** Tool calls and responses
- **Async:** Full async/await support

## Integration Examples

### Example 1: Claude Desktop Integration

**Configuration:** `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "security-auditor": {
      "command": "python",
      "args": ["-m", "security_auditor.mcp_server"],
      "env": {
        "NVD_API_KEY": "your_api_key"
      }
    }
  }
}
```

**User:** "Can you check my package.json for vulnerabilities?"

**Claude:** *Calls audit_package_file tool*

**Result:** Claude presents the security audit in natural language

### Example 2: Custom MCP Client

```python
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

async def use_security_auditor():
    async with stdio_client("python", ["-m", "security_auditor.mcp_server"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Call the tool
            result = await session.call_tool(
                "audit_package_file",
                {"file_path": "package.json"}
            )

            print(result)
```

## Data Flow

### Detailed Flow Diagram

```
┌────────────────────────────────────────────────┐
│ User Question:                                 │
│ "Are there security issues in my project?"    │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│ LLM (Claude):                                  │
│ - Understands natural language                │
│ - Decides to use security-auditor tool        │
│ - Constructs tool call parameters             │
└───────────────────┬────────────────────────────┘
                    │ MCP Tool Call
                    ▼
┌────────────────────────────────────────────────┐
│ MCP Server (Security Auditor):                │
│                                                │
│ 1. Receives: audit_package_file(              │
│      file_path="package.json"                 │
│    )                                          │
│                                                │
│ 2. PackageParser.parse_package_json()         │
│    → Extracts: express@4.17.1, lodash@4.20   │
│                                                │
│ 3. NVDClient.search_cves()                    │
│    → Queries NIST API for each package       │
│                                                │
│ 4. VulnerabilityAnalyzer.analyze_manifest()   │
│    → Matches CVEs to dependencies             │
│    → Filters by severity                      │
│                                                │
│ 5. ExecutiveSummaryGenerator.generate()       │
│    → Creates formatted report                 │
│                                                │
│ 6. Returns: TextContent with report           │
└───────────────────┬────────────────────────────┘
                    │ MCP Response
                    ▼
┌────────────────────────────────────────────────┐
│ LLM (Claude):                                  │
│ - Receives structured report                  │
│ - Interprets findings                         │
│ - Generates natural language response         │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│ User sees:                                     │
│ "I found 5 critical vulnerabilities in your   │
│  package.json. The most severe is CVE-2024-   │
│  1234 affecting express@4.17.1..."            │
└────────────────────────────────────────────────┘
```

## No LLM Dependencies

### Core Dependencies (NO AI)

```toml
dependencies = [
    "mcp>=1.0.0",        # Protocol, not AI
    "httpx>=0.27.0",     # HTTP client
    "pydantic>=2.0.0",   # Data validation
    "python-dotenv>=1.0.0"  # Config
]
```

### What's NOT Included

- ❌ `openai` - No OpenAI API
- ❌ `anthropic` - No Claude API
- ❌ `langchain` - No LLM framework
- ❌ `transformers` - No model loading
- ❌ `torch` / `tensorflow` - No ML frameworks

## Summary

| Aspect | Implementation |
|--------|----------------|
| **LLM Usage** | None - tool is used BY LLMs |
| **AI Integration** | Via MCP protocol only |
| **Data Source** | NIST NVD API (official CVE data) |
| **Report Generation** | Template-based, not AI-generated |
| **Natural Language** | Provided by calling LLM, not this tool |
| **Cost** | Free (except optional NVD API key) |
| **Privacy** | Data never sent to AI providers |

## Additional Resources

- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **MCP Integration Guide:** [MCP_INTEGRATION.md](MCP_INTEGRATION.md)
- **API Documentation:** [API_GUIDE.md](API_GUIDE.md)
- **Claude Desktop Setup:** [MCP_INTEGRATION.md#claude-desktop-integration](MCP_INTEGRATION.md#claude-desktop-integration)

---

**In Summary:** This tool is a **traditional data analysis application** that happens to expose its functionality through MCP so AI assistants can use it. It doesn't use AI internally - it provides AI assistants with accurate, deterministic security data.
