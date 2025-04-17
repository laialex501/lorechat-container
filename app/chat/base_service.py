"""Base chat service interface for LoreChat."""
from abc import ABC, abstractmethod
from typing import Generator, List, Optional

from app.services.prompts import PersonaType
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class BaseChatService(ABC):
    """
    Abstract base class for chat services.

    This defines the interface that all chat service implementations must follow.
    It provides a common API for chat interactions regardless of the underlying
    implementation details.
    """

    @abstractmethod
    def process_message(
        self,
        query: str,
        history: Optional[List[ChatMessage]] = None,
        thread_id: Optional[str] = None
    ) -> Generator:
        """
        Process a message and return a streaming response.

        Args:
            query: Current user query
            history: Optional chat history
            thread_id: Optional thread ID for conversation tracking

        Returns:
            Generator for streaming response
        """
        pass

    @abstractmethod
    def change_persona(self, persona_type: PersonaType) -> None:
        """
        Change the chat persona.

        Args:
            persona_type: New persona type to use
        """
        pass
