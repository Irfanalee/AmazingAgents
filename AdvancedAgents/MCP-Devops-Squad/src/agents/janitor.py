import logging
import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.utils.logger import setup_logger
from src.mcp.mcp_client import MCPClient
from src.mcp.mcp_config import get_mcp_config

class CommandRequest(BaseModel):
    command: str
    justification: str
    resource_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidatorAgent:
    """Agent that performs automated safety checks before HITL."""
    def __init__(self, name: str = "Validator-Agent"):
        self.name = name
        self.blocked_patterns = ["rm -rf /", "chmod 777", "sudo"]

    def validate(self, request: CommandRequest) -> Dict[str, Any]:
        """Check if a command violates basic safety rules."""
        for pattern in self.blocked_patterns:
            if pattern in request.command:
                return {"approved": False, "reason": f"Security violation: {pattern} is blocked."}
        
        # Simple heuristic: if it's a 'kill' or 'rm' command, it's flagged as sensitive
        is_sensitive = any(op in request.command.lower() for op in ["rm", "kill", "delete", "stop"])
        return {"approved": True, "is_sensitive": is_sensitive}

class JanitorAgent:
    """Agent responsible for executing fixes with Validator + HITL safety."""
    def __init__(self, name: str = "Janitor-Agent"):
        self.name = name
        self.logger = setup_logger(self.name)
        self.validator = ValidatorAgent()
        self.approval_file = "config/pending_approvals.json"
        self.config = get_mcp_config()
        self.mcp = MCPClient()
        self.connected = False
        self._ensure_approval_store()

    def _ensure_approval_store(self):
        if not os.path.exists("config"):
            os.makedirs("config")
        if not os.path.exists(self.approval_file):
            with open(self.approval_file, "w") as f:
                json.dump([], f)

    def _ensure_connected(self):
        if not self.connected and self.config.SHELL_MCP_COMMAND:
            try:
                self.mcp.sync_connect("shell", self.config.SHELL_MCP_COMMAND, self.config.SHELL_MCP_ARGS)
                self.connected = True
            except Exception as e:
                self.logger.warning("mcp_connection_failed", server="shell", error=str(e), fallback="mock_mode")

    def request_execution(self, command: str, justification: str, resource_id: str):
        request = CommandRequest(command=command, justification=justification, resource_id=resource_id)
        
        # Step 1: Automated Validation
        validation_result = self.validator.validate(request)
        if not validation_result["approved"]:
            return {"status": "rejected", "reason": validation_result["reason"]}

        # Step 2: HITL for Sensitive Commands
        if validation_result.get("is_sensitive"):
            self._stage_for_approval(request)
            return {
                "status": "pending_hitl",
                "message": f"Command '{command}' staged for manual approval in {self.approval_file}"
            }

        # Step 3: Direct Execution (for safe commands)
        return self.execute_approved_command(request.command)

    def _stage_for_approval(self, request: CommandRequest):
        """Write the request to the pending approvals file for HITL."""
        with open(self.approval_file, "r") as f:
            approvals = json.load(f)
        
        approvals.append(request.model_dump())
        
        with open(self.approval_file, "w") as f:
            json.dump(approvals, f, indent=2)

    def execute_approved_command(self, command: str):
        """Execute command via Shell MCP server. Public method for HITL CLI."""
        self.logger.info("executing_approved_command", command=command)
        self._ensure_connected()
        
        if self.connected:
            try:
                result = self.mcp.sync_call_tool("shell", "execute_command", {"command": command})
                # Handle list of content blocks
                output = result.content[0].text if hasattr(result, "content") and result.content else str(result)
                self.logger.info("remediation_success", command=command)
                return {"status": "success", "executed_command": command, "output": output}
            except Exception as e:
                self.logger.error("remediation_failed", command=command, error=str(e))
                return {"status": "error", "executed_command": command, "error": str(e)}
        
        return {"status": "success", "executed_command": command, "note": "Mock execution (MCP not connected)"}

if __name__ == "__main__":
    janitor = JanitorAgent()
    
    # Test a sensitive command (triggers HITL)
    print("--- Sensitive Command ---")
    res1 = janitor.request_execution("rm -rf /tmp/stale-logs", "Cleanup", "server-01")
    print(res1)

    # Test a safe command (executed directly via MCP/Mock)
    print("\n--- Safe Command ---")
    res3 = janitor.request_execution("ls -la", "Audit check", "server-01")
    print(res3)
