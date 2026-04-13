import structlog
import os
import sys
from datetime import datetime

def setup_logger(module_name: str):
    """Configures structlog for JSON logging to /logs/ and colored output to console."""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if sys.stderr.isatty() else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20), # INFO level
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger(module_name)

if __name__ == "__main__":
    log = setup_logger("test-module")
    log.info("logging_initialized", status="success", squad="MCP-DevOps")
