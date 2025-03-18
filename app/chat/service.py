"""Chat service implementation for SiteChat."""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Union

from app.services.llm import BaseLLMService
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class BaseChatService(ABC):
    """Abstract base class for chat services."""
    
    @abstractmethod
    async def process_message(
        self,
        message: str,
        history: List[ChatMessage],
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Process a user message and return a response."""
        pass


class ChatService(BaseChatService):
    """Main chat service implementation."""
    
    def __init__(
        self,
        llm_service: BaseLLMService,
        vector_store: BaseVectorStoreService,
    ):
        """Initialize chat service with required dependencies."""
        self.llm_service = llm_service
        self.vector_store = vector_store

    async def process_message(
        self, 
        message: str, 
        history: List[ChatMessage],
        stream: bool = False,
        max_retries: int = 3
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Process a user message and return a response.
        
        Args:
            message: The user's input message
            history: List of previous chat messages
            max_retries: Maximum number of retries for failed API calls
            
        Returns:
            str: The assistant's response
        """
        try:
            # Format conversation history for LLM
            messages = []
            
            # Start context fetch concurrently while formatting messages
            context_task = asyncio.create_task(
                self.vector_store.get_relevant_context(message)
            )
            
            # Process history while context is being fetched
            history_to_process = (
                history[:-1] if history and history[-1].role == "user"
                else history
            )
            
            for msg in history_to_process:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            # Wait for context and add system message if available
            context = await context_task
            if context:
                system_msg = (
                    "You are a helpful assistant answering questions "
                    "about a website. Here is relevant information "
                    f"from the website:\n\n{context}\n\n"
                    "Use this information to help answer the question."
                )
                messages.insert(0, SystemMessage(content=system_msg))
            
            # Get response from LLM with retries
            if stream:
                # For streaming, we don't use retries since we can't 
                # retry mid-stream
                async def response_generator() -> AsyncGenerator[str, None]:
                    try:
                        async for chunk in self.llm_service.generate_response(
                            messages,
                            stream=True
                        ):
                            yield chunk
                    except Exception as e:
                        logging.error(
                            "Error in stream generation: %s",
                            str(e),
                            exc_info=True
                        )
                        yield (
                            "I apologize, but I encountered an error. "
                            "Please try again."
                        )
                return response_generator()
            else:
                # Non-streaming with retries
                for attempt in range(max_retries):
                    try:
                        response = await self.llm_service.generate_response(
                            messages
                        )
                        return response
                    except Exception as e:
                        if attempt == max_retries - 1:  # Last attempt
                            logging.error(
                                "Max retries reached. Last error: %s",
                                str(e),
                                exc_info=True
                            )
                            raise
                        # Exponential backoff
                        await asyncio.sleep(1 * (attempt + 1))
            
        except Exception as e:
            logging.error(
                "Error processing message: %s",
                str(e),
                exc_info=True
            )
            return (
                "I apologize, but I encountered an error processing your "
                "message. Please try again."
            )
