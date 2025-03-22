"""Bedrock embedding model implementation."""
from typing import List

from app import logger
from app.config.settings import settings
from app.services.embeddings.base import BaseEmbeddingModel
from langchain_aws import BedrockEmbeddings


class BedrockEmbeddingModel(BaseEmbeddingModel):
    """Bedrock embedding model implementation."""

    def __init__(self, dimensions: int):
        super().__init__(dimensions)
        logger.info("Initializing Bedrock embedding model...")
        self.embeddings = BedrockEmbeddings(
            model_id=settings.BEDROCK_EMBEDDING_MODEL_ID,
            region_name=settings.AWS_DEFAULT_REGION,
            model_kwargs={"dimensions": dimensions}
        )

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single piece of text.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedding vector of length self.dimensions.
        """
        return self.embeddings.embed_query(text)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.

        Args:
            documents (List[str]): The documents to embed.

        Returns:
            List[List[float]]: A list of embedding vectors, each of length
                self.dimensions.
        """
        return self.embeddings.embed_documents(documents)
