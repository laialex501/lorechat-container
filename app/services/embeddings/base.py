"""Base class for embedding models."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class TitanModel(str, Enum):
    """Available Titan models."""
    TITAN_EMBED_V2 = "amazon.titan-embed-text-v2:0"


class BaseEmbeddingModel(ABC):
    """Abstract base class for embedding models."""

    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single piece of text.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedding vector of length self.dimensions.
        """
        pass

    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            documents (List[str]): The documents to embed.

        Returns:
            List[List[float]]: A list of embedding vectors.
        """
        pass
