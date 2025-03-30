"""Node implementations for chat graph."""
from typing import Any, Dict

from app.chat.graph.state import ChatState
from app.services.vectorstore import BaseVectorStoreService
from langchain_core.messages import HumanMessage


class RetrieveNode:
    """A node that retrieves documents from a vector store"""
    def __init__(self, vector_store: BaseVectorStoreService):
        self.vector_store = vector_store

    def __call__(self, state: ChatState) -> Dict[str, Any]:
        """Retrieve relevant documents based on latest message."""
        if not state["messages"]:
            return {"retrieved_docs": []}

        # Get latest message
        latest_message = state["messages"][-1]
        if not isinstance(latest_message, HumanMessage):
            return {"retrieved_docs": []}
      
        # Search vector store
        docs = self.vector_store.as_retriever().invoke(
            latest_message.content
        )
        return {"retrieved_docs": docs}
