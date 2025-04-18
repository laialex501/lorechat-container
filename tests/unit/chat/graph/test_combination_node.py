"""Unit tests for the combination node."""
from unittest.mock import MagicMock

from app.chat.graph.combination_node import CombinationNode
from app.chat.graph.constants import SubqueryStatus
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.services.llm import BaseLLMService
from langchain_core.messages import HumanMessage


class TestCombinationNode:
    """Tests for the CombinationNode class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock(spec=BaseLLMService)
        self.node = CombinationNode(self.mock_llm)

    def test_initialization(self):
        """Test that the node initializes correctly."""
        assert self.node.llm == self.mock_llm

    def test_combine_single_subquery(self):
        """Test combining results from a single subquery."""
        # Setup
        original_query = "What is the capital of France?"
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content=original_query)],
            subqueries=subqueries,
            original_query=original_query
        )
        
        # Mock LLM response - for a single subquery, it should just return the result
        mock_response = MagicMock()
        mock_response.content = "The capital of France is Paris."
        self.mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["combined_answer"] == "The capital of France is Paris."
        # LLM should not be called for a single subquery
        self.mock_llm.invoke.assert_not_called()

    def test_combine_multiple_subqueries(self):
        """Test combining results from multiple subqueries."""
        # Setup
        original_query = "Compare the capitals of France and Germany."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            ),
            SubQuery(
                text="What is the capital of Germany?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of Germany is Berlin.",
                sources=["https://example.com/germany"]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content=original_query)],
            subqueries=subqueries,
            original_query=original_query
        )
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Paris is the capital of France, while Berlin is the capital of Germany."
        self.mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["combined_answer"] == "Paris is the capital of France, while Berlin is the capital of Germany."
        self.mock_llm.invoke.assert_called_once()
        
        # Check that the prompt contains the original query and all subquery results
        prompt = self.mock_llm.invoke.call_args[0][0]
        assert original_query in prompt
        assert "The capital of France is Paris." in prompt
        assert "The capital of Germany is Berlin." in prompt

    def test_combine_with_incomplete_subqueries(self):
        """Test combining results when some subqueries are incomplete."""
        # Setup
        original_query = "Compare the capitals of France, Germany, and Italy."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            ),
            SubQuery(
                text="What is the capital of Germany?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of Germany is Berlin.",
                sources=["https://example.com/germany"]
            ),
            SubQuery(
                text="What is the capital of Italy?",
                status=SubqueryStatus.FAILED,  # This subquery failed
                result="",
                sources=[]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content=original_query)],
            subqueries=subqueries,
            original_query=original_query
        )
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "Paris is the capital of France, and Berlin is the capital of Germany.\
          I don't have information about Italy's capital."
        self.mock_llm.invoke.return_value = mock_response
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["combined_answer"] == "Paris is the capital of France, and Berlin is the capital of Germany.\
          I don't have information about Italy's capital."
        self.mock_llm.invoke.assert_called_once()
        
        # Check that the prompt contains the subquery with empty result
        prompt = self.mock_llm.invoke.call_args[0][0]
        assert "What is the capital of Italy?" in prompt
        assert "Answer: " in prompt  # Empty result after "Answer: "

    def test_combine_with_empty_subqueries(self):
        """Test combining results when there are no subqueries."""
        # Setup
        original_query = "What is the capital of France?"
        state = EnhancedChatState(
            messages=[HumanMessage(content=original_query)],
            subqueries=[],
            original_query=original_query
        )
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["combined_answer"] == "I don't have enough information to answer your question."
        self.mock_llm.invoke.assert_not_called()

    def test_combine_with_all_failed_subqueries(self):
        """Test combining results when all subqueries failed."""
        # Setup
        original_query = "What is the capital of France?"
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.FAILED,
                result="",
                sources=[]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content=original_query)],
            subqueries=subqueries,
            original_query=original_query
        )
        
        # Execute
        result = self.node(state)
        
        # Verify
        assert result["combined_answer"] == "I couldn't find the information to answer your question."
        self.mock_llm.invoke.assert_not_called()

    def test_llm_error_handling(self):
        """Test handling of LLM errors."""
        # Setup
        original_query = "Compare the capitals of France and Germany."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            ),
            SubQuery(
                text="What is the capital of Germany?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of Germany is Berlin.",
                sources=["https://example.com/germany"]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content=original_query)],
            subqueries=subqueries,
            original_query=original_query
        )
        
        # Mock LLM to raise an exception
        self.mock_llm.invoke.side_effect = Exception("Test error")
        
        # Execute
        result = self.node(state)
        
        # Verify - should fall back to a simple combination of results
        assert "Paris" in result["combined_answer"]
        assert "Berlin" in result["combined_answer"]
        self.mock_llm.invoke.assert_called_once()
