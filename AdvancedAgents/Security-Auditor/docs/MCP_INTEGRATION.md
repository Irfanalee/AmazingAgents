# MCP Integration Guide

This guide explains how to integrate Security Auditor with AI assistants using the Model Context Protocol (MCP).

## What is MCP?

The Model Context Protocol (MCP) is a standard protocol that allows AI assistants to interact with external tools and data sources. Security Auditor implements an MCP server that exposes security auditing capabilities.

## Running the MCP Server

### Start the Server

```bash
python -m security_auditor.mcp_server
```

The server will:
- Listen for MCP requests on stdio
- Load configuration from `.env` file
- Expose three security auditing tools to AI assistants

### Environment Configuration

Make sure your `.env` file is configured:

```bash
NVD_API_KEY=your_api_key_here
NVD_RATE_LIMIT=50
```

## Available MCP Tools

### 1. audit_package_file

Audit a package manifest file for known CVE vulnerabilities.

**Input Schema:**
```json
{
  "file_path": "path/to/package.json",
  "severity_filter": ["CRITICAL", "HIGH"],
  "include_dev_dependencies": false,
  "days_back": 30,
  "format": "text"
}
```

**Parameters:**
- `file_path` (required): Path to package manifest
- `severity_filter`: Array of severities (default: ["CRITICAL", "HIGH"])
- `include_dev_dependencies`: Include dev dependencies (default: false)
- `days_back`: Only consider CVEs from last N days (optional)
- `format`: Output format - "text", "markdown", or "json" (default: "text")

**Returns:**
Executive summary report in the requested format

**Example Usage:**
```json
{
  "name": "audit_package_file",
  "arguments": {
    "file_path": "/path/to/package.json",
    "severity_filter": ["CRITICAL", "HIGH"],
    "format": "markdown"
  }
}
```

### 2. search_cve

Search for specific CVE vulnerabilities from the NVD database.

**Input Schema:**
```json
{
  "cve_id": "CVE-2024-1234",
  "keyword": "nodejs",
  "product": "express",
  "severity": "CRITICAL",
  "limit": 10
}
```

**Parameters:**
- `cve_id`: Specific CVE identifier
- `keyword`: Search keyword in descriptions
- `product`: Product name to search for
- `severity`: Filter by severity ("CRITICAL", "HIGH", "MEDIUM", "LOW")
- `limit`: Maximum results (default: 10)

**Returns:**
Detailed CVE information including severity, CVSS scores, and references

**Example Usage:**
```json
{
  "name": "search_cve",
  "arguments": {
    "keyword": "nodejs buffer overflow",
    "severity": "CRITICAL",
    "limit": 5
  }
}
```

### 3. get_vulnerability_stats

Get vulnerability statistics without detailed listings.

**Input Schema:**
```json
{
  "file_path": "path/to/package.json"
}
```

**Parameters:**
- `file_path` (required): Path to package manifest

**Returns:**
JSON object with vulnerability counts by severity

**Example Usage:**
```json
{
  "name": "get_vulnerability_stats",
  "arguments": {
    "file_path": "/path/to/requirements.txt"
  }
}
```

## Integration Examples

### Claude Desktop Integration

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "security-auditor": {
      "command": "python",
      "args": [
        "-m",
        "security_auditor.mcp_server"
      ],
      "env": {
        "NVD_API_KEY": "your_api_key_here",
        "NVD_RATE_LIMIT": "50"
      }
    }
  }
}
```

### Using with Claude

Once configured, you can ask Claude to:

```
"Can you audit my package.json file for security vulnerabilities?"

"Search for critical CVEs affecting Node.js in the last 30 days"

"What are the vulnerability statistics for my project?"
```

Claude will use the MCP tools to:
1. Parse your package files
2. Query the NVD database
3. Generate executive summaries
4. Provide actionable recommendations

## Custom MCP Client Example

```python
import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

async def use_security_auditor():
    """Example MCP client using Security Auditor."""

    # Connect to the MCP server
    async with stdio_client("python", ["-m", "security_auditor.mcp_server"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools])

            # Call audit_package_file tool
            result = await session.call_tool(
                "audit_package_file",
                {
                    "file_path": "package.json",
                    "severity_filter": ["CRITICAL", "HIGH"],
                    "format": "json"
                }
            )

            print("Audit result:", result)

