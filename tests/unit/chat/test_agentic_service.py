"""Unit tests for the agentic chat service."""
from typing import Any, AsyncGenerator
from unittest.mock import MagicMock, patch

import pytest
from app.chat.agentic_service import AgenticChatService
from app.chat.base_service import BaseChatService, ChatMessage
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema.messages import AIMessage, HumanMessage


async def mock_async_generator(values: list) -> AsyncGenerator[Any, None]:
    """Helper function to create a mock async generator for testing."""
    for value in values:
        yield value


class TestAgenticChatService:
    """Tests for the AgenticChatService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock(spec=BaseLLMService)
        self.mock_vector_store = MagicMock(spec=BaseVectorStoreService)
        
        # Patch the create_workflow method to avoid actual workflow creation
        self.patcher = patch.object(AgenticChatService, '_create_workflow')
        self.mock_create_workflow = self.patcher.start()
        
        # Create the service
        self.service = AgenticChatService(
            llm_service=self.mock_llm,
            vector_store=self.mock_vector_store,
            persona_type=PersonaType.SCRIBE
        )
        
        # Mock the workflow
        self.mock_workflow = MagicMock()
        self.service.workflow = self.mock_workflow

    def teardown_method(self):
        """Tear down test fixtures."""
        self.patcher.stop()

    def test_initialization(self):
        """Test initialization of AgenticChatService."""
        assert self.service.llm_service == self.mock_llm
        assert self.service.vector_store == self.mock_vector_store
        assert self.service.persona_type == PersonaType.SCRIBE
        assert hasattr(self.service, 'memory')
        self.mock_create_workflow.assert_called_once()

    def test_create_workflow(self):
        """Test the _create_workflow method."""
        # Stop the patcher to test the actual method
        self.patcher.stop()
        
        # Patch the create_agentic_workflow function
        with patch('app.chat.agentic_service.create_agentic_workflow') as mock_create_workflow:
            mock_workflow = MagicMock()
            mock_create_workflow.return_value = mock_workflow
            
            # Create a new service to trigger _create_workflow
            service = AgenticChatService(
                llm_service=self.mock_llm,
                vector_store=self.mock_vector_store,
                persona_type=PersonaType.SCRIBE
            )
            
            # Verify
            mock_create_workflow.assert_called_once_with(
                user_llm_service=self.mock_llm,
                vector_store=self.mock_vector_store,
                persona_type=PersonaType.SCRIBE,
                memory=service.memory
            )
            assert service.workflow == mock_workflow
        
        # Restart the patcher for other tests
        self.patcher.start()

    def test_change_persona(self):
        """Test the change_persona method."""
        # Execute
        self.service.change_persona(PersonaType.DEVIL)
        
        # Verify
        assert self.service.persona_type == PersonaType.DEVIL
        self.mock_create_workflow.assert_called()

    def test_format_history(self):
        """Test the _format_history method."""
        # Setup
        history = [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there"),
            ChatMessage(role="user", content="How are you?")
        ]
        
        # Execute
        result = self.service._format_history(history)
        
        # Verify
        assert len(result) == 3
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == "Hello"
        assert isinstance(result[1], AIMessage)
        assert result[1].content == "Hi there"
        assert isinstance(result[2], HumanMessage)
        assert result[2].content == "How are you?"

    @pytest.mark.asyncio
    async def test_process_message_async(self):
        """Test the process_message_async method."""
        # Setup
        query = "What is the capital of France?"
        history = [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there")
        ]
        thread_id = "test-thread-id"
        
        # Mock the workflow's astream method to return a mock async generator
        mock_response = {"messages": [AIMessage(content="Paris is the capital of France.")]}
        self.mock_workflow.astream.return_value = mock_async_generator([mock_response])
        
        # Call the method and collect results
        result = []
        async for chunk in self.service.process_message_async(query, history, thread_id):
            result.append(chunk)
        
        # Verify we got the expected result
        assert result == ["Paris is the capital of France."]
        
        # Verify astream was called with correct parameters
        self.mock_workflow.astream.assert_called_once()
        args, kwargs = self.mock_workflow.astream.call_args
        assert "messages" in args[0]
        assert len(args[0]["messages"]) == 3  # 2 from history + 1 new message
        assert isinstance(args[0]["messages"][2], HumanMessage)
        assert args[0]["messages"][2].content == query
        assert kwargs["config"] == {"configurable": {"thread_id": thread_id}}
        assert kwargs["stream_mode"] == "values"

    def test_process_message(self):
        """Test the process_message method."""
        # Setup
        query = "What is the capital of France?"
        
        # Mock the async version
        async def mock_async_gen():
            yield "The capital of France is "
            yield "Paris."
        
        with patch.object(self.service, 'process_message_async', return_value=mock_async_gen()):
            # Execute
            result = list(self.service.process_message(query))
            
            # Verify
            assert result == ["The capital of France is ", "Paris."]

    @pytest.mark.asyncio
    async def test_process_message_async_with_empty_response(self):
        """Test process_message_async with an empty response."""
        # Setup
        query = "What is the capital of France?"
        
        # Mock the workflow's astream method to return a mock async generator with empty messages
        mock_response = {"messages": []}
        self.mock_workflow.astream.return_value = mock_async_generator([mock_response])
        
        # Call the method and collect results
        result = []
        async for chunk in self.service.process_message_async(query):
            result.append(chunk)
        
        # Verify we got no results
        assert result == []
        
        # Verify astream was called
        self.mock_workflow.astream.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_async_with_non_ai_message(self):
        """Test process_message_async with a non-AI message."""
        # Setup
        query = "What is the capital of France?"
        
        # Mock the workflow's astream method to return a mock async generator with non-AI message
        mock_response = {"messages": [HumanMessage(content="This is not an AI message")]}
        self.mock_workflow.astream.return_value = mock_async_generator([mock_response])
        
        # Call the method and collect results
        result = []
        async for chunk in self.service.process_message_async(query):
            result.append(chunk)
        
        # Verify we got no results (since the message is not an AIMessage)
        assert result == []
        
        # Verify astream was called
        self.mock_workflow.astream.assert_called_once()

    def test_is_subclass_of_base_service(self):
        """Test that AgenticChatService is a subclass of BaseChatService."""
        assert issubclass(AgenticChatService, BaseChatService)
