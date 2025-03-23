"""Vector store factory for LoreChat."""
from app import logger
from app.config.settings import settings
from app.services.vectorstore.base import (BaseVectorStoreService,
                                           VectorStoreProvider)
from app.services.vectorstore.faiss_service import FAISSService
from app.services.vectorstore.opensearch_service import OpenSearchService
from app.services.vectorstore.upstash_service import UpstashService


class VectorStoreFactory:
    """Factory class for vector store service."""

    @staticmethod
    def get_vector_store() -> BaseVectorStoreService:
        """Factory function to get vector store service."""
        logger.info("Initializing vector store...")
        if settings.VECTOR_STORE_PROVIDER == VectorStoreProvider.UPSTASH:
            return UpstashService()
        elif settings.VECTOR_STORE_PROVIDER == VectorStoreProvider.OPENSEARCH:
            return OpenSearchService()
        else:
            return FAISSService()
