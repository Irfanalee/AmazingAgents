"""
Configuration management for Shadow ARB.
Loads environment variables and provides centralized settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration for Shadow ARB."""
    
    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    
    # LiteLLM Configuration
    LITELLM_LOG: str = os.getenv("LITELLM_LOG", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validates that required configuration is present.
        
        Raises:
            ValueError: If required environment variables are missing
        """
        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "At least one of OPENAI_API_KEY or ANTHROPIC_API_KEY must be set"
            )
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """
        Returns LiteLLM configuration dictionary.
        
        Returns:
            Dictionary containing model and API key configuration
        """
        return {
            "model": cls.LLM_MODEL,
            "api_key": cls.OPENAI_API_KEY or cls.ANTHROPIC_API_KEY,
        }
