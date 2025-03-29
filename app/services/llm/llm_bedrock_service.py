"""Bedrock service implementation."""
from typing import Any, Generator, List

from app import logger
from app.config.settings import settings
from app.services.llm.llm_base import BaseLLMService, ClaudeModel
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_aws.chat_models.bedrock import ChatBedrock


class BedrockService(ChatBedrock, BaseLLMService):
    """
    Amazon Bedrock service implementation using LangChain's ChatBedrock.
    Inherits from both ChatBedrock for AWS-specific functionality and
    BaseLLMService for consistent interface.
    """

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "Bedrock LLM integration"

    def __init__(self, model: ClaudeModel = ClaudeModel.CLAUDE3_HAIKU):
        """Initialize the Bedrock service with model configuration."""
        if not settings.AWS_DEFAULT_REGION:
            raise ValueError("AWS region is not configured")
            
        logger.info(f"Initializing Bedrock LLM service with model {model}")
        
        super().__init__(
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
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response using Bedrock.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters for the model
            
        Returns:
            Generator yielding response content strings
        """
        try:
            for chunk in self._stream(
                messages,
                **kwargs
            ):
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            yield "I apologize, but I encountered an error. Please try again."
