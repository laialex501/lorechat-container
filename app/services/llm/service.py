"""LLM service implementations."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Generator, List

from app.config.settings import settings
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_aws.chat_models.bedrock import ChatBedrock
from langchain_community.chat_models import ChatOpenAI


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
    CLAUDE3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"


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


class OpenAIService(BaseLLMService):
    """
    OpenAI service implementation optimized for chat interactions.
    Uses ChatOpenAI over base OpenAI class for better conversation handling
    and more consistent responses in chat-based applications.
    """

    def __init__(self, model: OpenAIModel = OpenAIModel.GPT35_TURBO):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured")
        self.llm = ChatOpenAI(
            model=model.value,
            temperature=settings.TEMPERATURE,
            streaming=True,
            api_key=settings.OPENAI_API_KEY
        )

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> Generator:
        """Generate a streaming response using OpenAI."""
        for chunk in self.llm.stream(messages):
            if isinstance(chunk, AIMessageChunk):
                yield chunk.content


class BedrockService(BaseLLMService):
    """
    Amazon Bedrock service implementation for enterprise-grade deployment.
    Uses ChatBedrock for better integration with AWS services and
    to leverage existing AWS authentication mechanisms.
    """

    def __init__(self, model: ClaudeModel = ClaudeModel.CLAUDE3_SONNET):
        if not settings.AWS_DEFAULT_REGION:
            raise ValueError("AWS region is not configured")
        self.llm = ChatBedrock(
            model_id=model.value,
            model_kwargs={
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_RESPONSE_TOKENS
            },
            region_name=settings.AWS_DEFAULT_REGION,
            streaming=True
        )

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> Generator:
        """Generate a streaming response using AWS Bedrock."""
        for chunk in self.llm.stream(messages):
            if isinstance(chunk, AIMessageChunk):
                yield chunk.content


def get_llm_service(
    provider: str = "bedrock",
    model_name: BaseModel = ClaudeModel.CLAUDE3_SONNET
) -> BaseLLMService:
    """Factory function to get LLM service."""
    provider = provider.lower()
    
    if provider == "openai":
        model = model_name or OpenAIModel.GPT35_TURBO
        return OpenAIService(model)
    
    elif provider == "bedrock":
        model = model_name or ClaudeModel.CLAUDE3_SONNET
        return BedrockService(model)
    
    else:
        raise ValueError(f"Unknown provider: {provider}")
