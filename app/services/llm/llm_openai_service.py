"""OpenAI service implementation."""
import os
from typing import Any, Generator, List

import boto3
from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.llm.llm_base import BaseLLMService, OpenAIModel
from langchain.schema import BaseMessage
from langchain.schema.messages import AIMessageChunk
from langchain_community.chat_models import ChatOpenAI


class OpenAIService(ChatOpenAI, BaseLLMService):
    """
    OpenAI service implementation using LangChain's ChatOpenAI.
    Inherits from both our BaseLLMService for consistent interface
    and ChatOpenAI for OpenAI-specific functionality.
    """

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "OpenAI LLM integration"

    def _get_credentials(self) -> str:
        """Get OpenAI API key based on environment."""
        try:
            if settings.ENV == Environment.PRODUCTION:
                logger.info("Getting OpenAI API key from AWS Secrets Manager")
                # Check if secret name is configured
                if not os.environ.get("OPENAI_API_SECRET_NAME"):
                    raise ValueError("OPENAI_API_SECRET_NAME environment variable is required")

                try:
                    # Get secret from AWS Secrets Manager
                    secrets = boto3.client(
                        'secretsmanager',
                        region_name=settings.AWS_DEFAULT_REGION
                    )

                    # Get OpenAI API key
                    secret = secrets.get_secret_value(
                        SecretId=os.environ.get("OPENAI_API_SECRET_NAME")
                    )
                    api_key = secret['SecretString']
                    return api_key

                except Exception as e:
                    raise ValueError(f"Failed to retrieve OpenAI API key: {str(e)}")

            # Use local API key in development
            elif settings.ENV == Environment.DEVELOPMENT:
                logger.info("Using local OpenAI API key for development")
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY is required in development environment")
                
                return settings.OPENAI_API_KEY
                
        except Exception as e:
            logger.error(f"Error getting OpenAI API key: {str(e)}")
            raise

    def __init__(self, model: OpenAIModel = OpenAIModel.GPT_4o_MINI):
        """Initialize the OpenAI service with model configuration."""
        api_key = self._get_credentials()
        
        logger.info(f"Initializing OpenAI LLM service with model {model}")

        super().__init__(
            model_name=model.value,
            temperature=settings.TEMPERATURE,
            streaming=True,
            api_key=api_key
        )

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
            for chunk in self._stream(
                messages,
                **kwargs
            ):
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            yield "I apologize, but I encountered an error. Please try again."
