"""Agentic chat service implementation for LoreChat."""
import asyncio
from typing import Generator, List, Optional

from app import logger
from app.chat.base_service import BaseChatService, ChatMessage
from app.chat.graph.agentic_workflow import create_agentic_workflow
from app.services.llm import BaseLLMService
from app.services.llm.parser import normalize_llm_content
from app.services.prompts import PersonaType
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver


class AgenticChatService(BaseChatService):
    """
    AgenticChatService provides a high-level interface for chat interactions using
    the agentic retrieval system. It handles:
    1. Message history management and formatting
    2. Query decomposition and parallel processing
    3. Result combination and response generation
    4. Persona-based interactions
    """

    def __init__(
        self,
        llm_service: BaseLLMService,
        vector_store: BaseVectorStoreService,
        persona_type: PersonaType = PersonaType.SCRIBE
    ):
        """Initialize chat service with required dependencies."""
        # Store services and persona
        logger.info("Initializing AgenticChatService")
        self.llm_service = llm_service
        self.vector_store = vector_store
        self.persona_type = persona_type

        # Create memory saver for graph checkpointing
        self.memory = MemorySaver()

        # Create workflow
        self._create_workflow()

    def _create_workflow(self) -> None:
        """Create or recreate the workflow with current settings."""
        logger.info("Creating agentic workflow")
        self.workflow = create_agentic_workflow(
            user_llm_service=self.llm_service,
            vector_store=self.vector_store,
            persona_type=self.persona_type,
            memory=self.memory
        )

    def change_persona(self, persona_type: PersonaType) -> None:
        """Change the chat persona."""
        logger.info(f"Changing persona to {persona_type}")
        self.persona_type = persona_type
        self._create_workflow()

    def _format_history(self, history: List[ChatMessage]) -> List[BaseMessage]:
        """Format chat history into LangChain messages."""
        messages = []
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        return messages

    async def process_message_async(
        self,
        query: str,
        history: Optional[List[ChatMessage]] = None,
        thread_id: Optional[str] = None
    ) -> Generator:
        """
        Process a message asynchronously and return a streaming response.
 
        Args:
            query: Current user query
            history: Optional chat history
            thread_id: Optional thread ID for conversation tracking
        
        Returns:
            Generator for streaming response
        """
        # Format history and create input message
        formatted_history = self._format_history(history) if history else []
        input_message = HumanMessage(content=query)

        # Create config with thread ID
        config = {
            "configurable": {
                "thread_id": thread_id or "default"
            }
        }

        logger.info(f"Processing message with thread_id: {thread_id or 'default'}")

        # Stream through workflow with config
        async for event in self.workflow.astream(
            {"messages": formatted_history + [input_message]},
            config=config,
            stream_mode="values"
        ):
            # Extract just the response content
            if "messages" in event and event["messages"]:
                response = event["messages"][-1]
                if isinstance(response, AIMessage):
                    # Extract and normalize content from AIMessage
                    content = response.content
                    yield normalize_llm_content(content)

    def process_message(
        self,
        query: str,
        history: Optional[List[ChatMessage]] = None,
        thread_id: Optional[str] = None
    ) -> Generator:
        """
        Process a message and return a streaming response.

        This is a synchronous wrapper around the async version.

        Args:
            query: Current user query
            history: Optional chat history
            thread_id: Optional thread ID for conversation tracking

        Returns:
            Generator for streaming response
        """

        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Create async generator
        async_gen = self.process_message_async(query, history, thread_id)

        # Convert async generator to sync generator
        while True:
            try:
                next_item = loop.run_until_complete(async_gen.__anext__())
                yield next_item
            except StopAsyncIteration:
                break
