from typing import Dict, Any
from pydantic import BaseModel
from src.utils.logger import setup_logger

class MetricUpdate(BaseModel):
    """Structured metric data for A2A hand-offs."""
    resource_id: str
    cpu_percent: float
    memory_percent: float
    status: str
    timestamp: str

class MonitorAgent:
    """Agent responsible for streaming metrics from Docker/K8s via MCP (Mocked)."""
    def __init__(self, name: str = "Monitor-Agent"):
        self.name = name
        self.logger = setup_logger(self.name)

    def get_metrics(self, resource_id: str) -> MetricUpdate:
        """Fetch metrics for a specific resource using Mocked MCP logic."""
        self.logger.info("fetching_metrics", resource_id=resource_id)
        
        # MOCK LOGIC (Option A): Simulating a CPU spike for demonstration
        import datetime
        mock_data = MetricUpdate(
            resource_id=resource_id,
            cpu_percent=88.5, # Above 80% threshold
            memory_percent=45.2,
            status="running",
            timestamp=datetime.datetime.now().isoformat()
        )
        
        self.logger.info("metrics_received", 
                         resource_id=resource_id, 
                         cpu=mock_data.cpu_percent, 
                         mem=mock_data.memory_percent)
        return mock_data

if __name__ == "__main__":
    monitor = MonitorAgent()
    metrics = monitor.get_metrics("prod-web-server-01")
    print(metrics.model_dump_json(indent=2))
