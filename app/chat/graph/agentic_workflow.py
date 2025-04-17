"""Agentic workflow configuration for LoreChat."""
from typing import Optional

from app import logger
from app.chat.graph.combination_node import CombinationNode
from app.chat.graph.decomposition_node import DecompositionNode
from app.chat.graph.enhanced_state import EnhancedChatState
from app.chat.graph.processing_node import ProcessingNode
from app.chat.graph.response_node import ResponseNode
from app.services.llm import BaseLLMService
from app.services.llm.llm_config import LLMConfiguration, NodeType
from app.services.prompts import PersonaType, PromptFactory
from app.services.vectorstore import BaseVectorStoreService
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from typing_extensions import TypedDict


class ConfigSchema(TypedDict):
    """Configuration schema for chat workflow."""
    thread_id: str


def create_agentic_workflow(
    user_llm_service: BaseLLMService,
    vector_store: BaseVectorStoreService,
    persona_type: PersonaType = PersonaType.SCRIBE,
    memory: Optional[MemorySaver] = None
):
    """
    Create and configure the agentic retrieval workflow.

    This function creates a LangGraph workflow with nodes for query decomposition,
    processing, combination, and response. Each node uses an appropriate LLM based
    on its requirements.

    Args:
        user_llm_service: User-selected LLM service
        vector_store: Vector store for document retrieval
        persona_type: Type of chat persona to use
        memory: Optional memory saver for graph checkpointing

    Returns:
        Compiled workflow graph
    """
    # Create graph with our custom state and config schema
    logger.info("Creating agentic workflow graph")
    workflow = StateGraph(EnhancedChatState, config_schema=ConfigSchema)

    # Create prompt
    prompt = PromptFactory.create_prompt(persona_type)

    # Create nodes with appropriate LLMs
    logger.info("Creating workflow nodes with specialized LLMs")

    # Decomposition node
    decomposition_llm = LLMConfiguration.get_llm_service(
        NodeType.DECOMPOSITION, user_llm_service
    )
    decomposition_node = DecompositionNode(decomposition_llm)

    # Processing node with specialized LLMs for each step
    processing_llm = LLMConfiguration.get_llm_service(
        NodeType.PROCESSING, user_llm_service
    )
    evaluation_llm = LLMConfiguration.get_llm_service(
        NodeType.EVALUATION, user_llm_service
    )
    refinement_llm = LLMConfiguration.get_llm_service(
        NodeType.REFINEMENT, user_llm_service
    )
    answer_llm = LLMConfiguration.get_llm_service(
        NodeType.ANSWER, user_llm_service
    )

    processing_node = ProcessingNode(
        vector_store=vector_store,
        retrieval_llm_service=processing_llm,
        evaluation_llm_service=evaluation_llm,
        refinement_llm_service=refinement_llm,
        answer_llm_service=answer_llm
    )

    # Combination node
    combination_llm = LLMConfiguration.get_llm_service(
        NodeType.COMBINATION, user_llm_service
    )
    combination_node = CombinationNode(combination_llm)

    # Response node (uses user-selected LLM)
    response_llm = LLMConfiguration.get_llm_service(
        NodeType.RESPONSE, user_llm_service
    )
    response_node = ResponseNode(response_llm, prompt)

    # Add nodes to graph
    workflow.add_node("decompose", decomposition_node)
    workflow.add_node("process", processing_node)
    workflow.add_node("combine", combination_node)
    workflow.add_node("respond", response_node)

    # Configure edges
    workflow.set_entry_point("decompose")
    workflow.add_edge("decompose", "process")
    workflow.add_edge("process", "combine")
    workflow.add_edge("combine", "respond")

    # If no memory provided, create one
    if memory is None:
        memory = MemorySaver()

    # Compile graph with memory
    logger.info("Compiling workflow graph")
    return workflow.compile(checkpointer=memory)
