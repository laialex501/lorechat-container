"""
LLM service implementations that abstract provider-specific details.
This abstraction allows us to easily switch between different LLM providers
while maintaining consistent behavior across the application.
"""

from abc import ABC, abstractmethod
from typing import List

from app.config.settings import settings
from langchain.chat_models import BedrockChat, ChatOpenAI
from langchain.schema import BaseMessage


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
    ) -> str:
        """
        Generate a response from the LLM based on conversation history.
        Abstract method to enforce implementation in concrete classes,
        ensuring consistent behavior across different providers.
        """
        pass


class OpenAIService(BaseLLMService):
    """
    OpenAI service implementation optimized for chat interactions.
    Uses ChatOpenAI over base OpenAI class for better conversation handling
    and more consistent responses in chat-based applications.
    """

    def __init__(self):
        # Validate configuration before initialization to fail fast
        if not settings.is_openai:
            raise ValueError("OpenAI is not configured as the LLM provider")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured")

        # Initialize with controlled parameters for consistent output
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_RESPONSE_TOKENS,
            api_key=settings.OPENAI_API_KEY
        )

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> str:
        """
        Generate a response using OpenAI's chat models.
        Returns the first generation's text as we prioritize
        deterministic responses over multiple alternatives.
        """
        response = self.llm.generate([messages])
        return response.generations[0][0].text


class BedrockService(BaseLLMService):
    """
    Amazon Bedrock service implementation for enterprise-grade deployment.
    Uses BedrockChat for better integration with AWS services and
    to leverage existing AWS authentication mechanisms.
    """

    def __init__(self):
        # Validate configuration before initialization to fail fast
        if not settings.is_bedrock:
            raise ValueError("Bedrock is not configured as the LLM provider")
        
        if not settings.AWS_DEFAULT_REGION:
            raise ValueError("AWS region is not configured")

        # Initialize with enterprise-focused configuration
        self.llm = BedrockChat(
            model_id=settings.AWS_BEDROCK_MODEL_ID,
            model_kwargs={
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_RESPONSE_TOKENS
            },
            region_name=settings.AWS_DEFAULT_REGION
        )

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> str:
        """
        Generate a response using AWS Bedrock.
        Returns the first generation's text to maintain
        consistency with OpenAI implementation.
        """
        response = self.llm.generate([messages])
        return response.generations[0][0].text


def get_llm_service() -> BaseLLMService:
    """
    Factory function to get the configured LLM service.
    This pattern allows for runtime provider selection and
    ensures proper initialization based on configuration.
    """
    if settings.is_openai:
        return OpenAIService()
    elif settings.is_bedrock:
        return BedrockService()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
