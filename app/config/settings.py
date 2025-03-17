from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="APP_DEBUG")
    
    # Application
    APP_NAME: str = "SiteChat"
    APP_VERSION: str = "0.1.0"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field("logs/sitechat.log", env="LOG_FILE")
    
    # OpenAI (Development)
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    
    # Vector Store
    VECTOR_STORE_PATH: Path = Field(
        BASE_DIR / "vectorstore",
        env="VECTOR_STORE_PATH"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()
