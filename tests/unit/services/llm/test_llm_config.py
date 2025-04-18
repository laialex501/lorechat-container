"""Unit tests for the LLM configuration system."""
from unittest.mock import MagicMock, patch

from app.services.llm import (AmazonModel, BaseLLMService, ClaudeModel,
                              DeepseekModel, LLMProvider, OpenAIModel)
from app.services.llm.llm_config import LLMConfiguration, NodeType


class TestLLMConfiguration:
    """Tests for the LLMConfiguration class."""

    def test_default_config_mapping(self):
        """Test that the default configuration maps node types to appropriate providers/models."""
        config = LLMConfiguration.DEFAULT_CONFIG

        # Check decomposition node config
        assert config[NodeType.DECOMPOSITION]["provider"] == LLMProvider.Anthropic
        assert config[NodeType.DECOMPOSITION]["model"] == ClaudeModel.CLAUDE3_5_SONNET

        # Check processing node config
        assert config[NodeType.PROCESSING]["provider"] == LLMProvider.Amazon
        assert config[NodeType.PROCESSING]["model"] == AmazonModel.AMAZON_NOVA_LITE

        # Check evaluation node config
        assert config[NodeType.EVALUATION]["provider"] == LLMProvider.Anthropic
        assert config[NodeType.EVALUATION]["model"] == ClaudeModel.CLAUDE3_5_HAIKU

        # Check refinement node config
        assert config[NodeType.REFINEMENT]["provider"] == LLMProvider.Deepseek
        assert config[NodeType.REFINEMENT]["model"] == DeepseekModel.DEEPSEEK_R1

        # Check answer node config
        assert config[NodeType.ANSWER]["provider"] == LLMProvider.OpenAI
        assert config[NodeType.ANSWER]["model"] == OpenAIModel.GPT_4o_MINI

        # Check combination node config
        assert config[NodeType.COMBINATION]["provider"] == LLMProvider.Anthropic
        assert config[NodeType.COMBINATION]["model"] == ClaudeModel.CLAUDE3_5_HAIKU

        # Check response node config (should be None to use user-selected model)
        assert config[NodeType.RESPONSE] is None

    @patch("app.services.llm.llm_config.LLMFactory")
    def test_get_llm_service_for_user_selected_node(self, mock_llm_factory):
        """Test getting LLM service for a node that should use the user-selected LLM."""
        # Create a mock user LLM service
        mock_user_llm = MagicMock(spec=BaseLLMService)
        
        # Get LLM service for response node (which should use user-selected LLM)
        result = LLMConfiguration.get_llm_service(NodeType.RESPONSE, mock_user_llm)
        
        # Verify that the user-selected LLM is returned
        assert result == mock_user_llm
        # Verify that the factory was not called
        mock_llm_factory.create_llm_service.assert_not_called()

    @patch("app.services.llm.llm_config.LLMFactory")
    def test_get_llm_service_for_specialized_node(self, mock_llm_factory):
        """Test getting LLM service for a node that should use a specialized LLM."""
        # Create a mock user LLM service and a mock specialized LLM service
        mock_user_llm = MagicMock(spec=BaseLLMService)
        mock_specialized_llm = MagicMock(spec=BaseLLMService)
        mock_llm_factory.create_llm_service.return_value = mock_specialized_llm
        
        # Get LLM service for decomposition node (which should use a specialized LLM)
        result = LLMConfiguration.get_llm_service(NodeType.DECOMPOSITION, mock_user_llm)
        
        # Verify that the specialized LLM is returned
        assert result == mock_specialized_llm
        # Verify that the factory was called with the correct parameters
        mock_llm_factory.create_llm_service.assert_called_once_with(
            provider=LLMProvider.Anthropic,
            model_name=ClaudeModel.CLAUDE3_5_SONNET
        )

    @patch("app.services.llm.llm_config.LLMFactory")
    def test_get_llm_service_with_factory_error(self, mock_llm_factory):
        """Test getting LLM service when the factory raises an error."""
        # Create a mock user LLM service
        mock_user_llm = MagicMock(spec=BaseLLMService)
        # Make the factory raise an exception
        mock_llm_factory.create_llm_service.side_effect = Exception("Test error")
        
        # Get LLM service for decomposition node
        result = LLMConfiguration.get_llm_service(NodeType.DECOMPOSITION, mock_user_llm)
        
        # Verify that the user-selected LLM is returned as a fallback
        assert result == mock_user_llm
        # Verify that the factory was called
        mock_llm_factory.create_llm_service.assert_called_once()
