"""Base class for vector store services."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class VectorStoreProvider(str, Enum):
    """Enum for vector store providers."""

    FAISS = "faiss"
    OPENSEARCH = "opensearch"
    UPSTASH = "upstash"


class BaseVectorStoreService(ABC):
    """Abstract base class for vector store services."""
    
    @abstractmethod
    def get_relevant_context(self, query: str) -> Optional[str]:
        """Get relevant context for a query from the vector store."""
        pass
    
    """
    Do not define a add_texts method because this is supposed to be
    a retrieval-only db
    """
