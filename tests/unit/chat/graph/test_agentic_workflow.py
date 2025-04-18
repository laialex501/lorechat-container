"""Unit tests for the agentic workflow."""
from unittest.mock import MagicMock, patch

from app.chat.graph.agentic_workflow import (ConfigSchema,
                                             create_agentic_workflow)
from app.chat.graph.combination_node import CombinationNode
from app.chat.graph.decomposition_node import DecompositionNode
from app.chat.graph.enhanced_state import EnhancedChatState
from app.chat.graph.processing_node import ProcessingNode
from app.chat.graph.response_node import ResponseNode
from app.services.llm import BaseLLMService
from app.services.llm.llm_config import NodeType
from app.services.prompts import PersonaType
from app.services.vectorstore import BaseVectorStoreService
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph


class TestConfigSchema:
    """Tests for the ConfigSchema class."""

    def test_config_schema_structure(self):
        """Test that ConfigSchema has the expected structure."""
        # Verify that ConfigSchema is a TypedDict with thread_id field
        assert hasattr(ConfigSchema, "__annotations__")
        assert "thread_id" in ConfigSchema.__annotations__


class TestCreateAgenticWorkflow:
    """Tests for the create_agentic_workflow function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock(spec=BaseLLMService)
        self.mock_vector_store = MagicMock(spec=BaseVectorStoreService)
        self.persona_type = PersonaType.SCRIBE
        self.memory = MemorySaver()

    @patch("app.chat.graph.agentic_workflow.StateGraph")
    @patch("app.chat.graph.agentic_workflow.DecompositionNode")
    @patch("app.chat.graph.agentic_workflow.ProcessingNode")
    @patch("app.chat.graph.agentic_workflow.CombinationNode")
    @patch("app.chat.graph.agentic_workflow.ResponseNode")
    @patch("app.chat.graph.agentic_workflow.PromptFactory")
    @patch("app.chat.graph.agentic_workflow.LLMConfiguration")
    def test_workflow_creation(
        self,
        mock_llm_config,
        mock_prompt_factory,
        mock_response_node,
        mock_combination_node,
        mock_processing_node,
        mock_decomposition_node,
        mock_state_graph
    ):
        """Test the creation of the agentic workflow."""
        # Setup
        mock_graph = MagicMock(spec=StateGraph)
        mock_state_graph.return_value = mock_graph
        
        mock_prompt = MagicMock()
        mock_prompt_factory.create_prompt.return_value = mock_prompt
        
        # Mock LLM services for each node
        mock_decomposition_llm = MagicMock(spec=BaseLLMService)
        mock_processing_llm = MagicMock(spec=BaseLLMService)
        mock_evaluation_llm = MagicMock(spec=BaseLLMService)
        mock_refinement_llm = MagicMock(spec=BaseLLMService)
        mock_answer_llm = MagicMock(spec=BaseLLMService)
        mock_combination_llm = MagicMock(spec=BaseLLMService)
        mock_response_llm = MagicMock(spec=BaseLLMService)
        
        # Configure LLMConfiguration.get_llm_service to return appropriate mocks
        def mock_get_llm_service(node_type, user_llm):
            if node_type == NodeType.DECOMPOSITION:
                return mock_decomposition_llm
            elif node_type == NodeType.PROCESSING:
                return mock_processing_llm
            elif node_type == NodeType.EVALUATION:
                return mock_evaluation_llm
            elif node_type == NodeType.REFINEMENT:
                return mock_refinement_llm
            elif node_type == NodeType.ANSWER:
                return mock_answer_llm
            elif node_type == NodeType.COMBINATION:
                return mock_combination_llm
            elif node_type == NodeType.RESPONSE:
                return mock_response_llm
        
        mock_llm_config.get_llm_service.side_effect = mock_get_llm_service
        
        # Mock node instances
        mock_decomposition_instance = MagicMock(spec=DecompositionNode)
        mock_processing_instance = MagicMock(spec=ProcessingNode)
        mock_combination_instance = MagicMock(spec=CombinationNode)
        mock_response_instance = MagicMock(spec=ResponseNode)
        
        mock_decomposition_node.return_value = mock_decomposition_instance
        mock_processing_node.return_value = mock_processing_instance
        mock_combination_node.return_value = mock_combination_instance
        mock_response_node.return_value = mock_response_instance
        
        # Execute
        result = create_agentic_workflow(
            user_llm_service=self.mock_llm,
            vector_store=self.mock_vector_store,
            persona_type=self.persona_type,
            memory=self.memory
        )
        
        # Verify
        # Check that StateGraph was created with correct parameters
        mock_state_graph.assert_called_once_with(EnhancedChatState, config_schema=ConfigSchema)
        
        # Check that PromptFactory was called
        mock_prompt_factory.create_prompt.assert_called_once_with(self.persona_type)
        
        # Check that LLMConfiguration was called for each node type
        mock_llm_config.get_llm_service.assert_any_call(NodeType.DECOMPOSITION, self.mock_llm)
        mock_llm_config.get_llm_service.assert_any_call(NodeType.PROCESSING, self.mock_llm)
        mock_llm_config.get_llm_service.assert_any_call(NodeType.EVALUATION, self.mock_llm)
        mock_llm_config.get_llm_service.assert_any_call(NodeType.REFINEMENT, self.mock_llm)
        mock_llm_config.get_llm_service.assert_any_call(NodeType.ANSWER, self.mock_llm)
        mock_llm_config.get_llm_service.assert_any_call(NodeType.COMBINATION, self.mock_llm)
        mock_llm_config.get_llm_service.assert_any_call(NodeType.RESPONSE, self.mock_llm)
        
        # Check that nodes were created with correct parameters
        mock_decomposition_node.assert_called_once_with(mock_decomposition_llm)
        mock_processing_node.assert_called_once_with(
            vector_store=self.mock_vector_store,
            retrieval_llm_service=mock_processing_llm,
            evaluation_llm_service=mock_evaluation_llm,
            refinement_llm_service=mock_refinement_llm,
            answer_llm_service=mock_answer_llm
        )
        mock_combination_node.assert_called_once_with(mock_combination_llm)
        mock_response_node.assert_called_once_with(mock_response_llm, mock_prompt)
        
        # Check that nodes were added to graph
        mock_graph.add_node.assert_any_call("decompose", mock_decomposition_instance)
        mock_graph.add_node.assert_any_call("process", mock_processing_instance)
        mock_graph.add_node.assert_any_call("combine", mock_combination_instance)
        mock_graph.add_node.assert_any_call("respond", mock_response_instance)
        
        # Check that edges were configured
        mock_graph.set_entry_point.assert_called_once_with("decompose")
        mock_graph.add_edge.assert_any_call("decompose", "process")
        mock_graph.add_edge.assert_any_call("process", "combine")
        mock_graph.add_edge.assert_any_call("combine", "respond")
        
        # Check that graph was compiled with memory
        mock_graph.compile.assert_called_once_with(checkpointer=self.memory)
        assert result == mock_graph.compile.return_value

    def test_workflow_creation_with_default_memory(self):
        """Test workflow creation with default memory."""
        # Setup - patch everything to avoid actual instantiation
        with patch("app.chat.graph.agentic_workflow.StateGraph") as mock_state_graph, \
             patch("app.chat.graph.agentic_workflow.DecompositionNode"), \
             patch("app.chat.graph.agentic_workflow.ProcessingNode"), \
             patch("app.chat.graph.agentic_workflow.CombinationNode"), \
             patch("app.chat.graph.agentic_workflow.ResponseNode"), \
             patch("app.chat.graph.agentic_workflow.PromptFactory"), \
             patch("app.chat.graph.agentic_workflow.LLMConfiguration"), \
             patch("app.chat.graph.agentic_workflow.MemorySaver") as mock_memory_saver:
            
            # Mock graph
            mock_graph = MagicMock(spec=StateGraph)
            mock_state_graph.return_value = mock_graph
            
            # Mock memory
            mock_memory = MagicMock(spec=MemorySaver)
            mock_memory_saver.return_value = mock_memory
            
            # Execute - pass None for memory
            create_agentic_workflow(
                user_llm_service=self.mock_llm,
                vector_store=self.mock_vector_store,
                persona_type=self.persona_type,
                memory=None
            )
            
            # Verify that a new MemorySaver was created
            mock_memory_saver.assert_called_once()
            
            # Verify that graph was compiled with the new memory
            mock_graph.compile.assert_called_once_with(checkpointer=mock_memory)
