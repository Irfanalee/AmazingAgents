import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class MCPSettings(BaseSettings):
    """Configuration for MCP server and AI provider connections."""
    # AI Provider Settings
    AI_PROVIDER: str = "google" # options: google, openai, anthropic, ollama
    AI_MODEL: str = "gemini-1.5-pro"
    AI_API_KEY: Optional[str] = None
    AI_BASE_URL: Optional[str] = None # For Ollama or custom endpoints

    # Memory Settings
    CHROMA_PERSIST_DIR: str = "./.chroma"

    # MCP Server Settings
    DOCKER_MCP_URI: Optional[str] = None
    DOCKER_MCP_COMMAND: Optional[str] = "docker"
    DOCKER_MCP_ARGS: List[str] = ["run", "-i", "--rm", "mcp/docker-server"]
    TRIVY_MCP_COMMAND: Optional[str] = "docker"
    TRIVY_MCP_ARGS: List[str] = ["run", "-i", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "mcp/trivy-server"]
    GITHUB_MCP_URI: Optional[str] = None
    GITHUB_MCP_COMMAND: Optional[str] = "docker"
    GITHUB_MCP_ARGS: List[str] = ["run", "-i", "--rm", "mcp/github-server"]
    FILESYSTEM_MCP_URI: Optional[str] = None
    FILESYSTEM_MCP_COMMAND: Optional[str] = "docker"
    FILESYSTEM_MCP_ARGS: List[str] = ["run", "-i", "--rm", "-v", "/:/host", "mcp/filesystem-server"]
    SHELL_MCP_COMMAND: Optional[str] = "docker"
    SHELL_MCP_ARGS: List[str] = ["run", "-i", "--rm", "mcp/shell-server"]
    GITHUB_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def get_mcp_config() -> MCPSettings:
    """Helper function to load MCP settings."""
    return MCPSettings()

if __name__ == "__main__":
    # Simple check for configuration loading
    config = get_mcp_config()
    print(f"Docker MCP URI: {config.DOCKER_MCP_URI}")