asyncio.run(use_security_auditor())
```

## MCP Server Architecture

```
┌─────────────────┐
│   AI Assistant  │
│   (e.g. Claude) │
└────────┬────────┘
         │ MCP Protocol
         │ (stdio)
┌────────▼────────┐
│  MCP Server     │
│  (Python)       │
├─────────────────┤
│ Tools:          │
│ • audit_package │
│ • search_cve    │
│ • get_stats     │
└────────┬────────┘
         │
    ┌────▼────┐
    │ NVD API │
    └─────────┘
```

## Tool Response Formats

### Text Format

```
================================================================================
SECURITY AUDIT EXECUTIVE SUMMARY
================================================================================

Analysis Date: 2024-12-10 14:30:00
Project: example-app v1.0.0

OVERVIEW
--------------------------------------------------------------------------------
Packages Analyzed: 10
Packages with Vulnerabilities: 3
Total Vulnerabilities Found: 8
...
```

### Markdown Format

```markdown
# Security Audit Executive Summary

**Analysis Date:** 2024-12-10 14:30:00
**Project:** example-app v1.0.0

## Overview
- **Packages Analyzed:** 10
- **Packages with Vulnerabilities:** 3
- **Total Vulnerabilities:** 8
...
```

### JSON Format

```json
{
  "analysis_date": "2024-12-10T14:30:00",
  "project": {
    "name": "example-app",
    "version": "1.0.0"
  },
  "summary": {
    "packages_analyzed": 10,
    "packages_with_vulnerabilities": 3,
    "total_vulnerabilities": 8,
    "actionable_vulnerabilities": 5
  },
  "severity_breakdown": {
    "critical": 2,
    "high": 3,
    "medium": 2,
    "low": 1
  },
  "risk_level": "HIGH"
}
```

## Best Practices

### 1. API Key Management

Always use environment variables for API keys:

```json
{
  "mcpServers": {
    "security-auditor": {
      "env": {
        "NVD_API_KEY": "${NVD_API_KEY}"
      }
    }
  }
}
```

### 2. Rate Limiting

Be aware of NVD API rate limits:
- Without key: 5 requests/30 seconds
- With key: 50 requests/30 seconds

For large projects, the analysis may take several minutes.

### 3. Caching

Consider implementing caching for repeated analyses:

```python
# The MCP server could cache results for a configurable TTL
# This is a potential enhancement for future versions
```

### 4. Error Handling

The MCP server handles errors gracefully:
- File not found errors
- Invalid file format errors
- NVD API errors
- Network timeout errors

Errors are returned as text responses to the AI assistant.

### 5. Security

- Never commit API keys to version control
- Use environment variables or secure secret management
- Restrict file system access to necessary directories
- Validate all input parameters

## Troubleshooting

### Server Won't Start

```bash
# Check Python version
python --version  # Should be 3.10+

# Verify dependencies
pip install -r requirements.txt

# Test manually
python -m security_auditor.mcp_server
```

### No Response from Server

- Check that .env file exists and has NVD_API_KEY
- Verify network connectivity to nvd.nist.gov
- Check rate limit hasn't been exceeded

### Slow Performance

- Get an NVD API key for higher rate limits
- Reduce number of dependencies to analyze
- Use severity filtering to reduce API calls
- Consider analyzing only runtime dependencies

## Advanced Configuration

### Custom MCP Server

You can extend the MCP server with custom tools:

```python
from security_auditor.mcp_server import SecurityAuditorMCP

class CustomSecurityAuditor(SecurityAuditorMCP):
    def _register_handlers(self):
        super()._register_handlers()

        @self.server.list_tools()
        async def list_tools():
            tools = await super().list_tools()

            # Add custom tool
            tools.append(Tool(
                name="custom_scan",
                description="Custom security scan",
                inputSchema={...}
            ))

            return tools
```

### Environment-Specific Configuration

```bash
# Development
NVD_API_KEY=dev_key
NVD_RATE_LIMIT=5

# Production
NVD_API_KEY=prod_key
NVD_RATE_LIMIT=50
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [NVD API Documentation](https://nvd.nist.gov/developers/vulnerabilities)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/mcp)

## Support

For issues with MCP integration:
1. Check server logs
2. Verify configuration
3. Test with CLI first
4. Open an issue on GitHub
