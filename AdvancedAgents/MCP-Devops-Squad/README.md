# MCP-DevOps-Squad

A production-ready Multi-Agent SRE System powered by the Model Context Protocol (MCP) and Google A2A patterns.

## Features
- **Lead-SRE**: Central orchestrator for task delegation.
- **Monitor-Agent**: Metrics and health monitoring (Docker/K8s).
- **Debugger-Agent**: Code and log analysis.
- **Janitor-Agent**: System fixes and cleanup (Human-in-the-loop enabled).

## Setup

1. **Environment Variables**:
   Create a `.env` file with the following:
   ```env
   DOCKER_MCP_URI=http://localhost:port
   GITHUB_MCP_URI=http://localhost:port
   FILESYSTEM_MCP_URI=http://localhost:port
   GITHUB_TOKEN=your_token
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Register MCP Servers**:
   Follow the documentation of the specific MCP servers (e.g., Docker, GitHub) to ensure they are running at the URIs specified in your `.env`.

## Usage
Run the Lead-SRE orchestrator:
```bash
python src/orchestrator/lead_sre.py
```
