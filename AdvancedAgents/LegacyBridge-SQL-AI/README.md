# Legacy Bridge - SQL Analyst MCP Server

An MCP (Model Context Protocol) server that bridges LLMs with legacy SQL databases, allowing natural language queries against the Chinook database (simulating SAP/Oracle ERP systems).

## Overview

This project demonstrates how to expose a legacy database to LLMs through MCP, enabling executives and non-technical users to query business data without knowing SQL.

### Features

- 📊 **Schema Discovery**: Exposes database schema as MCP resources
- 🔍 **Natural Language to SQL**: LLMs can generate and execute SQL queries
- 🔒 **Read-Only Access**: Secure, read-only query execution
- 🎯 **Business Intelligence**: Query customers, invoices, tracks, and artists
- 🛡️ **Error Handling**: Graceful error messages and validation
- ⚡ **Connection Pooling**: Thread-safe connection management for better performance

## Database

Uses the **Chinook Database** - a sample database representing a digital media store with:
- Customers and invoices
- Artists, albums, and tracks
- Employees and sales data
- Invoice lines and purchasing history

Source: [Chinook Database](https://github.com/lerocha/chinook-database)

## Project Structure

```
legacy-bridge-sql-ai/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server implementation
│   ├── database.py        # Database connection and query execution
│   └── schema.py          # Schema inspection utilities
├── tests/
│   ├── __init__.py
│   └── test_server.py     # Unit tests
├── data/
│   └── chinook.db         # Chinook SQLite database
├── pyproject.toml         # Project configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation

1. **Clone or navigate to the repository**

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download the Chinook database**
   - See Step 2 in the implementation guide

## Usage

### Option 1: Command Line Interface (CLI)

Test queries directly from your terminal with raw SQL:

```bash
# Interactive mode - query the database directly
python -m src.cli query "SELECT * FROM Artist LIMIT 5"

# Show database schema
python -m src.cli schema

# List all tables
python -m src.cli tables
```

### Option 2: AI-Powered API Mode (No Claude Desktop Required)

Use natural language queries with the Anthropic API:

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Interactive chat mode
python -m src.server_api

# Single query mode
python -m src.server_api "Show me all artists"
python -m src.server_api "What are the top 5 customers by total purchases?"
```

**Get API Key:** https://console.anthropic.com/

### Option 3: MCP Server Mode (Claude Desktop Integration)

Run as an MCP server for integration with Claude Desktop or other MCP clients:

```bash
python -m src.server
```

### Available MCP Resources

- `schema://tables` - List all database tables
- `schema://table/{table_name}` - Get schema for a specific table

### Available MCP Tools

- `query_database` - Execute read-only SQL queries
  - Parameters: `sql` (string) - The SQL query to execute
  - Returns: Query results as JSON

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Test connection pooling performance
python tests/test_connection_pool.py
```

### Code Formatting

```bash
black src/ tests/
ruff check src/ tests/
```

## Integration with Claude Desktop

### Step 1: Locate Your Project Path

```bash
pwd
# Example: /Users/username/Documents/LegacyBridge-SQL-AI
```

### Step 2: Find Your Python Virtual Environment

```bash
which python3
# Should show: /path/to/LegacyBridge-SQL-AI/venv/bin/python3
```

### Step 3: Create/Edit Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "legacy-bridge": {
      "command": "/full/path/to/your/venv/bin/python3",
      "args": [
        "/full/path/to/your/project/run_server.py"
      ]
    }
  }
}
```

**Example:**
```json
{
  "mcpServers": {
    "legacy-bridge": {
      "command": "/Users/username/Documents/LegacyBridge-SQL-AI/venv/bin/python3",
      "args": [
        "/Users/username/Documents/LegacyBridge-SQL-AI/run_server.py"
      ]
    }
  }
}
```

### Step 4: Restart Claude Desktop

Completely quit (Cmd+Q) and reopen Claude Desktop.

### Troubleshooting

#### Server Shows "Disconnected" or "Failed"

**Check the logs:**
```bash
tail -f ~/Library/Logs/Claude/mcp-server-legacy-bridge.log
```

**Common Issues:**

1. **"No such file or directory"**
   - ❌ Problem: Using `python` instead of full path
   - ✅ Solution: Use full path to `venv/bin/python3`

2. **"ModuleNotFoundError: No module named 'src'"**
   - ❌ Problem: Python can't find the project modules
   - ✅ Solution: Use `run_server.py` wrapper (not `-m src.server`)

3. **"Failed to spawn process"**
   - ❌ Problem: Incorrect path to Python or script
   - ✅ Solution: Verify paths with `which python3` and `pwd`

**Test the server manually:**
```bash
cd /path/to/LegacyBridge-SQL-AI
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | venv/bin/python3 run_server.py
# Should see server logs without errors
```

## Example Queries (Natural Language)

Once integrated with an LLM, you can ask questions like:

- "Show me the top 10 customers by total purchases"
- "Which artists have the most tracks in the database?"
- "What were total sales by country last year?"
- "List all rock albums and their artists"

The LLM will generate appropriate SQL and execute it through the MCP server.

## Performance

### Connection Pooling

The database uses connection pooling for better performance and concurrent access:

- **Default Pool Size**: 5 connections
- **Thread-Safe**: Handles concurrent requests safely
- **WAL Mode**: Automatically enabled for better concurrent reads
- **Configurable**: Adjust pool size based on your workload

For details, see [CONNECTION_POOLING.md](CONNECTION_POOLING.md)

## Production Deployment

For deploying this application in production with Docker/Kubernetes and connecting to external databases (PostgreSQL, MySQL, SQL Server, Oracle), see the comprehensive guide:

**[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)**

Covers:
- Multi-database support (PostgreSQL, MySQL, SQL Server, Oracle)
- Docker containerization and Docker Compose
- Kubernetes deployment with auto-scaling
- Configuration management and secrets
- Security best practices
- Monitoring, logging, and health checks
- Connection pool optimization for production

## Security Notes

- ⚠️ **Read-only mode**: All queries are restricted to SELECT statements
- 🔒 **SQL injection prevention**: Queries are validated before execution
- 📝 **Query logging**: All queries are logged for audit purposes
- 🔑 **API keys**:
  - **MCP Server Mode**: No API key needed (uses Claude Desktop's auth)
  - **API Mode**: Requires Anthropic API key (set via environment variable)

## License

MIT License - feel free to use this for learning and commercial purposes.

## Next Steps

- [x] Connection pooling for better performance
- [ ] Support for multiple database backends (PostgreSQL, MySQL)
- [ ] Query result caching
- [ ] Rate limiting for query execution
- [ ] Advanced schema annotations and business logic
