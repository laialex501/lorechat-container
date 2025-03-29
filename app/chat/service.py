"""Chat service implementation for LoreChat."""
from typing import Generator, List, Optional

from app.chat.graph.workflow import create_chat_workflow
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType
from app.services.vectorstore import BaseVectorStoreService
from langchain.schema.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatService:
    """
    ChatService provides a high-level interface for chat interactions using LangChain chains.
    It handles:
    1. Message history management and formatting
    2. Context retrieval and integration
    3. Response generation with proper streaming
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
        self.llm_service = llm_service
        self.vector_store = vector_store
        self.persona_type = persona_type

        # Create memory saver for graph checkpointing
        self.memory = MemorySaver()

        # Create workflow
        self._create_workflow()

    def _create_workflow(self) -> None:
        """Create or recreate the workflow with current settings."""
        self.workflow = create_chat_workflow(
            llm_service=self.llm_service,
            vector_store=self.vector_store,
            persona_type=self.persona_type,
            memory=self.memory
        )

    def change_persona(self, persona_type: PersonaType) -> None:
        """Change the chat persona."""
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
        # Format history and create input message
        formatted_history = self._format_history(history) if history else []
        input_message = HumanMessage(content=query)

        # Create config with thread ID
        config = {
            "configurable": {
                "thread_id": thread_id or "default"
            }
        }

        # Stream through workflow with config
        for event in self.workflow.stream(
            {"messages": formatted_history + [input_message]},
            config=config,
            stream_mode="values"
        ):
            # Extract just the response content
            if "messages" in event and event["messages"]:
                response = event["messages"][-1]
                if isinstance(response, AIMessage):
                    yield response.content
