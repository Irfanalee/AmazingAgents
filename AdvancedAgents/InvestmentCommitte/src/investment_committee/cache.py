"""
File-based caching for financial data with TTL support.

This module provides a simple file-based cache to reduce redundant API calls
to yfinance and improve response times for repeated ticker queries.
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class CacheConfig(BaseModel):
    """Cache configuration settings"""

    enabled: bool = True
    cache_dir: str = ".cache/investment_committee"
    default_ttl_hours: int = 24  # Default: cache for 24 hours
    max_entries: int = 1000  # Maximum cached entries before cleanup


class CacheEntry(BaseModel):
    """A single cache entry with metadata"""

    key: str
    data: dict[str, Any]
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        """Check if this entry has expired"""
        return datetime.now() > self.expires_at


class FileCache:
    """
    File-based cache with TTL support.

    Stores cached data as JSON files in a configurable directory.
    Each ticker gets its own file for easy management.
    """

    def __init__(self, config: CacheConfig | None = None):
        """
        Initialize the cache.

        Args:
            config: Cache configuration. Uses defaults if not provided.
        """
        self.config = config or CacheConfig()
        self._cache_path = Path(self.config.cache_dir)

        if self.config.enabled:
            self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist"""
        self._cache_path.mkdir(parents=True, exist_ok=True)

    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a given key"""
        # Use hash for safe filenames
        safe_key = hashlib.md5(key.lower().encode()).hexdigest()[:16]
        return self._cache_path / f"{key.upper()}_{safe_key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        """
        Retrieve a cached value if it exists and hasn't expired.

        Args:
            key: The cache key (typically a ticker symbol)

        Returns:
            Cached data dict or None if not found/expired
        """
        if not self.config.enabled:
            return None

        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                entry_data = json.load(f)

            entry = CacheEntry(
                key=entry_data["key"],
                data=entry_data["data"],
                created_at=datetime.fromisoformat(entry_data["created_at"]),
                expires_at=datetime.fromisoformat(entry_data["expires_at"]),
            )

            if entry.is_expired():
                # Clean up expired entry
                cache_file.unlink(missing_ok=True)
                return None

            return entry.data

        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache file, remove it
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict[str, Any], ttl_hours: int | None = None) -> None:
        """
        Store a value in the cache.

        Args:
            key: The cache key (typically a ticker symbol)
            data: The data to cache (must be JSON-serializable)
            ttl_hours: Time-to-live in hours. Uses default if not specified.
        """
        if not self.config.enabled:
            return

        ttl = ttl_hours if ttl_hours is not None else self.config.default_ttl_hours
        now = datetime.now()

        entry = CacheEntry(
            key=key.upper(), data=data, created_at=now, expires_at=now + timedelta(hours=ttl)
        )

        cache_file = self._get_cache_file(key)

        try:
            with open(cache_file, "w") as f:
                json.dump(
                    {
                        "key": entry.key,
                        "data": entry.data,
                        "created_at": entry.created_at.isoformat(),
                        "expires_at": entry.expires_at.isoformat(),
                    },
                    f,
                    indent=2,
                    default=str,
                )
        except (OSError, TypeError) as e:
            # Log error but don't fail the operation
            print(f"Warning: Failed to cache data for {key}: {e}")

    def delete(self, key: str) -> bool:
        """
        Remove a specific entry from the cache.

        Args:
            key: The cache key to remove

        Returns:
            True if entry was deleted, False if it didn't exist
        """
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def clear(self) -> int:
        """
        Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        if not self._cache_path.exists():
            return 0

        count = 0
        for cache_file in self._cache_path.glob("*.json"):
            cache_file.unlink()
            count += 1

        return count

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.

        Returns:
            Number of expired entries removed
        """
        if not self._cache_path.exists():
            return 0

        count = 0
        for cache_file in self._cache_path.glob("*.json"):
            try:
                with open(cache_file) as f:
                    entry_data = json.load(f)

                expires_at = datetime.fromisoformat(entry_data["expires_at"])
                if datetime.now() > expires_at:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted file, remove it
                cache_file.unlink()
                count += 1

        return count

    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats (entries, size, etc.)
        """
        if not self._cache_path.exists():
            return {"entries": 0, "size_bytes": 0, "expired": 0}

        entries = 0
        expired = 0
        size_bytes = 0

        for cache_file in self._cache_path.glob("*.json"):
            entries += 1
            size_bytes += cache_file.stat().st_size

            try:
                with open(cache_file) as f:
                    entry_data = json.load(f)
                expires_at = datetime.fromisoformat(entry_data["expires_at"])
                if datetime.now() > expires_at:
                    expired += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                expired += 1

        return {
            "entries": entries,
            "size_bytes": size_bytes,
            "size_readable": f"{size_bytes / 1024:.1f} KB",
            "expired": expired,
            "valid": entries - expired,
        }


# Global cache instance (lazy-loaded)
_cache_instance: FileCache | None = None


def get_cache(config: CacheConfig | None = None) -> FileCache:
    """
    Get or create the global cache instance.

    Args:
        config: Optional config to use when creating the cache

    Returns:
        FileCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = FileCache(config)
    return _cache_instance
