import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
from src.utils.logger import setup_logger
from src.mcp.mcp_client import MCPClient
from src.mcp.mcp_config import get_mcp_config

class MetricUpdate(BaseModel):
    """Structured metric data for A2A hand-offs."""
    resource_id: str
    cpu_percent: float
    memory_percent: float
    status: str
    timestamp: str

class MonitorAgent:
    """Agent responsible for streaming metrics from Docker/K8s via MCP."""
    def __init__(self, name: str = "Monitor-Agent"):
        self.name = name
        self.logger = setup_logger(self.name)
        self.config = get_mcp_config()
        self.mcp = MCPClient()
        self.connected = False

    def _ensure_connected(self):
        if not self.connected and self.config.DOCKER_MCP_COMMAND:
            try:
                self.mcp.sync_connect("docker", self.config.DOCKER_MCP_COMMAND, self.config.DOCKER_MCP_ARGS)
                self.connected = True
            except Exception as e:
                self.logger.warning("mcp_connection_failed", error=str(e), fallback="mock_mode")

    def get_metrics(self, resource_id: str) -> MetricUpdate:
        """Fetch metrics for a specific resource using MCP with Mock fallback."""
        self.logger.info("fetching_metrics", resource_id=resource_id)
        
        self._ensure_connected()
        
        if self.connected:
            try:
                return self._fetch_live_metrics(resource_id)
            except Exception as e:
                self.logger.warning("live_metrics_failed", error=str(e), fallback="mock_mode")
        
        return self._get_mock_metrics(resource_id)

    def _fetch_live_metrics(self, resource_id: str) -> MetricUpdate:
        """Call live Docker MCP server tool."""
        # Assuming the docker MCP server has a 'get_container_metrics' tool
        result = self.mcp.sync_call_tool("docker", "get_container_metrics", {"container_id": resource_id})
        
        # Parse result (MCP ToolResult content is usually a list of content blocks)
        # This is a heuristic based on common MCP tool implementations
        data = result.content[0].text
        import json
        metrics_data = json.loads(data)
        
        return MetricUpdate(
            resource_id=resource_id,
            cpu_percent=metrics_data.get("cpu_percent", 0.0),
            memory_percent=metrics_data.get("memory_percent", 0.0),
            status=metrics_data.get("status", "unknown"),
            timestamp=datetime.datetime.now().isoformat()
        )

    def _get_mock_metrics(self, resource_id: str) -> MetricUpdate:
        """Mock logic for demonstration or fallback."""
        mock_data = MetricUpdate(
            resource_id=resource_id,
            cpu_percent=88.5, # Above 80% threshold
            memory_percent=45.2,
            status="running",
            timestamp=datetime.datetime.now().isoformat()
        )
        
        self.logger.info("metrics_received_mock", 
                         resource_id=resource_id, 
                         cpu=mock_data.cpu_percent, 
                         mem=mock_data.memory_percent)
        return mock_data

if __name__ == "__main__":
    monitor = MonitorAgent()
    metrics = monitor.get_metrics("prod-web-server-01")
    print(metrics.model_dump_json(indent=2))
