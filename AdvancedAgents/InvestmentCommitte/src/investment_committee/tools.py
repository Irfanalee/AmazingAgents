"""
Data Layer: Financial data fetching using yfinance with caching support.
"""

import os
import sys
from contextlib import contextmanager
from datetime import datetime

import yfinance as yf
from pydantic import BaseModel, Field

from .cache import get_cache


@contextmanager
def suppress_stderr():
    """Temporarily suppress stderr output from yfinance"""
    stderr = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = stderr


class FinancialMetrics(BaseModel):
    """Structured financial data for a stock ticker"""

    ticker: str
    current_price: float | None = None
    pe_ratio: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None
    market_cap: float | None = None
    volume: int | None = None
    avg_volume: int | None = None
    news_headlines: list[str] = Field(default_factory=list)
    fetch_timestamp: datetime = Field(default_factory=datetime.now)
    error: str | None = None
    from_cache: bool = False  # Indicates if data was loaded from cache


def get_financial_metrics(
    ticker: str, use_cache: bool = True, cache_ttl_hours: int | None = None
) -> FinancialMetrics:
    """
    Fetch comprehensive financial metrics for a given stock ticker.

    Uses file-based caching to reduce API calls. Cached data is used if:
    - Cache is enabled (use_cache=True)
    - Valid cached data exists and hasn't expired

    Args:
        ticker: Stock ticker symbol (e.g., "NVDA", "AAPL", "SAAB-B.ST")
        use_cache: Whether to use cached data if available (default: True)
        cache_ttl_hours: Custom TTL for this request (default: uses cache config)

    Returns:
        FinancialMetrics object with all available data
    """
    cache = get_cache()
    cache_key = ticker.upper()

    # Try to get from cache first
    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            # Reconstruct FinancialMetrics from cached dict
            cached_data["from_cache"] = True
            # Parse the timestamp back to datetime
            if "fetch_timestamp" in cached_data:
                cached_data["fetch_timestamp"] = datetime.fromisoformat(
                    cached_data["fetch_timestamp"]
                )
            return FinancialMetrics(**cached_data)

    # Cache miss or disabled - fetch from yfinance
    try:
        # Auto-correct common international ticker formats
        # Swedish stocks (e.g., SAAB-B -> SAAB-B.ST)
        if "-" in ticker and "." not in ticker:
            ticker_variants = [ticker, f"{ticker}.ST"]
        else:
            ticker_variants = [ticker]

        # Try each variant (suppress yfinance error output)
        stock = None
        working_ticker = ticker

        with suppress_stderr():
            for variant in ticker_variants:
                try:
                    test_stock = yf.Ticker(variant)
                    test_info = test_stock.info
                    # Check if we got valid data
                    if test_info.get("currentPrice") or test_info.get("regularMarketPrice"):
                        stock = test_stock
                        working_ticker = variant
                        break
                except Exception:
                    continue

            if stock is None:
                stock = yf.Ticker(ticker)
                working_ticker = ticker

            info = stock.info

        # Validate that we got actual stock data
        if not info or (not info.get("currentPrice") and not info.get("regularMarketPrice")):
            return FinancialMetrics(
                ticker=working_ticker.upper(),
                error=f"Ticker '{working_ticker}' not found. Please verify the symbol is correct.",
            )

        # Fetch recent news (last 5 headlines)
        news = stock.news[:5] if hasattr(stock, "news") and stock.news else []
        headlines = []
        for article in news:
            # Try different paths for title (yfinance API structure varies)
            title = (
                article.get("title")
                or article.get("content", {}).get("title")
                or "No title available"
            )
            headlines.append(title)

        # Extract key metrics with safe fallbacks
        metrics = FinancialMetrics(
            ticker=working_ticker.upper(),
            current_price=info.get("currentPrice") or info.get("regularMarketPrice"),
            pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
            week_52_high=info.get("fiftyTwoWeekHigh"),
            week_52_low=info.get("fiftyTwoWeekLow"),
            market_cap=info.get("marketCap"),
            volume=info.get("volume"),
            avg_volume=info.get("averageVolume"),
            news_headlines=headlines if headlines else ["No recent news available"],
            from_cache=False,
        )

        # Store in cache (only successful fetches, not errors)
        if use_cache and not metrics.error:
            cache_data = metrics.model_dump()
            # Convert datetime to ISO format for JSON serialization
            cache_data["fetch_timestamp"] = metrics.fetch_timestamp.isoformat()
            cache.set(cache_key, cache_data, ttl_hours=cache_ttl_hours)

        return metrics

    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if "404" in error_msg or "Not Found" in error_msg:
            return FinancialMetrics(
                ticker=ticker.upper(),
                error=f"Ticker '{ticker}' not found. Please check the symbol and try again.",
            )
        else:
            return FinancialMetrics(
                ticker=ticker.upper(), error=f"Failed to fetch data: {error_msg}"
            )


