"""Chat service implementation for LoreChat."""
from typing import Generator, List

from app.services.llm import BaseLLMService
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema.messages import (AIMessage, BaseMessage, HumanMessage,
                                       SystemMessage)
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatService:
    """
    ChatService provides a high-level interface for chat interactions.
    It handles:
    1. Message history management and formatting
    2. Context retrieval and integration
    3. Response generation with proper streaming
    """
    
    def __init__(
        self,
        llm_service: BaseLLMService,
        vector_store: BaseVectorStoreService,
    ):
        """Initialize chat service with required dependencies."""
        self.llm_service = llm_service
        self.vector_store = vector_store

    def get_messages(
        self,
        query: str,
        history: List[ChatMessage]
    ) -> List[BaseMessage]:
        """
        Format messages for LLM with context.
        
        Args:
            query: Current user query
            history: Complete chat history
            
        Returns:
            List of formatted messages with context
        """
        messages = []
        
        # Add context if available
        context = self.vector_store.get_relevant_context(query)
        if context:
            messages.append(SystemMessage(
                content=(
                    "You are a helpful assistant answering questions "
                    "about a website. Here is relevant information "
                    f"from the website:\n\n{context}\n\n"
                    "Use this information to help answer the question."
                )
            ))
        
        # Add conversation history
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        return messages

    def process_message(
        self,
        query: str,
        history: List[ChatMessage]
    ) -> Generator:
        """
        Process a message and return a streaming response.
        
        Args:
            query: Current user query
            history: Complete chat history
            
        Returns:
            Generator for streaming response
        """
        # Format messages with context
        messages = self.get_messages(query, history)
        
        # Generate streaming response
        return self.llm_service.generate_response(messages)
