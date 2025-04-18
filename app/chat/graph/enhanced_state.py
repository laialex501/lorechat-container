"""Enhanced state management for agentic retrieval system."""
from typing import List, Optional
from uuid import uuid4

from app.chat.graph.constants import QueryComplexity, SubqueryStatus
from langchain.schema import Document
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class SubQuery(BaseModel):
    """
    Represents a single subquery with its processing state.

    This class tracks all information related to a subquery, including
    its text, retrieved documents, processing status, and results.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))  # Unique identifier
    text: str  # The actual query text
    status: str = SubqueryStatus.PENDING
    retrieved_docs: List[Document] = Field(default_factory=list)
    refinement_count: int = 0
    result: str = ""
    sources: List[str] = Field(default_factory=list)  # Sources specific to this subquery


class EnhancedChatState(MessagesState, TypedDict, total=False):
    """
    Enhanced chat state with subquery tracking.

    This state object extends LangGraph's MessagesState to include additional
    fields needed for our agentic retrieval system.
    """
    subqueries: List[SubQuery]
    original_query: str
    query_complexity: str
    combined_answer: Optional[str]
    thread_id: str


def create_enhanced_chat_state(**kwargs) -> EnhancedChatState:
    """
    Create an EnhancedChatState with default values.
    
    Args:
        **kwargs: Optional values to override defaults
        
    Returns:
        An initialized EnhancedChatState dictionary
    """
    return {
        "messages": kwargs.get("messages", []),
        "subqueries": kwargs.get("subqueries", []),
        "original_query": kwargs.get("original_query", ""),
        "query_complexity": kwargs.get("query_complexity", QueryComplexity.SIMPLE),
        "combined_answer": kwargs.get("combined_answer", None),
        "thread_id": kwargs.get("thread_id", str(uuid4())),
    }
