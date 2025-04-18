"""Unit tests for the response node."""
from unittest.mock import MagicMock

import pytest
from app.chat.graph.constants import SubqueryStatus
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.chat.graph.response_node import ResponseNode
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType
from langchain.schema.messages import AIMessageChunk
from langchain_core.messages import AIMessage, HumanMessage
from tests.conftest import MockPrompt


class TestResponseNode:
    """Tests for the ResponseNode class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock(spec=BaseLLMService)
        self.mock_prompt = MockPrompt()
        self.node = ResponseNode(self.mock_llm, self.mock_prompt)

    def test_initialization(self):
        """Test that the node initializes correctly."""
        assert self.node.llm_service == self.mock_llm
        assert self.node.prompt_template == self.mock_prompt

    @pytest.mark.asyncio
    async def test_response_with_combined_answer(self):
        """Test generating a response with a combined answer."""
        # Setup
        combined_answer = "Paris is the capital of France."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content="What is the capital of France?")],
            subqueries=subqueries,
            combined_answer=combined_answer
        )
        
        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response("Paris is the capital of France.")
        
        # Execute
        result = await self.node(state)
        
        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original message + response
        assert isinstance(result["messages"][1], AIMessage)
        assert "Paris is the capital of France" in result["messages"][1].content

    @pytest.mark.asyncio
    async def test_response_with_no_combined_answer(self):
        """Test generating a response when there is no combined answer."""
        # Setup
        state = EnhancedChatState(
            messages=[HumanMessage(content="What is the capital of France?")],
            subqueries=[],
            combined_answer=None
        )

        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response("I don't have enough information")

        # Execute
        result = await self.node(state)

        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original message + response
        assert isinstance(result["messages"][1], AIMessage)
        assert "I don't have enough information" in result["messages"][1].content or \
               "I couldn't find" in result["messages"][1].content

    @pytest.mark.asyncio
    async def test_response_with_no_sources(self):
        """Test generating a response when there are no sources."""
        # Setup
        combined_answer = "Paris is the capital of France."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=[]  # No sources
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content="What is the capital of France?")],
            subqueries=subqueries,
            combined_answer=combined_answer
        )
        
        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response("Paris is the capital of France.")
        
        # Execute
        result = await self.node(state)
        
        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original message + response
        assert isinstance(result["messages"][1], AIMessage)
        assert "Paris is the capital of France" in result["messages"][1].content

    @pytest.mark.asyncio
    async def test_response_with_multiple_sources(self):
        """Test generating a response with multiple sources."""
        # Setup
        combined_answer = "Paris is the capital of France, and Berlin is the capital of Germany."
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
            messages=[HumanMessage(content="Compare the capitals of France and Germany.")],
            subqueries=subqueries,
            combined_answer=combined_answer
        )
        
        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response(
            "Paris is the capital of France, and Berlin is the capital of Germany."
        )
        
        # Execute
        result = await self.node(state)
        
        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original message + response
        assert isinstance(result["messages"][1], AIMessage)
        assert "Paris is the capital of France" in result["messages"][1].content
        assert "Berlin is the capital of Germany" in result["messages"][1].content

    @pytest.mark.asyncio
    async def test_response_with_duplicate_sources(self):
        """Test generating a response with duplicate sources."""
        # Setup
        combined_answer = "Paris is the capital of France."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france", "https://example.com/france"]  # Duplicate source
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content="What is the capital of France?")],
            subqueries=subqueries,
            combined_answer=combined_answer
        )
        
        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response("Paris is the capital of France.")
        
        # Execute
        result = await self.node(state)
        
        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original message + response
        assert isinstance(result["messages"][1], AIMessage)

    @pytest.mark.asyncio
    async def test_response_with_empty_messages(self):
        """Test generating a response when there are no messages."""
        # Setup
        state = EnhancedChatState(
            messages=[],
            subqueries=[],
            combined_answer=None
        )
        
        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response("I don't have enough information")
        
        # Execute
        result = await self.node(state)
        
        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 1  # Just the response
        assert isinstance(result["messages"][0], AIMessage)
        assert "I don't have enough information" in result["messages"][0].content or \
               "I couldn't find" in result["messages"][0].content

    @pytest.mark.asyncio
    async def test_different_persona(self):
        """Test generating a response with a different persona."""
        # Setup
        combined_answer = "Paris is the capital of France."
        subqueries = [
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            )
        ]
        
        state = EnhancedChatState(
            messages=[HumanMessage(content="What is the capital of France?")],
            subqueries=subqueries,
            combined_answer=combined_answer
        )
        
        # Change the persona
        self.mock_prompt.persona_type = PersonaType.SCRIBE
        
        # Mock the astream method to return a simple string
        self.mock_llm.astream.return_value = self._mock_astream_response("Paris is the capital of France.")
        
        # Execute
        result = await self.node(state)
        
        # Verify
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original message + response
        assert isinstance(result["messages"][1], AIMessage)
        
    async def _mock_astream_response(self, content):
        """Helper to create a mock async generator for astream responses."""
        async def mock_generator():
            yield AIMessageChunk(content=content)
        return mock_generator()
