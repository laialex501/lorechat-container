"""State definitions for chat graph."""
from typing import List, Optional

from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from pydantic import Field


class ChatState(MessagesState):
    """
    Chat state with vector store context.
    
    Attributes:
        messages: List of chat messages
        retrieved_docs: Optional list of retrieved documents for context
    """
    messages: List[BaseMessage] = Field(default_factory=list)
    retrieved_docs: Optional[List[Document]] = Field(default=None)
