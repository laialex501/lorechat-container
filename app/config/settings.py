"""
Application settings configuration for development and production environments.
Centralizes config for consistent deployment and environment-based settings.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings configurable via environment variables or .env files.
    Provides type safety and validation through Pydantic.
    """
    
    # Environment
    ENV: Literal["development", "production"] = Field("development", description="Environment mode")
    DEBUG: bool = Field(False, description="Debug mode flag")
    
    # Application
    APP_NAME: str = "LoreChat"
    APP_VERSION: str = "0.1.0"
    
    # Paths - Structured for clear separation of concerns
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Logging - Configurable to support different environments
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(
        "logs/lorechat.log",
        description="Log file path"
    )

    # LLM Response Configuration - Tune model behavior
    TEMPERATURE: float = Field(
        0.7,
        description="Controls response randomness"
    )
    MAX_RESPONSE_TOKENS: int = Field(
        500,
        description="Limits response length"
    )

    # AWS Bedrock Settings - Required for AWS integration
    AWS_DEFAULT_REGION: str = Field(
        "us-east-1",
        description="AWS region for services"
    )

    # Vector Store - Persistent storage for embeddings
    VECTOR_STORE_PATH: Path = Field(
        None,
        description="Path to vector store files"
    )
    
    @field_validator("VECTOR_STORE_PATH", mode="before")
    def set_vector_store_path(cls, v, info):
        if v is None:
            # Access BASE_DIR from the values dict
            base_dir = info.data.get("BASE_DIR")
            if base_dir:
                return base_dir / "local_vectorstore" / "faiss"
        return v

    # Vector store implementation to use for this application
    # Set this environmental variable to test different stores in local
    VECTOR_STORE_PROVIDER: Literal["faiss", "opensearch", "upstash"] = Field(
        "faiss",
        description="Vector store provider to use"
    )

    @field_validator("VECTOR_STORE_PROVIDER", mode="before")
    def set_vector_store_provider(cls, v, info):
        if v is None:
            env = info.data.get("ENV")
            return "upstash" if env == "production" else "faiss"
        return v

    # Embedding model configuration
    EMBEDDING_DIMENSIONS: int = Field(
        512,
        description="Number of dimensions for embedding vectors"
    )
    BEDROCK_EMBEDDING_MODEL_ID: str = Field(
        "amazon.titan-embed-text-v2:0",
        description="AWS Bedrock model ID for embedding generation"
    )

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")

    # Vector store provider configuration
    OPENSEARCH_ENDPOINT: Optional[str] = Field(None, description="OpenSearch endpoint URL")

    # Upstash Settings
    UPSTASH_ENDPOINT_SECRET_NAME: Optional[str] = Field(
        None,
        description="AWS Secrets Manager secret name for Upstash endpoint"
    )
    UPSTASH_TOKEN_SECRET_NAME: Optional[str] = Field(
        None,
        description="AWS Secrets Manager secret name for Upstash token"
    )

    # Optional Upstash Settings for local development
    UPSTASH_ENDPOINT: Optional[str] = Field(
        None,
        description="Upstash endpoint URL"
    )
    UPSTASH_TOKEN: Optional[str] = Field(
        None,
        description="Upstash token"
    )

    # Use SettingsConfigDict instead of Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        # By default, field names are used as environment variable names
        # Only use env_mapping if you need custom environment variable names
        # env_mapping={"FIELD_NAME": "CUSTOM_ENV_VAR_NAME"}
    )


# Create global settings instance
settings = Settings()
