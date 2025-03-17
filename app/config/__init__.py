"""
Configuration module for SiteChat application.
"""

from app.config.constants import (CHUNK_OVERLAP, CHUNK_SIZE,
                                  MAX_CONCURRENT_REQUESTS, MAX_HISTORY_LENGTH,
                                  MAX_RESPONSE_TOKENS, SYSTEM_PROMPT,
                                  TEMPERATURE, TOP_K, ChatRole, Environment,
                                  LLMProvider, LogLevel, VectorStoreType)
from app.config.settings import Settings, settings

__all__ = [
    # Classes
    "Settings",
    "ChatRole",
    "Environment",
    "LLMProvider",
    "LogLevel",
    "VectorStoreType",
    # Constants
    "MAX_HISTORY_LENGTH",
    "SYSTEM_PROMPT",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "MAX_CONCURRENT_REQUESTS",
    "MAX_RESPONSE_TOKENS",
    "TEMPERATURE",
    "TOP_K",
    # Instances
    "settings",
]
