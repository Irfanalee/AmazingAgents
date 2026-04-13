import logging
from pydantic import BaseModel

class DebuggerAgent:
    """Agent responsible for analyzing code and logs via MCP."""
    def __init__(self, name: str = "Debugger-Agent"):
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def analyze_logs(self, log_content: str):
        """Analyze log content for errors."""
        self.logger.info("Analyzing logs...")
        # Simple analysis logic or LLM call via A2A
        if "ERROR" in log_content:
            return {"status": "error_found", "details": "Found ERROR in logs."}
        return {"status": "clean"}

if __name__ == "__main__":
    debugger = DebuggerAgent()
    result = debugger.analyze_logs("2026-04-13 ERROR: Out of memory in service A")
    print(result)
