"""LLM configuration system for agentic retrieval."""
from enum import Enum
from typing import Dict, Optional

from app import logger
from app.services.llm import (AmazonModel, BaseLLMService, ClaudeModel,
                              DeepseekModel, LLMFactory, LLMProvider,
                              OpenAIModel)


class NodeType(str, Enum):
    """Types of nodes in the workflow."""
    DECOMPOSITION = "decomposition"
    PROCESSING = "processing"
    EVALUATION = "evaluation"
    REFINEMENT = "refinement"
    ANSWER = "answer"
    COMBINATION = "combination"
    RESPONSE = "response"


class LLMConfiguration:
    """
    Configuration for LLMs used in different nodes.
    
    This class maps node types to appropriate LLM models based on
    the requirements of each node. This allows us to use smaller,
    faster models for simple tasks and more powerful models for
    complex reasoning.
    """

    # Default configuration mapping node types to provider/model
    DEFAULT_CONFIG: Dict[NodeType, Optional[Dict[str, str]]] = {
        NodeType.DECOMPOSITION: {"provider": LLMProvider.Anthropic, "model": ClaudeModel.CLAUDE3_5_SONNET},
        NodeType.PROCESSING: {"provider": LLMProvider.Amazon, "model": AmazonModel.AMAZON_NOVA_LITE},
        NodeType.EVALUATION: {"provider": LLMProvider.Anthropic, "model": ClaudeModel.CLAUDE3_5_HAIKU},
        NodeType.REFINEMENT: {"provider": LLMProvider.Deepseek, "model": DeepseekModel.DEEPSEEK_R1},
        NodeType.ANSWER: {"provider": LLMProvider.OpenAI, "model": OpenAIModel.GPT_4o_MINI},
        NodeType.COMBINATION: {"provider": LLMProvider.Anthropic, "model": ClaudeModel.CLAUDE3_5_HAIKU},
        NodeType.RESPONSE: None  # Use user-selected model
    }

    @classmethod
    def get_llm_service(cls, node_type: NodeType, user_llm_service: BaseLLMService) -> BaseLLMService:
        """
        Get the appropriate LLM service for a node type.

        Args:
            node_type: Type of node requiring an LLM
            user_llm_service: User-selected LLM service

        Returns:
            LLM service configured for the node
        """
        # If this node should use the user-selected LLM, return it
        if cls.DEFAULT_CONFIG[node_type] is None:
            logger.info(f"Using user-selected LLM for {node_type}")
            return user_llm_service

        # Otherwise, create a new LLM service based on configuration
        config = cls.DEFAULT_CONFIG[node_type]
        logger.info(f"Creating LLM service for {node_type}: {config['provider']}/{config['model']}")

        try:
            return LLMFactory.create_llm_service(
                provider=config["provider"],
                model_name=config["model"]
            )
        except Exception as e:
            logger.error(f"Error creating LLM service for {node_type}: {str(e)}", exc_info=True)
            # Fall back to user-selected LLM
            logger.info(f"Falling back to user-selected LLM for {node_type}")
            return user_llm_service
