"""Factory for creating embedding model instances."""
from app import logger
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.embeddings.embeddings_base import BaseEmbeddingModel


class EmbeddingsFactory:
    """Factory class for creating embedding model instances."""
    
    @staticmethod
    def create_embedding_model(dimensions: int = 512) -> BaseEmbeddingModel:
        """
        Create and return an embedding model instance.
        
        Args:
            dimensions: The dimensionality of the embedding vectors
            
        Returns:
            An instance of BaseEmbeddingModel
        """
        logger.info("Initializing embedding model...")
        return BedrockEmbeddingModel(dimensions=dimensions)
