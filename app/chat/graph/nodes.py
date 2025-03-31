"""Node implementations for chat graph."""
from typing import Any, Dict

from app.chat.graph.response_node import ResponseNode
from app.chat.graph.retrieve_node import RetrieveNode
from app.services.llm import BaseLLMService
from app.services.prompts import PersonaType, PromptFactory
from app.services.vectorstore import BaseVectorStoreService


def create_nodes(
    llm_service: BaseLLMService,
    vector_store: BaseVectorStoreService,
    persona_type: PersonaType = PersonaType.SCRIBE
) -> Dict[str, Any]:
    """
    Create graph nodes for chat workflow.

    Args:
        llm_service: LLM service for response generation
        vector_store: Vector store for document retrieval
        persona_type: Type of chat persona to use

    Returns:
        Dictionary of node functions
    """
    # Initialize prompt
    prompt = PromptFactory.create_prompt(persona_type)

    # Each node function has dependencies injected by LangGraph
    return {
        "retrieve": RetrieveNode(vector_store),
        "respond": ResponseNode(llm_service, prompt)
    }
