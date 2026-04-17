# How-To: Connecting MCP Servers

The **MCP-DevOps-Squad** relies on external Model Context Protocol (MCP) servers to interact with your infrastructure (Docker, Kubernetes, GitHub, etc.). This guide explains how to configure and connect these servers.

## Prerequisites

1.  **Docker:** Ensure Docker is installed and running on your host machine.
2.  **MCP Python SDK:** Installed in your virtual environment (included in `requirements.txt`).

## Configured MCP Servers

The squad currently supports the following MCP servers via the `stdio` transport. These servers are typically launched as Docker containers.

### 1. Docker MCP Server (Monitor-Agent)
Provides container metrics, status, and control.
- **Default Image:** `mcp/docker-server`
- **Configuration:** `DOCKER_MCP_COMMAND` and `DOCKER_MCP_ARGS` in `MCPSettings`.

### 2. Trivy MCP Server (Sargent-Agent)
Provides vulnerability scanning for images and local paths.
- **Default Image:** `mcp/trivy-server`
- **Configuration:** `TRIVY_MCP_COMMAND` and `TRIVY_MCP_ARGS`.
- **Note:** Requires mounting the Docker socket (`/var/run/docker.sock`) to scan local images.

### 3. Filesystem & GitHub MCP Servers (Debugger-Agent)
Used for deep analysis of logs and source code.
- **Filesystem Image:** `mcp/filesystem-server`
- **GitHub Image:** `mcp/github-server`
- **Configuration:** `GITHUB_MCP_COMMAND`, `GITHUB_MCP_ARGS`, `FILESYSTEM_MCP_COMMAND`, `FILESYSTEM_MCP_ARGS`.
- **Note:** `GITHUB_TOKEN` is required for repository access.

### 4. Shell/CLI MCP Server (Janitor-Agent)
Used to execute remediation commands.
- **Default Image:** `mcp/shell-server`
- **Configuration:** `SHELL_MCP_COMMAND`, `SHELL_MCP_ARGS`.

## How to Customize Connections

You can override the default connection settings using environment variables or a `.env` file in the project root.

### Example `.env` File

```env
# Custom Docker MCP settings
DOCKER_MCP_COMMAND=docker
DOCKER_MCP_ARGS='["run", "-i", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "my-custom/docker-mcp-server"]'

# Sargent Security Settings
TRIVY_MCP_COMMAND=docker
TRIVY_MCP_ARGS='["run", "-i", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "mcp/trivy-server"]'

# Credentials
GITHUB_TOKEN=your_github_personal_access_token
```

## Running a Standalone Test

Each agent can be run standalone to verify its MCP connection and fallback logic.

```bash
# Test Monitor Agent
export PYTHONPATH=$PYTHONPATH:$(pwd)
venv/bin/python src/agents/monitor.py

# Test Sargent Agent
venv/bin/python src/agents/sargent.py
```

If an MCP server is not running or unreachable, the agents will log a `mcp_connection_failed` warning and fallback to **Mock Mode**, allowing you to test the orchestration logic without a full infrastructure setup.
