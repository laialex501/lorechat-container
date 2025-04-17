"""Enhanced state management for agentic retrieval system."""
from typing import List, Optional
from uuid import uuid4

from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class SubQuery(BaseModel):
    """
    Represents a single subquery with its processing state.

    This class tracks all information related to a subquery, including
    its text, retrieved documents, processing status, and results.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))  # Unique identifier
    text: str  # The actual query text
    status: str = "pending"  # pending, processing, complete, failed
    retrieved_docs: List[Document] = Field(default_factory=list)
    refinement_count: int = 0
    result: str = ""
    sources: List[str] = Field(default_factory=list)  # Sources specific to this subquery


class EnhancedChatState(MessagesState):
    """
    Enhanced chat state with subquery tracking.

    This state object extends LangGraph's MessagesState to include additional
    fields needed for our agentic retrieval system.
    """
    messages: List[BaseMessage] = Field(default_factory=list)
    subqueries: List[SubQuery] = Field(default_factory=list)
    original_query: str = ""
    query_complexity: str = "simple"  # simple or complex
    combined_answer: Optional[str] = None
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
