"""Base classes and enums for LLM services."""
from enum import Enum
from typing import Any, Generator, List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult
from langchain.schema.messages import AIMessage, AIMessageChunk


class BaseModel(str, Enum):
    """Base class for LLM model enums"""
    pass


class OpenAIModel(BaseModel):
    """Available OpenAI models."""
    GPT_4o_MINI = "gpt-4o-mini"


# https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html
# Use cross-region inference profiles for the following bedrock profiles

class ClaudeModel(BaseModel):
    """Available Claude models via Bedrock."""
    CLAUDE3_5_HAIKU = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE3_5_SONNET = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"


class DeepseekModel(BaseModel):
    """Available DeepSeek models via Bedrock."""
    DEEPSEEK_R1 = "us.deepseek.r1-v1:0"


class AmazonModel(BaseModel):
    """Available Amazon models via Bedrock."""
    AMAZON_NOVA_LITE = "us.amazon.nova-lite-v1:0"


class LLMProvider(str, Enum):
    """Available LLM providers."""
    OpenAI = "OpenAI"
    Anthropic = "Anthropic"
    Deepseek = "Deepseek"
    Amazon = "Amazon"


class BaseLLMService(BaseChatModel):
    """
    Base interface for LLM services.
    Inherits from LangChain's BaseChatModel to ensure compatibility with LangChain's
    ecosystem while providing our custom functionality.
    """

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "custom_chat_model"

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response from the LLM.
        This is the core method that subclasses must implement.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generator yielding response content strings
        """
        raise NotImplementedError(
            "Subclasses must implement generate_response for streaming responses"
        )

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Generator[AIMessageChunk, None, None]:
        """
        Stream a chat response. Uses our generate_response method and wraps the
        output in AIMessageChunks for LangChain compatibility.
        """
        for content in self.generate_response(messages, **kwargs):
            yield AIMessageChunk(content=content)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate a chat response. This is used by LangChain for non-streaming responses.
        We implement it by collecting all chunks from our streaming implementation.
        """
        chunks = []
        for chunk in self.generate_response(messages, **kwargs):
            chunks.append(chunk)
        
        return ChatResult(generations=[AIMessage(content="".join(chunks))])
