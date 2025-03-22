"""OpenAI service implementation."""
from typing import Generator, List

from app import logger
from app.config.settings import settings
from app.services.llm.llm_base import BaseLLMService, OpenAIModel
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_community.chat_models import ChatOpenAI


class OpenAIService(BaseLLMService):
    """
    OpenAI service implementation optimized for chat interactions.
    Uses ChatOpenAI over base OpenAI class for better conversation handling
    and more consistent responses in chat-based applications.
    """

    def __init__(self, model: OpenAIModel = OpenAIModel.GPT35_TURBO):
        logger.info(f"Initializing OpenAI LLM service with model {model}")
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
