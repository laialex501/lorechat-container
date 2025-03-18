"""
LLM service implementations that abstract provider-specific details.
This abstraction allows us to easily switch between different LLM providers
while maintaining consistent behavior across the application.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Union

from app.config.settings import settings
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_community.chat_models import BedrockChat, ChatOpenAI


class BaseLLMService(ABC):
    """
    Abstract base class for LLM services to ensure consistent interface.
    This abstraction enables easy provider switching and testing by
    defining a common contract that all LLM implementations must follow.
    """

    @abstractmethod
    async def generate_response(
        self,
        messages: List[BaseMessage],
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate a response from the LLM based on conversation history.
        
        Args:
            messages: List of conversation messages
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Either a complete response string or an async generator of chunks
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

    async def generate_response(
        self,
        messages: List[BaseMessage],
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Generate a response using OpenAI's chat models."""
        if not stream:
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
        
        async def stream_response() -> AsyncGenerator[str, None]:
            async for chunk in self.llm.astream(messages):
                if isinstance(chunk, AIMessageChunk):
                    yield chunk.content
        
        return stream_response()


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

    async def generate_response(
        self,
        messages: List[BaseMessage],
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Generate a response using AWS Bedrock."""
        if not stream:
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
            
        async def stream_response() -> AsyncGenerator[str, None]:
            async for chunk in self.llm.astream(messages):
                if isinstance(chunk, AIMessageChunk):
                    yield chunk.content
        
        return stream_response()


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
