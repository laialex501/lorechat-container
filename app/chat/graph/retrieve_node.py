"""Node implementations for chat graph."""
import time
from typing import Any, Dict

from app import logger
from app.chat.graph.state import ChatState
from app.services.vectorstore import BaseVectorStoreService
from langchain_core.messages import HumanMessage


class RetrieveNode:
    """A node that retrieves documents from a vector store"""
    def __init__(self, vector_store: BaseVectorStoreService):
        logger.info("Initializing RetrieveNode")
        self.vector_store = vector_store

    def __call__(self, state: ChatState) -> Dict[str, Any]:
        """Retrieve relevant documents based on latest message."""
        logger.info("Retrieving documents")
        if not state["messages"]:
            return {"retrieved_docs": []}

        # Get latest message
        latest_message = state["messages"][-1]
        if not isinstance(latest_message, HumanMessage):
            return {"retrieved_docs": []}
      
        # Search vector store
        start_time = time.time()
        docs = self.vector_store.as_retriever().invoke(
            latest_message.content
        )
        logger.info(f"Retrieved documents in {time.time() - start_time} seconds")
        return {"retrieved_docs": docs}
