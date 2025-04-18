"""Unit tests for the base chat service."""
from abc import ABC
from typing import Generator, List, Optional

import pytest
from app.chat.base_service import BaseChatService, ChatMessage
from app.services.prompts import PersonaType


class TestChatMessage:
    """Tests for the ChatMessage model."""

    def test_initialization(self):
        """Test initialization of ChatMessage."""
        # Execute
        message = ChatMessage(role="user", content="Hello, world!")
        
        # Verify
        assert message.role == "user"
        assert message.content == "Hello, world!"

    def test_model_validation(self):
        """Test that ChatMessage validates input."""
        # Verify that both role and content are required
        with pytest.raises(ValueError):
            ChatMessage(role="user")
        
        with pytest.raises(ValueError):
            ChatMessage(content="Hello, world!")


class MockChatService(BaseChatService):
    """Mock implementation of BaseChatService for testing."""
    
    def __init__(self):
        """Initialize mock service."""
        self.persona_type = PersonaType.SCRIBE
    
    def process_message(
        self,
        query: str,
        history: Optional[List[ChatMessage]] = None,
        thread_id: Optional[str] = None
    ) -> Generator:
        """Mock implementation of process_message."""
        yield "Mock response"
    
    def change_persona(self, persona_type: PersonaType) -> None:
        """Mock implementation of change_persona."""
        self.persona_type = persona_type


class TestBaseChatService:
    """Tests for the BaseChatService abstract base class."""

    def test_is_abstract_base_class(self):
        """Test that BaseChatService is an abstract base class."""
        assert issubclass(BaseChatService, ABC)

    def test_abstract_methods(self):
        """Test that abstract methods must be implemented."""
        # Define a class that inherits from BaseChatService but doesn't implement methods
        class IncompleteChatService(BaseChatService):
            pass
        
        # Verify that instantiating it raises TypeError
        with pytest.raises(TypeError):
            IncompleteChatService()

    def test_concrete_implementation(self):
        """Test that a concrete implementation can be instantiated."""
        # Execute
        service = MockChatService()

        # Verify
        assert isinstance(service, BaseChatService)
        assert service.persona_type == PersonaType.SCRIBE

    def test_process_message(self):
        """Test the process_message method."""
        # Setup
        service = MockChatService()

        # Execute
        response_gen = service.process_message("Hello, world!")

        # Verify
        response = list(response_gen)
        assert response == ["Mock response"]

    def test_change_persona(self):
        """Test the change_persona method."""
        # Setup
        service = MockChatService()

        # Execute
        service.change_persona(PersonaType.DEVIL)

        # Verify
        assert service.persona_type == PersonaType.DEVIL
