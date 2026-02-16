"""
Configuration management for The Investment Committee
"""

import os
from typing import Literal, cast

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM provider configuration"""

    provider: Literal["openai", "anthropic"] = Field(default="anthropic")
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_model: str = Field(default="gpt-4-turbo-preview")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load configuration from environment variables"""
        load_dotenv()

        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        if provider not in ["openai", "anthropic"]:
            raise ValueError(f"Invalid LLM_PROVIDER: {provider}. Must be 'openai' or 'anthropic'")

        return cls(
            provider=cast(Literal["openai", "anthropic"], provider),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        )

    def validate_api_key(self) -> bool:
        """Validate that the appropriate API key is set"""
        if self.provider == "openai":
            return bool(self.openai_api_key)
        elif self.provider == "anthropic":
            return bool(self.anthropic_api_key)
        return False

    def get_model(self) -> str:
        """Get the model name for the current provider"""
        if self.provider == "openai":
            return self.openai_model
        return self.anthropic_model


class CacheSettings(BaseModel):
    """Cache configuration settings"""

    enabled: bool = Field(default=True)
    cache_dir: str = Field(default=".cache/investment_committee")
    ttl_hours: int = Field(default=24)  # Default: 24 hour cache

    @classmethod
    def from_env(cls) -> "CacheSettings":
        """Load cache configuration from environment variables"""
        return cls(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            cache_dir=os.getenv("CACHE_DIR", ".cache/investment_committee"),
            ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
        )


class AppConfig(BaseModel):
    """Application configuration"""

    llm: LLMConfig
    cache: CacheSettings = Field(default_factory=CacheSettings)
    enable_rebuttal: bool = Field(default=True)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=60)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load full application configuration"""
        return cls(
            llm=LLMConfig.from_env(),
            cache=CacheSettings.from_env(),
            enable_rebuttal=os.getenv("ENABLE_REBUTTAL", "true").lower() == "true",
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout=int(os.getenv("TIMEOUT", "60")),
        )
