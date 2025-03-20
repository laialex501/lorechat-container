"""
Application settings configuration for development and production environments.
Centralizes config for consistent deployment and environment-based settings.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings configurable via environment variables or .env files.
    Provides type safety and validation through Pydantic.
    """
    
    # Environment
    ENV: Literal["development", "production"] = Field("development",
                                                      env="ENV")
    DEBUG: bool = Field(False, env="DEBUG")
    
    # Application
    APP_NAME: str = "SiteChat"
    APP_VERSION: str = "0.1.0"
    
    # Paths - Structured for clear separation of concerns
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Logging - Configurable to support different environments
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(
        "logs/sitechat.log",
        env="LOG_FILE"
    )
    
    # LLM Response Configuration - Tune model behavior
    TEMPERATURE: float = Field(
        0.7,
        env="TEMPERATURE",
        description="Controls response randomness"
    )
    MAX_RESPONSE_TOKENS: int = Field(
        500,
        env="MAX_RESPONSE_TOKENS",
        description="Limits response length"
    )
    
    # AWS Bedrock Settings - Required for AWS integration
    AWS_DEFAULT_REGION: str = Field(
        "us-west-2",
        env="AWS_DEFAULT_REGION"
    )
    
    # Vector Store - Persistent storage for embeddings
    VECTOR_STORE_PATH: Path = Field(
        BASE_DIR / "dev_vectorstore" / "faiss",
        env="VECTOR_STORE_PATH"
    )

    # Vector store provider configuration
    VECTOR_STORE_PROVIDER: Literal["faiss", "opensearch"] = Field(
        "faiss",
        env="VECTOR_STORE_PROVIDER",
        description="Vector store provider (faiss or opensearch)"
    )
    OPENSEARCH_ENDPOINT: Optional[str] = Field(None, env="OPENSEARCH_ENDPOINT")

    # Use SettingsConfigDict instead of Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    def validate_vector_store_config(self) -> None:
        """
        Validates vector store configuration.
        Prevents runtime errors due to missing configuration.
        """
        if (self.VECTOR_STORE_PROVIDER == "opensearch"
                and not self.OPENSEARCH_ENDPOINT):
            msg = "OPENSEARCH_ENDPOINT is required when using OpenSearch as " \
                + "vector store provider"
            raise ValueError(msg)


# Create global settings instance
settings = Settings()

# Validate vector store configuration
settings.validate_vector_store_config()
