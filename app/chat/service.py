"""Chat service factory for LoreChat."""
from app import logger
from app.chat.agentic_service import AgenticChatService
from app.chat.base_service import BaseChatService
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType
from app.services.vectorstore import VectorStoreFactory


class ChatServiceFactory:
    """
    Factory for creating chat service instances.

    This factory abstracts the creation of chat services and handles
    dependencies like vector stores internally.
    """

    @staticmethod
    def create_chat_service(
        llm_service: BaseLLMService,
        persona_type: PersonaType = PersonaType.SCRIBE
    ) -> BaseChatService:
        """
        Create a chat service instance.

        Args:
            llm_service: LLM service for response generation
            persona_type: Type of chat persona to use

        Returns:
            A chat service implementation
        """
        logger.info(f"Creating chat service with persona: {persona_type}")

        # Get vector store internally
        vector_store = VectorStoreFactory.get_vector_store()

        # For now, always return AgenticChatService
        return AgenticChatService(
            llm_service=llm_service,
            vector_store=vector_store,
            persona_type=persona_type
        )


# For backward compatibility, re-export ChatService
ChatService = AgenticChatService
