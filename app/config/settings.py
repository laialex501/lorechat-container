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
    APP_NAME: str = "LoreChat"
    APP_VERSION: str = "0.1.0"
    
    # Paths - Structured for clear separation of concerns
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Logging - Configurable to support different environments
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(
        "logs/lorechat.log",
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
        "us-east-1",
        env="AWS_DEFAULT_REGION"
    )
    
    # Vector Store - Persistent storage for embeddings
    VECTOR_STORE_PATH: Path = Field(
        BASE_DIR / "dev_vectorstore" / "faiss",
        env="VECTOR_STORE_PATH"
    )
    # Vector store implementation to use for this application
    # Set this enviornmental variable to test different stores in local
    VECTOR_STORE_PROVIDER: Literal["faiss", "opensearch", "upstash"] = Field(
        "faiss",
        env="VECTOR_STORE_PROVIDER"
    )

    # Embedding model configuration
    EMBEDDING_DIMENSIONS: int = Field(
        512,
        env="EMBEDDING_DIMENSIONS",
        description="Number of dimensions for embedding vectors"
    )
    BEDROCK_EMBEDDING_MODEL_ID: str = Field(
        "amazon.titan-embed-text-v2:0",
        env="BEDROCK_EMBEDDING_MODEL_ID",
        description="AWS Bedrock model ID for embedding generation"
    )

    # Vector store provider configuration
    OPENSEARCH_ENDPOINT: Optional[str] = Field(None, env="OPENSEARCH_ENDPOINT")
    
    # Upstash Settings
    UPSTASH_ENDPOINT_SECRET_NAME: Optional[str] = Field(
        None,
        env="UPSTASH_ENDPOINT_SECRET_NAME",
        description="AWS Secrets Manager secret name for Upstash endpoint"
    )
    UPSTASH_TOKEN_SECRET_NAME: Optional[str] = Field(
        None,
        env="UPSTASH_TOKEN_SECRET_NAME",
        description="AWS Secrets Manager secret name for Upstash token"
    )

    # Use SettingsConfigDict instead of Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # Optional Upstash Settings for local development
    UPSTASH_ENDPOINT: Optional[str] = Field(
        None,
        env="UPSTASH_ENDPOINT",
        description="Upstash endpoint URL"
    )
    UPSTASH_TOKEN: Optional[str] = Field(
        None,
        env="UPSTASH_TOKEN",
        description="Upstash token"
    )


# Create global settings instance
settings = Settings()
