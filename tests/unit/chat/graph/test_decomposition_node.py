"""Unit tests for the decomposition node."""
import json
from unittest.mock import MagicMock, patch

from app.chat.graph.decomposition_node import DecompositionNode
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.services.llm import BaseLLMService
from langchain_core.messages import HumanMessage


class TestDecompositionNode:
    """Tests for the DecompositionNode class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock(spec=BaseLLMService)
        self.node = DecompositionNode(self.mock_llm)

    def test_initialization(self):
        """Test that the node initializes correctly."""
        assert self.node.llm == self.mock_llm

    def test_empty_messages(self):
        """Test handling of empty messages list."""
        # Setup
        state = EnhancedChatState(messages=[])
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["original_query"] == ""
        assert result["query_complexity"] == "simple"
        assert result["subqueries"] == []

    def test_non_human_message(self):
        """Test handling of non-human messages."""
        # Setup
        state = EnhancedChatState(messages=[MagicMock(spec=HumanMessage)])
        state["messages"][0].__class__ = type('AIMessage', (), {})  # Mock as non-HumanMessage
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["original_query"] == ""
        assert result["query_complexity"] == "simple"
        assert result["subqueries"] == []

    def test_simple_query_analysis(self):
        """Test analysis of a simple query."""
        # Setup
        query = "What is the capital of France?"
        state = EnhancedChatState(messages=[HumanMessage(content=query)])
        
        # Mock LLM response for a simple query
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "query_type": "simple",
            "reasoning": "This is a straightforward factual question.",
            "subqueries": [query]
        })
        self.mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["original_query"] == query
        assert result["query_complexity"] == "simple"
        assert len(result["subqueries"]) == 1
        assert result["subqueries"][0].text == query
        assert result["subqueries"][0].status == "pending"
        self.mock_llm.invoke.assert_called_once()

    def test_complex_query_analysis(self):
        """Test analysis of a complex query."""
        # Setup
        query = "Compare the economic policies of the US and China, and explain their impact on global trade."
        state = EnhancedChatState(messages=[HumanMessage(content=query)])
        
        # Mock LLM response for a complex query
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "query_type": "complex",
            "reasoning": "This question requires comparing multiple aspects and analyzing impacts.",
            "subqueries": [
                "What are the key economic policies of the United States?",
                "What are the key economic policies of China?",
                "How do these policies affect global trade patterns?",
                "What are the major points of economic conflict between the US and China?"
            ]
        })
        self.mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["original_query"] == query
        assert result["query_complexity"] == "complex"
        assert len(result["subqueries"]) == 4
        for subquery in result["subqueries"]:
            assert isinstance(subquery, SubQuery)
            assert subquery.status == "pending"
        self.mock_llm.invoke.assert_called_once()

    def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Setup
        query = "What is the meaning of life?"
        state = EnhancedChatState(messages=[HumanMessage(content=query)])
        
        # Mock LLM to raise an exception
        self.mock_llm.invoke.side_effect = Exception("Test error")
        
        # Execute
        result = self.node(state)
        
        # Verify - should fall back to treating as simple query
        assert result["original_query"] == query
        assert result["query_complexity"] == "simple"
        assert len(result["subqueries"]) == 1
        assert result["subqueries"][0].text == query
        assert result["subqueries"][0].status == "pending"

    def test_malformed_llm_response(self):
        """Test handling of malformed LLM responses."""
        # Setup
        query = "What is quantum computing?"
        state = EnhancedChatState(messages=[HumanMessage(content=query)])
        
        # Mock LLM to return malformed JSON
        mock_response = MagicMock()
        mock_response.content = "This is not valid JSON"
        self.mock_llm.invoke.return_value = mock_response
        
        # Mock parse_json_response to raise ValueError
        with patch("app.chat.graph.decomposition_node.parse_json_response", side_effect=ValueError("Invalid JSON")):
            # Execute
            result = self.node(state)
            
            # Verify - should fall back to treating as simple query
            assert result["original_query"] == query
            assert result["query_complexity"] == "simple"
            assert len(result["subqueries"]) == 1
            assert result["subqueries"][0].text == query
            assert result["subqueries"][0].status == "pending"

    def test_empty_subqueries_handling(self):
        """Test handling of empty subqueries list in LLM response."""
        # Setup
        query = "What is artificial intelligence?"
        state = EnhancedChatState(messages=[HumanMessage(content=query)])
        
        # Mock LLM response with empty subqueries
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "query_type": "simple",
            "reasoning": "This is a simple question.",
            "subqueries": []
        })
        self.mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = self.node(state)
        
        # Verify - should fall back to using original query
        assert result["original_query"] == query
        assert result["query_complexity"] == "simple"
        assert len(result["subqueries"]) == 1
        assert result["subqueries"][0].text == query
        assert result["subqueries"][0].status == "pending"
