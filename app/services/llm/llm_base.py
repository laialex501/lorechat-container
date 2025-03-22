"""Base classes and enums for LLM services."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Generator, List

from langchain.schema import BaseMessage


class BaseModel(str, Enum):
    """Base class for LLM model enums"""
    pass


class OpenAIModel(BaseModel):
    """Available OpenAI models."""
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT35_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT35_MINI = "gpt-3.5-turbo-0125"


class ClaudeModel(BaseModel):
    """Available Claude models via Bedrock."""
    CLAUDE3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"


class LLMProvider(str, Enum):
    """Available LLM providers."""
    OPENAI = "OpenAi"
    Anthropic = "Anthropic"


class BaseLLMService(ABC):
    """
    Abstract base class for LLM services to ensure consistent interface.
    This abstraction enables easy provider switching and testing by
    defining a common contract that all LLM implementations must follow.
    """
    
    @abstractmethod
    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> Generator:
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generator yielding response chunks
        """
        pass
