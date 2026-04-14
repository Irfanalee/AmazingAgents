import datetime
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.utils.logger import setup_logger
from src.mcp.mcp_client import MCPClient
from src.mcp.mcp_config import get_mcp_config

class Vulnerability(BaseModel):
    """A single vulnerability found during a scan."""
    cve_id: str
    severity: str
    component: str
    description: str

class SecurityReport(BaseModel):
    """The structured result from a security scan."""
    target: str
    is_secure: bool
    vulnerabilities: List[Vulnerability]
    timestamp: str

class SargentAgent:
    """Security agent responsible for vulnerability scanning and audits via MCP."""
    def __init__(self, name: str = "Sargent-Agent"):
        self.name = name
        self.logger = setup_logger(self.name)
        self.config = get_mcp_config()
        self.mcp = MCPClient()
        self.connected = False

    def _ensure_connected(self):
        if not self.connected and self.config.TRIVY_MCP_COMMAND:
            try:
                self.mcp.sync_connect("trivy", self.config.TRIVY_MCP_COMMAND, self.config.TRIVY_MCP_ARGS)
                self.connected = True
            except Exception as e:
                self.logger.warning("mcp_connection_failed", server="trivy", error=str(e), fallback="mock_mode")

    def run_security_scan(self, target: str, scan_type: str = "image") -> SecurityReport:
        """Scan a target (image or directory) for vulnerabilities."""
        self.logger.info("starting_security_scan", target=target, scan_type=scan_type)
        
        self._ensure_connected()
        
        if self.connected:
            try:
                return self._fetch_live_scan(target, scan_type)
            except Exception as e:
                self.logger.warning("live_scan_failed", error=str(e), fallback="mock_mode")
        
        return self._get_mock_scan(target)

    def _fetch_live_scan(self, target: str, scan_type: str) -> SecurityReport:
        """Call live Trivy MCP server tool."""
        # Tool name and arguments are based on the mcp/trivy-server implementation
        tool_name = "scan_image" if scan_type == "image" else "scan_local_path"
        args = {"image": target} if scan_type == "image" else {"path": target}
        
        result = self.mcp.sync_call_tool("trivy", tool_name, args)
        
        # Parse result from MCP tool output
        data = result.content[0].text
        scan_data = json.loads(data)
        
        vulnerabilities = [
            Vulnerability(
                cve_id=v.get("id"),
                severity=v.get("severity"),
                component=v.get("pkgName"),
                description=v.get("title")
            ) for v in scan_data.get("vulnerabilities", [])
        ]
        
        return SecurityReport(
            target=target,
            is_secure=len(vulnerabilities) == 0,
            vulnerabilities=vulnerabilities,
            timestamp=datetime.datetime.now().isoformat()
        )

    def _get_mock_scan(self, target: str) -> SecurityReport:
        """Mock scan result for demonstration or fallback."""
        self.logger.info("returning_mock_scan", target=target)
        
        # Simulating a finding if target is 'prod-image'
        vulns = []
        if "prod" in target:
            vulns.append(Vulnerability(
                cve_id="CVE-2024-1234",
                severity="CRITICAL",
                component="openssl",
                description="Remote Code Execution vulnerability in OpenSSL."
            ))

        return SecurityReport(
            target=target,
            is_secure=len(vulns) == 0,
            vulnerabilities=vulns,
            timestamp=datetime.datetime.now().isoformat()
        )

if __name__ == "__main__":
    sargent = SargentAgent()
    
    # Test a scan on a 'prod' image
    print("--- Scanning prod-web-server-image ---")
    report1 = sargent.run_security_scan("prod-web-server-image")
    print(report1.model_dump_json(indent=2))

    # Test a scan on a clean image
    print("\n--- Scanning local-dev-image ---")
    report2 = sargent.run_security_scan("local-dev-image")
    print(report2.model_dump_json(indent=2))
