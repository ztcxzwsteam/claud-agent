"""Application settings using Pydantic Settings."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 显式加载 agent 目录下的 .env 文件，确保无论以何种工作目录启动均能正确读取配置
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # LLM Configuration (DeepSeek for chat and decision-making)
    deepseek_api_key: str = Field(alias="DEEPSEEK_API_KEY")
    model: str = Field(default="deepseek-chat", alias="MODEL")
    base_url: str = Field(default="https://api.deepseek.com/v1", alias="BASE_URL")

    # Embeddings Configuration (DashScope strictly for embeddings)
    dashscope_api_key: str = Field(alias="DASHSCOPE_API_KEY")

    # Tavily Web Search API
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")
    
    # MCP Configuration
    mcp_servers_config: Path = Field(
        default=Path(__file__).parent / "mcp_servers.json",
        alias="MCP_SERVERS_CONFIG"
    )
    
    # Weather API
    openweather_api_key: str | None = Field(default=None, alias="OPENWEATHER_API_KEY")
    
    # Redis (short-term memory)
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    redis_ttl: int = Field(default=1800, alias="REDIS_TTL")  # seconds
    
    # Milvus (long-term memory)
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")
    milvus_api_key: str | None = Field(default=None, alias="MILVUS_API_KEY")
    
    # Neo4j (knowledge graph)
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", alias="NEO4J_DATABASE")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    @field_validator("deepseek_api_key", "dashscope_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("API key cannot be empty")
        return v.strip()
    
    def get_model_config(self) -> dict[str, Any]:
        """Get model configuration for LangChain (DeepSeek)."""
        return {
            "model": self.model,
            "api_key": self.deepseek_api_key,
            "base_url": self.base_url,
        }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
