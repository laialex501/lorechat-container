"""OpenAI service implementation."""
from typing import Any, Generator, List

from app import logger
from app.config.settings import settings
from app.services.llm.llm_base import BaseLLMService, OpenAIModel
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_community.chat_models import ChatOpenAI


class OpenAIService(BaseLLMService, ChatOpenAI):
    """
    OpenAI service implementation using LangChain's ChatOpenAI.
    Inherits from both our BaseLLMService for consistent interface
    and ChatOpenAI for OpenAI-specific functionality.
    """

    def __init__(self, model: OpenAIModel = OpenAIModel.GPT35_TURBO):
        """Initialize the OpenAI service with model configuration."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured")
            
        logger.info(f"Initializing OpenAI LLM service with model {model}")
        
        ChatOpenAI.__init__(
            self,
            model_name=model.value,
            temperature=settings.TEMPERATURE,
            streaming=True,
            api_key=settings.OPENAI_API_KEY
        )
        BaseLLMService.__init__(self)

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response using OpenAI.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters for the model
            
        Returns:
            Generator yielding response content strings
        """
        try:
            for chunk in ChatOpenAI._stream(
                self,
                messages,
                **kwargs
            ):
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            yield "I apologize, but I encountered an error. Please try again."
