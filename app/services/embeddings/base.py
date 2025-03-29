"""Base class for embedding models."""
from enum import Enum
from typing import List

from langchain.embeddings.base import Embeddings


class TitanModel(str, Enum):
    """Available Titan models."""
    TITAN_EMBED_V2 = "amazon.titan-embed-text-v2:0"


class BaseEmbeddingModel(Embeddings):
    """Base class for embedding models using LangChain's Embeddings."""

    def __init__(self, dimensions: int):
        super().__init__()
        self.dimensions = dimensions

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single piece of text.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedding vector of length self.dimensions.
        """
        raise NotImplementedError

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            texts (List[str]): The documents to embed.

        Returns:
            List[List[float]]: A list of embedding vectors.
        """
        raise NotImplementedError
