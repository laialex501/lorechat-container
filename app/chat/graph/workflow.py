"""Workflow configuration for chat graph."""
from typing import Optional

from app.chat.graph.nodes import create_nodes
from app.chat.graph.state import ChatState
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType
from app.services.vectorstore import BaseVectorStoreService
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from typing_extensions import TypedDict


class ConfigSchema(TypedDict):
    """Configuration schema for chat workflow."""
    thread_id: str


def create_chat_workflow(
    llm_service: BaseLLMService,
    vector_store: BaseVectorStoreService,
    persona_type: PersonaType = PersonaType.SCRIBE,
    memory: Optional[MemorySaver] = None
):
    """
    Create and configure the chat workflow graph.

    Args:
        llm_service: LLM service for response generation
        vector_store: Vector store for document retrieval
        persona_type: Type of chat persona to use
        memory: Optional memory saver for graph checkpointing

    Returns:
        Compiled workflow graph
    """
    # Create graph with our custom state and config schema
    workflow = StateGraph(ChatState, config_schema=ConfigSchema)

    # Create nodes
    nodes = create_nodes(llm_service, vector_store, persona_type)

    # Add nodes to graph
    for name, node in nodes.items():
        workflow.add_node(name, node)

    # Configure edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "respond")

    # If no memory provided, create one
    if memory is None:
        memory = MemorySaver()

    # Compile graph with memory
    return workflow.compile(checkpointer=memory)
