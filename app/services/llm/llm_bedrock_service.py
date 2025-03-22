"""Bedrock service implementation."""
from typing import Generator, List

from app import logger
from app.config.settings import settings
from app.services.llm.llm_base import BaseLLMService, ClaudeModel
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_aws.chat_models.bedrock import ChatBedrock


class BedrockService(BaseLLMService):
    """
    Amazon Bedrock service implementation for enterprise-grade deployment.
    Uses ChatBedrock for better integration with AWS services and
    to leverage existing AWS authentication mechanisms.
    """

    def __init__(self, model: ClaudeModel = ClaudeModel.CLAUDE3_HAIKU):
        logger.info(f"Initializing Bedrock LLM service with model {model}")
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
