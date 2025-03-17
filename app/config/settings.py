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
    ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="APP_DEBUG")
    
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
    
    # LLM Configuration - Support multiple providers
    LLM_PROVIDER: Literal["openai", "bedrock"] = Field(
        ...,  # Required to ensure explicit provider selection
        env="LLM_PROVIDER",
        description="LLM provider (openai or bedrock)"
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
    
    # OpenAI Settings - Required for OpenAI integration
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    
    # AWS Bedrock Settings - Required for AWS integration
    AWS_DEFAULT_REGION: Optional[str] = Field(
        None,
        env="AWS_DEFAULT_REGION"
    )
    AWS_BEDROCK_MODEL_ID: str = Field(
        "anthropic.claude-3-sonnet-20240229-v1:0",
        env="AWS_BEDROCK_MODEL_ID"
    )
    
    # Vector Store - Persistent storage for embeddings
    VECTOR_STORE_PATH: Path = Field(
        BASE_DIR / "vectorstore",
        env="VECTOR_STORE_PATH"
    )
    
    # Use SettingsConfigDict instead of Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def is_openai(self) -> bool:
        """
        Determines if OpenAI is the selected provider.
        Used for configuration validation and service init.
        """
        return self.LLM_PROVIDER == "openai"

    @property
    def is_bedrock(self) -> bool:
        """
        Determines if AWS Bedrock is the selected provider.
        Used for configuration validation and service init.
        """
        return self.LLM_PROVIDER == "bedrock"

    def validate_llm_config(self) -> None:
        """
        Validates LLM configuration based on selected provider.
        Prevents runtime errors due to missing configuration.
        """
        if self.is_openai and not self.OPENAI_API_KEY:
            msg = "OPENAI_API_KEY is required when using OpenAI provider"
            raise ValueError(msg)
        
        if self.is_bedrock and not self.AWS_DEFAULT_REGION:
            msg = "AWS_DEFAULT_REGION is required when using Bedrock provider"
            raise ValueError(msg)


# Create global settings instance
settings = Settings()

# Validate LLM configuration
settings.validate_llm_config()
