import logging
from pydantic import BaseModel
from typing import Optional

class JanitorAgent:
    """Agent responsible for executing fixes with human-in-the-loop safety."""
    def __init__(self, name: str = "Janitor-Agent", require_approval: bool = True):
        self.name = name
        self.require_approval = require_approval
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def execute_command(self, command: str, justification: str):
        """Execute a shell command via MCP, checking for approval if destructive."""
        destructive_ops = ["rm", "kill", "delete", "stop", "terminate"]
        is_destructive = any(op in command.lower() for op in destructive_ops)

        if is_destructive and self.require_approval:
            self.logger.warning(f"WAITING FOR APPROVAL: Action '{command}' is destructive. Justification: {justification}")
            # Placeholder for human approval check (e.g., Slack, CLI prompt, or Validator agent)
            # For now, we simulate a 'denied' response unless explicitly overridden.
            return {"status": "pending_approval", "message": "Command requires human-in-the-loop sign-off."}

        self.logger.info(f"Executing: {command}")
        # Placeholder for MCP Shell execution
        return {"status": "success", "command": command}

if __name__ == "__main__":
    janitor = JanitorAgent()
    result = janitor.execute_command("rm -rf /tmp/stale-logs", "Cleanup stale logs to free up space.")
    print(result)
    
    # Safe command
    safe_result = janitor.execute_command("ls -la /tmp", "Checking directory content.")
    print(safe_result)
