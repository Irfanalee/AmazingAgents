from typing import Dict, Any, Optional
from pydantic import BaseModel
from src.utils.logger import setup_logger
from src.mcp.mcp_client import MCPClient
from src.mcp.mcp_config import get_mcp_config

class DebuggerAgent:
    """Agent responsible for analyzing code and logs via MCP."""
    def __init__(self, name: str = "Debugger-Agent"):
        self.name = name
        self.logger = setup_logger(self.name)
        self.config = get_mcp_config()
        self.mcp = MCPClient()
        self.fs_connected = False
        self.github_connected = False

    def _ensure_fs_connected(self):
        if not self.fs_connected and self.config.FILESYSTEM_MCP_COMMAND:
            try:
                self.mcp.sync_connect("filesystem", self.config.FILESYSTEM_MCP_COMMAND, self.config.FILESYSTEM_MCP_ARGS)
                self.fs_connected = True
            except Exception as e:
                self.logger.warning("mcp_connection_failed", server="filesystem", error=str(e), fallback="mock_mode")

    def _ensure_github_connected(self):
        if not self.github_connected and self.config.GITHUB_MCP_COMMAND:
            try:
                self.mcp.sync_connect("github", self.config.GITHUB_MCP_COMMAND, self.config.GITHUB_MCP_ARGS)
                self.github_connected = True
            except Exception as e:
                self.logger.warning("mcp_connection_failed", server="github", error=str(e), fallback="mock_mode")

    def analyze_logs(self, log_path: str) -> Dict[str, Any]:
        """Analyze log file for errors via Filesystem MCP."""
        self.logger.info("analyzing_logs", path=log_path)
        self._ensure_fs_connected()

        if self.fs_connected:
            try:
                return self._fetch_live_logs(log_path)
            except Exception as e:
                self.logger.warning("live_log_analysis_failed", error=str(e), fallback="mock_mode")
        
        return self._mock_analyze_logs(log_path)

    def analyze_code(self, repo: str, file_path: str) -> Dict[str, Any]:
        """Analyze source code for bugs via GitHub MCP."""
        self.logger.info("analyzing_code", repo=repo, path=file_path)
        self._ensure_github_connected()

        if self.github_connected:
            try:
                return self._fetch_live_code(repo, file_path)
            except Exception as e:
                self.logger.warning("live_code_analysis_failed", error=str(e), fallback="mock_mode")
        
        return self._mock_analyze_code(repo, file_path)

    def _fetch_live_logs(self, log_path: str) -> Dict[str, Any]:
        """Call live Filesystem MCP server tool."""
        result = self.mcp.sync_call_tool("filesystem", "read_file", {"path": log_path})
        content = result.content[0].text
        
        if "ERROR" in content or "Exception" in content:
            return {"status": "error_found", "details": f"Detected errors in {log_path}"}
        return {"status": "clean"}

    def _fetch_live_code(self, repo: str, file_path: str) -> Dict[str, Any]:
        """Call live GitHub MCP server tool."""
        # Assuming github MCP has 'get_file_content'
        result = self.mcp.sync_call_tool("github", "get_file_content", {"repo": repo, "path": file_path})
        content = result.content[0].text
        
        # Simple heuristic for demonstration
        if "FIXME" in content or "TODO" in content:
            return {"status": "potential_bug", "details": f"Found FIXME/TODO in {file_path}"}
        return {"status": "clean"}

    def _mock_analyze_logs(self, log_path: str) -> Dict[str, Any]:
        """Mock log analysis for demonstration."""
        self.logger.info("returning_mock_log_analysis", path=log_path)
        return {"status": "error_found", "details": "Found ERROR in mocked logs: Out of memory in service A"}

    def _mock_analyze_code(self, repo: str, file_path: str) -> Dict[str, Any]:
        """Mock code analysis for demonstration."""
        self.logger.info("returning_mock_code_analysis", repo=repo, path=file_path)
        return {"status": "potential_bug", "details": "Found a potential memory leak in mocked code."}

if __name__ == "__main__":
    debugger = DebuggerAgent()
    
    print("--- Log Analysis ---")
    res1 = debugger.analyze_logs("/var/log/syslog")
    print(res1)

    print("\n--- Code Analysis ---")
    res2 = debugger.analyze_code("org/repo", "src/main.py")
    print(res2)
