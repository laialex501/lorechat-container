"""Unit tests for the LLM base classes and enums."""
from unittest.mock import MagicMock

import pytest
from app.services.llm.llm_base import BaseLLMService
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import ChatGeneration
from langchain.schema.messages import AIMessage, AIMessageChunk, HumanMessage
from tests.conftest import MockLLMService


class TestBaseLLMService:
    """Tests for the BaseLLMService abstract base class."""

    def test_stream(self):
        """Test the _stream method."""
        # Setup
        service = MockLLMService(["First chunk", "Second chunk"])
        messages = [HumanMessage(content="Test message")]
        run_manager = MagicMock(spec=CallbackManagerForLLMRun)
        
        # Execute
        stream_gen = service._stream(messages, run_manager=run_manager)
        
        # Verify
        chunks = list(stream_gen)
        assert len(chunks) == 2
        assert isinstance(chunks[0], AIMessageChunk)
        assert chunks[0].content == "First chunk"
        assert isinstance(chunks[1], AIMessageChunk)
        assert chunks[1].content == "Second chunk"

    def test_generate(self):
        """Test the _generate method."""
        # Setup
        service = MockLLMService(["First chunk ", "Second chunk"])
        messages = [HumanMessage(content="Test message")]
        run_manager = MagicMock(spec=CallbackManagerForLLMRun)

        # Execute
        result = service._generate(messages, run_manager=run_manager)

        # Verify
        assert len(result.generations) == 1
        assert isinstance(result.generations[0], ChatGeneration)
        assert isinstance(result.generations[0].message, AIMessage)
        assert result.generations[0].message.content == "First chunk Second chunk"

    def test_abstract_generate_response(self):
        """Test that generate_response is abstract and must be implemented."""
        # Define a class that inherits from BaseLLMService but doesn't implement generate_response
        class IncompleteService(BaseLLMService):
            pass
        
        # Create an instance
        service = IncompleteService()
        
        # Verify that calling generate_response raises NotImplementedError
        with pytest.raises(NotImplementedError):
            next(service.generate_response([HumanMessage(content="Test")]))
