"""
The Investment Committee - Multi-Agent Stock Analysis System
"""

from .agents import (
    Agent,
    AgentResponse,
    AgentRole,
    BearAgent,
    BullAgent,
    Decision,
    PortfolioDecision,
    PortfolioManagerAgent,
    extract_key_points,
)
from .cache import CacheConfig, FileCache, get_cache
from .config import AppConfig, CacheSettings, LLMConfig
from .tools import FinancialMetrics, format_metrics_for_agent, get_financial_metrics

__version__ = "1.0.0"

__all__ = [
    "Agent",
    "AgentRole",
    "AgentResponse",
    "BullAgent",
    "BearAgent",
    "PortfolioManagerAgent",
    "Decision",
    "PortfolioDecision",
    "FinancialMetrics",
    "get_financial_metrics",
    "format_metrics_for_agent",
    "extract_key_points",
    "LLMConfig",
    "AppConfig",
    "CacheSettings",
    "CacheConfig",
    "FileCache",
    "get_cache",
]