def _format_market_cap(market_cap: float | None) -> str:
    """Format market cap in human-readable form (B/T)"""
    if not market_cap:
        return "N/A"
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.1f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.1f}M"
    return f"${market_cap:,.0f}"


def _format_volume(volume: int | None) -> str:
    """Format volume in human-readable form (K/M)"""
    if not volume:
        return "N/A"
    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.1f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.1f}K"
    return f"{volume:,}"


def format_metrics_for_agent(metrics: FinancialMetrics, compressed: bool = True) -> str:
    """
    Format financial metrics into a text block for LLM consumption.

    Args:
        metrics: FinancialMetrics object
        compressed: If True, use compact format (~50% fewer tokens)

    Returns:
        Formatted string with all relevant data
    """
    if metrics.error:
        return f"ERROR: {metrics.error}"

    if compressed:
        # Compressed format: ~250 tokens vs ~500 tokens
        price = f"${metrics.current_price:.2f}" if metrics.current_price else "N/A"
        pe = f"{metrics.pe_ratio:.1f}" if metrics.pe_ratio else "N/A"
        mcap = _format_market_cap(metrics.market_cap)
        high = f"${metrics.week_52_high:.2f}" if metrics.week_52_high else "N/A"
        low = f"${metrics.week_52_low:.2f}" if metrics.week_52_low else "N/A"
        vol = _format_volume(metrics.volume)
        avg_vol = _format_volume(metrics.avg_volume)

        output = f"""{metrics.ticker} | Price: {price} | P/E: {pe} | MCap: {mcap}
52-Week Range: {low} - {high} | Volume: {vol} (avg: {avg_vol})
News: """

        # Compact news (first 3 headlines, truncated)
        news_items = []
        for i, headline in enumerate(metrics.news_headlines[:3], 1):
            # Truncate long headlines
            truncated = headline[:80] + "..." if len(headline) > 80 else headline
            news_items.append(f"({i}) {truncated}")
        output += " ".join(news_items)

        return output

    # Original verbose format (kept for backwards compatibility)
    output = f"""
FINANCIAL DATA FOR {metrics.ticker}
{"=" * 50}

PRICE METRICS:
- Current Price: ${metrics.current_price:.2f} if metrics.current_price else 'N/A'
- 52-Week High: ${metrics.week_52_high:.2f} if metrics.week_52_high else 'N/A'
- 52-Week Low: ${metrics.week_52_low:.2f} if metrics.week_52_low else 'N/A'

VALUATION:
- P/E Ratio: {f"{metrics.pe_ratio:.2f}" if metrics.pe_ratio else "N/A"}
- Market Cap: ${metrics.market_cap:,.0f} if metrics.market_cap else 'N/A'

VOLUME:
- Current Volume: {f"{metrics.volume:,}" if metrics.volume else "N/A"}
- Average Volume: {f"{metrics.avg_volume:,}" if metrics.avg_volume else "N/A"}

RECENT NEWS HEADLINES:
"""

    for i, headline in enumerate(metrics.news_headlines, 1):
        output += f"{i}. {headline}\n"

    output += f"\nData fetched at: {metrics.fetch_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    return output
