"""LLM factory for creating LLM service instances."""
from typing import Union

from app import logger
from app.services.llm.llm_base import (BaseLLMService, BaseModel, ClaudeModel,
                                       DeepseekModel, LLMProvider, OpenAIModel)
from app.services.llm.llm_bedrock_service import BedrockService
from app.services.llm.llm_openai_service import OpenAIService
from langchain.chat_models.base import BaseChatModel


class LLMFactory:
    """Factory class for creating LLM service instances."""
    
    @staticmethod
    def create_llm_service(
        provider: LLMProvider = LLMProvider.Anthropic,
        model_name: BaseModel = ClaudeModel.CLAUDE3_5_HAIKU
    ) -> Union[BaseLLMService, BaseChatModel]:
        """
        Create and return an LLM service instance.
        
        Args:
            provider: The LLM provider to use
            model_name: The specific model to use
            
        Returns:
            An instance of BaseLLMService
            
        Raises:
            ValueError: If the provider is unknown
        """
        logger.info("Initializing LLM service")
        if provider == LLMProvider.OpenAI:
            model = model_name or OpenAIModel.GPT35_TURBO
            return OpenAIService(model)
        
        elif provider == LLMProvider.Anthropic:
            model = model_name or ClaudeModel.CLAUDE3_5_HAIKU
            return BedrockService(model)
        
        elif provider == LLMProvider.Deepseek:
            model = model_name or DeepseekModel.DEEPSEEK_R1
            return BedrockService(model)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
