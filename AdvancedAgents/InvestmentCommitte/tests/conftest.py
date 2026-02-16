"""Shared test fixtures for Investment Committee tests"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def sample_financial_metrics():
    """Create a sample FinancialMetrics object for testing"""
    from src.investment_committee import FinancialMetrics

    return FinancialMetrics(
        ticker="AAPL",
        current_price=185.50,
        pe_ratio=28.5,
        week_52_high=199.62,
        week_52_low=143.90,
        market_cap=2850000000000,
        volume=55000000,
        avg_volume=60000000,
        news_headlines=[
            "Apple announces new iPhone",
            "Apple stock hits new high",
            "Apple earnings beat expectations",
        ],
        fetch_timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def sample_metrics_with_error():
    """Create a FinancialMetrics object with an error"""
    from src.investment_committee import FinancialMetrics

    return FinancialMetrics(
        ticker="INVALID",
        error="Ticker 'INVALID' not found. Please verify the symbol is correct.",
    )


@pytest.fixture
def mock_env_anthropic(monkeypatch):
    """Set up environment for Anthropic provider"""
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")


@pytest.fixture
def mock_env_openai(monkeypatch):
    """Set up environment for OpenAI provider"""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4-turbo-preview")


@pytest.fixture
def mock_yfinance_response():
    """Create a mock yfinance Ticker response"""
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "currentPrice": 185.50,
        "regularMarketPrice": 185.50,
        "trailingPE": 28.5,
        "fiftyTwoWeekHigh": 199.62,
        "fiftyTwoWeekLow": 143.90,
        "marketCap": 2850000000000,
        "volume": 55000000,
        "averageVolume": 60000000,
    }
    mock_ticker.news = [
        {"title": "Apple announces new iPhone"},
        {"title": "Apple stock hits new high"},
    ]
    return mock_ticker
