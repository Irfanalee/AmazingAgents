import logging
import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

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
        self.validator = ValidatorAgent()
        self.approval_file = "config/pending_approvals.json"
        self._ensure_approval_store()

    def _ensure_approval_store(self):
        if not os.path.exists("config"):
            os.makedirs("config")
        if not os.path.exists(self.approval_file):
            with open(self.approval_file, "w") as f:
                json.dump([], f)

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
        return self._execute_mcp_command(request.command)

    def _stage_for_approval(self, request: CommandRequest):
        """Write the request to the pending approvals file for HITL."""
        with open(self.approval_file, "r") as f:
            approvals = json.load(f)
        
        approvals.append(request.model_dump())
        
        with open(self.approval_file, "w") as f:
            json.dump(approvals, f, indent=2)

    def _execute_mcp_command(self, command: str):
        """Simulated MCP Shell execution."""
        return {"status": "success", "executed_command": command}

if __name__ == "__main__":
    janitor = JanitorAgent()
    
    # Test a sensitive command (triggers HITL)
    print("--- Sensitive Command ---")
    res1 = janitor.request_execution("rm -rf /tmp/stale-logs", "Cleanup", "server-01")
    print(res1)

    # Test a blocked command (rejected by Validator)
    print("\n--- Blocked Command ---")
    res2 = janitor.request_execution("rm -rf /", "Total Destruction", "server-01")
    print(res2)

    # Test a safe command (executed directly)
    print("\n--- Safe Command ---")
    res3 = janitor.request_execution("ls -la", "Audit check", "server-01")
    print(res3)
