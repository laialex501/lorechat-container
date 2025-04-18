"""Unit tests for the LLM factory."""
from unittest.mock import patch

import pytest
from app.services.llm import (AmazonModel, ClaudeModel, DeepseekModel,
                              LLMProvider, OpenAIModel)
from app.services.llm.llm_factory import LLMFactory


class TestLLMFactory:
    """Tests for the LLMFactory class."""

    @patch("app.services.llm.llm_factory.OpenAIService")
    def test_create_openai_service(self, mock_openai_service):
        """Test creating an OpenAI service."""
        # Setup
        provider = LLMProvider.OpenAI
        model = OpenAIModel.GPT_4o_MINI
        mock_instance = mock_openai_service.return_value
        
        # Execute
        service = LLMFactory.create_llm_service(provider, model)
        
        # Verify
        assert service == mock_instance
        mock_openai_service.assert_called_once_with(model)

    @patch("app.services.llm.llm_factory.BedrockService")
    def test_create_anthropic_service(self, mock_bedrock_service):
        """Test creating an Anthropic service via Bedrock."""
        # Setup
        provider = LLMProvider.Anthropic
        model = ClaudeModel.CLAUDE3_5_HAIKU
        mock_instance = mock_bedrock_service.return_value
        
        # Execute
        service = LLMFactory.create_llm_service(provider, model)
        
        # Verify
        assert service == mock_instance
        mock_bedrock_service.assert_called_once_with(model)

    @patch("app.services.llm.llm_factory.BedrockService")
    def test_create_deepseek_service(self, mock_bedrock_service):
        """Test creating a Deepseek service via Bedrock."""
        # Setup
        provider = LLMProvider.Deepseek
        model = DeepseekModel.DEEPSEEK_R1
        mock_instance = mock_bedrock_service.return_value
        
        # Execute
        service = LLMFactory.create_llm_service(provider, model)
        
        # Verify
        assert service == mock_instance
        mock_bedrock_service.assert_called_once_with(model)

    @patch("app.services.llm.llm_factory.BedrockService")
    def test_create_amazon_service(self, mock_bedrock_service):
        """Test creating an Amazon service via Bedrock."""
        # Setup
        provider = LLMProvider.Amazon
        model = AmazonModel.AMAZON_NOVA_LITE
        mock_instance = mock_bedrock_service.return_value
        
        # Execute
        service = LLMFactory.create_llm_service(provider, model)
        
        # Verify
        assert service == mock_instance
        mock_bedrock_service.assert_called_once_with(model)

    def test_create_with_unknown_provider(self):
        """Test creating a service with an unknown provider raises ValueError."""
        # Setup
        provider = "UnknownProvider"
        model = OpenAIModel.GPT_4o_MINI
        
        # Execute and verify
        with pytest.raises(ValueError, match=f"Unknown provider: {provider}"):
            LLMFactory.create_llm_service(provider, model)

    @patch("app.services.llm.llm_factory.BedrockService")
    def test_create_with_default_model(self, mock_bedrock_service):
        """Test creating a service with a default model when none is provided."""
        # Setup
        mock_instance = mock_bedrock_service.return_value
        
        # Execute
        service = LLMFactory.create_llm_service()  # No arguments = use defaults
        
        # Verify
        assert service == mock_instance
        mock_bedrock_service.assert_called_once_with(ClaudeModel.CLAUDE3_5_HAIKU)
