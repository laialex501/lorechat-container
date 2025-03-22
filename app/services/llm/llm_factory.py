"""LLM factory for creating LLM service instances."""
from app import logger
from app.services.llm.llm_base import (BaseLLMService, BaseModel, ClaudeModel,
                                       LLMProvider, OpenAIModel)
from app.services.llm.llm_bedrock_service import BedrockService
from app.services.llm.llm_openai_service import OpenAIService


class LLMFactory:
    """Factory class for creating LLM service instances."""
    
    @staticmethod
    def create_llm_service(
        provider: LLMProvider = LLMProvider.Anthropic,
        model_name: BaseModel = ClaudeModel.CLAUDE3_SONNET
    ) -> BaseLLMService:
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
        if provider == LLMProvider.OPENAI:
            model = model_name or OpenAIModel.GPT35_TURBO
            return OpenAIService(model)
        
        elif provider == LLMProvider.Anthropic:
            model = model_name or ClaudeModel.CLAUDE3_HAIKU
            return BedrockService(model)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
