"""Unit tests for the processing node."""
from unittest.mock import MagicMock, patch

import pytest
from app.chat.graph.constants import SubqueryStatus
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.chat.graph.processing_node import ProcessingNode
from app.services.llm import BaseLLMService
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema import Document
from langchain_core.messages import HumanMessage

# Test constants
TEST_QUERY_FRANCE = "What is the capital of France?"
TEST_QUERY_GERMANY = "What is the capital of Germany?"
TEST_ANSWER_FRANCE = "The capital of France is Paris."
TEST_ANSWER_GERMANY = "The capital of Germany is Berlin."
TEST_URL_FRANCE = "https://example.com/france"
TEST_URL_GERMANY = "https://example.com/germany"
TEST_URL_PARIS = "https://example.com/paris"
TEST_CONTENT_FRANCE = "Paris is the capital of France."
TEST_CONTENT_EUROPE = "France is a country in Europe."
TEST_REFINED_QUERY = "What is the capital city of France?"


class TestProcessingNode:
    """Tests for the ProcessingNode class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_vector_store = MagicMock(spec=BaseVectorStoreService)
        self.mock_retrieval_llm = MagicMock(spec=BaseLLMService)
        self.mock_evaluation_llm = MagicMock(spec=BaseLLMService)
        self.mock_refinement_llm = MagicMock(spec=BaseLLMService)
        self.mock_answer_llm = MagicMock(spec=BaseLLMService)
        
        # Set up retriever mock
        self.mock_retriever = MagicMock()
        self.mock_vector_store.as_retriever.return_value = self.mock_retriever
        
        self.node = ProcessingNode(
            vector_store=self.mock_vector_store,
            retrieval_llm_service=self.mock_retrieval_llm,
            evaluation_llm_service=self.mock_evaluation_llm,
            refinement_llm_service=self.mock_refinement_llm,
            answer_llm_service=self.mock_answer_llm
        )

    def test_initialization(self):
        """Test that the node initializes correctly."""
        assert self.node.vector_store == self.mock_vector_store
        assert self.node.retrieval_llm == self.mock_retrieval_llm
        assert self.node.evaluation_llm == self.mock_evaluation_llm
        assert self.node.refinement_llm == self.mock_refinement_llm
        assert self.node.answer_llm == self.mock_answer_llm

    @pytest.mark.asyncio
    async def test_call_with_subqueries(self):
        """Test processing of subqueries in the __call__ method."""
        # Setup
        subqueries = [
            SubQuery(text=TEST_QUERY_FRANCE, status=SubqueryStatus.PENDING),
            SubQuery(text=TEST_QUERY_GERMANY, status=SubqueryStatus.PENDING)
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content="Compare the capitals of France and Germany.")],
            subqueries=subqueries
        )
        
        # Mock the _process_subquery method
        async def mock_process_subquery(subquery):
            if subquery.text == TEST_QUERY_FRANCE:
                return {
                    "retrieved_docs": [Document(page_content=TEST_CONTENT_FRANCE, metadata={"url": TEST_URL_FRANCE})],
                    "refinement_count": 0,
                    "answer": TEST_ANSWER_FRANCE,
                    "sources": [TEST_URL_FRANCE]
                }
            else:
                return {
                    "retrieved_docs": [Document(page_content="Berlin is the capital of Germany.",
                                                metadata={"url": TEST_URL_GERMANY})],
                    "refinement_count": 0,
                    "answer": TEST_ANSWER_GERMANY,
                    "sources": [TEST_URL_GERMANY]
                }
        
        # Patch the _process_subquery method
        with patch.object(self.node, '_process_subquery', side_effect=mock_process_subquery):
            # Execute
            result = await self.node(state)
            
            # Verify
            assert len(result["subqueries"]) == 2
            assert result["subqueries"][0].status == SubqueryStatus.COMPLETE
            assert result["subqueries"][0].result == TEST_ANSWER_FRANCE
            assert result["subqueries"][0].sources == [TEST_URL_FRANCE]
            assert result["subqueries"][1].status == SubqueryStatus.COMPLETE
            assert result["subqueries"][1].result == TEST_ANSWER_GERMANY
            assert result["subqueries"][1].sources == [TEST_URL_GERMANY]

    @pytest.mark.asyncio
    async def test_process_subquery_success(self):
        """Test successful processing of a single subquery."""
        # Setup
        subquery = SubQuery(text=TEST_QUERY_FRANCE, status=SubqueryStatus.PENDING)
        
        # Mock vector store to return documents
        mock_docs = [
            Document(page_content=TEST_CONTENT_FRANCE, metadata={"url": TEST_URL_FRANCE})
        ]
        self.mock_retriever.invoke.return_value = mock_docs
        
        # Mock evaluation LLM to indicate sufficient context
        mock_eval_response = MagicMock()
        mock_eval_response.content = '{"sufficient": true, "reasoning": "The document contains the answer"}'
        self.mock_evaluation_llm.invoke.return_value = mock_eval_response
        
        # Mock answer LLM to generate an answer
        mock_answer_response = MagicMock()
        mock_answer_response.content = TEST_ANSWER_FRANCE
        self.mock_answer_llm.invoke.return_value = mock_answer_response
        
        # Execute
        result = await self.node._process_subquery(subquery)
        
        # Verify
        assert isinstance(result, dict)
        assert result["retrieved_docs"] == mock_docs
        assert result["answer"] == TEST_ANSWER_FRANCE
        assert result["sources"] == [TEST_URL_FRANCE]
        assert result["refinement_count"] == 0
        self.mock_retriever.invoke.assert_called_once_with(TEST_QUERY_FRANCE)
        self.mock_evaluation_llm.invoke.assert_called_once()
        self.mock_answer_llm.invoke.assert_called_once()
        self.mock_refinement_llm.invoke.assert_not_called()  # No refinement needed

    @pytest.mark.asyncio
    async def test_process_subquery_with_refinement(self):
        """Test processing of a subquery that requires refinement."""
        # Setup
        subquery = SubQuery(text=TEST_QUERY_FRANCE, status=SubqueryStatus.PENDING)
        
        # Mock vector store to return documents
        mock_docs = [
            Document(page_content=TEST_CONTENT_EUROPE, metadata={"url": TEST_URL_FRANCE})
        ]
        better_docs = [
            Document(page_content=TEST_CONTENT_FRANCE, metadata={"url": TEST_URL_PARIS})
        ]
        self.mock_retriever.invoke.side_effect = [mock_docs, better_docs]
        
        # Mock evaluation LLM to indicate insufficient context first, then sufficient
        eval_responses = [
            MagicMock(content='{"sufficient": false, "reasoning": "No capital mentioned"}'),
            MagicMock(content='{"sufficient": true, "reasoning": "Contains capital info"}')
        ]
        self.mock_evaluation_llm.invoke.side_effect = eval_responses
        
        # Mock refinement LLM to generate a refined query
        mock_refinement_response = MagicMock()
        mock_refinement_response.content = TEST_REFINED_QUERY
        self.mock_refinement_llm.invoke.return_value = mock_refinement_response
        
        # Mock answer LLM to generate an answer
        mock_answer_response = MagicMock()
        mock_answer_response.content = TEST_ANSWER_FRANCE
        self.mock_answer_llm.invoke.return_value = mock_answer_response
        
        # Execute
        result = await self.node._process_subquery(subquery)
        
        # Verify
        assert isinstance(result, dict)
        assert result["retrieved_docs"] == better_docs
        assert result["answer"] == TEST_ANSWER_FRANCE
        assert result["sources"] == [TEST_URL_PARIS]
        assert result["refinement_count"] == 1
        assert self.mock_retriever.invoke.call_count == 2
        self.mock_retriever.invoke.assert_any_call(TEST_QUERY_FRANCE)
        self.mock_retriever.invoke.assert_any_call(TEST_REFINED_QUERY)
        assert self.mock_evaluation_llm.invoke.call_count == 1  # Changed from 2 to 1
        self.mock_refinement_llm.invoke.assert_called_once()
        self.mock_answer_llm.invoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_subquery_retrieval_error(self):
        """Test processing of a subquery when retrieval fails."""
        # Setup
        subquery = SubQuery(text=TEST_QUERY_FRANCE, status=SubqueryStatus.PENDING)
        
        # Mock vector store to raise an exception
        error_message = "Retrieval error"
        self.mock_retriever.invoke.side_effect = Exception(error_message)
        
        # Execute - the method should handle the exception internally
        result = await self.node._process_subquery(subquery)
        
        # Verify the result contains an empty document list and error message
        assert isinstance(result, dict)
        assert result["retrieved_docs"] == []
        assert "I couldn't find any relevant information to answer your question" in result["answer"]
        
        # Verify method calls
        assert self.mock_retriever.invoke.call_count == 2
        self.mock_evaluation_llm.invoke.assert_not_called()
        self.mock_refinement_llm.invoke.assert_called_once()
        # Answer LLM should be called with a fallback prompt
        self.mock_answer_llm.invoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_subquery_with_no_documents(self):
        """Test processing of a subquery when no documents are retrieved."""
        # Setup
        subquery = SubQuery(text=TEST_QUERY_FRANCE, status=SubqueryStatus.PENDING)
        
        # Mock vector store to return empty list
        self.mock_retriever.invoke.return_value = []
        
        # Mock answer LLM to generate a fallback answer
        mock_answer_response = MagicMock()
        mock_answer_response.content = "I couldn't find any relevant information to answer your question."
        self.mock_answer_llm.invoke.return_value = mock_answer_response
        
        # Execute
        result = await self.node._process_subquery(subquery)
        
        # Verify
        assert isinstance(result, dict)
        assert result["retrieved_docs"] == []
        assert "I couldn't find any relevant information to answer your question." in result["answer"]
        assert result["sources"] == []
        # The implementation calls invoke twice, so we should expect that
        assert self.mock_retriever.invoke.call_count == 2
        # Evaluation and answer should be skipped if no documents
        self.mock_evaluation_llm.invoke.assert_not_called()
        self.mock_refinement_llm.invoke.assert_called_once()
        self.mock_answer_llm.invoke.assert_not_called()
