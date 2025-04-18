"""Vector store factory for LoreChat."""
import os
from typing import Optional

from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.vectorstore.faiss_service import FAISSService
from app.services.vectorstore.opensearch_service import OpenSearchService
from app.services.vectorstore.upstash_service import UpstashService
from app.services.vectorstore.vectorstore_base import (BaseVectorStoreService,
                                                       VectorStoreProvider)
from langchain_community.vectorstores import FAISS


class VectorStoreFactory:
    """Factory class for vector store service."""

    @staticmethod
    def create_vector_store(provider: Optional[VectorStoreProvider] = None) -> BaseVectorStoreService:
        """Factory function to get vector store service."""
        if not provider:
            provider = settings.VECTOR_STORE_PROVIDER
        logger.info(f"Initializing vector store with provider {provider}...")
        if provider == VectorStoreProvider.UPSTASH:
            return UpstashService()
        elif provider == VectorStoreProvider.OPENSEARCH:
            return OpenSearchService()
        elif provider == VectorStoreProvider.FAISS:
            return VectorStoreFactory._create_faiss_service()
        else:
            raise ValueError(f"Invalid vector store provider: {provider}")

    @staticmethod
    def _create_faiss_service() -> FAISSService:
        """Create and initialize FAISS service."""
        embeddings = BedrockEmbeddingModel(settings.EMBEDDING_DIMENSIONS)
        
        # Try to load existing index
        if os.path.exists(settings.VECTOR_STORE_PATH):
            loaded = FAISS.load_local(
                settings.VECTOR_STORE_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            return FAISSService(
                embedding_function=embeddings,
                index=loaded.index,
                docstore=loaded.docstore,
                index_to_docstore_id=loaded.index_to_docstore_id
            )
            
        # Create service with empty index
        faiss_service = FAISSService(embedding_function=embeddings)

        # Initialize with sample data in development
        if settings.ENV == Environment.DEVELOPMENT:
            # Load sample documents if available
            documents = FAISSService._get_sample_documents()
            logger.info(f"Sample documents: {len(documents)}")
            if documents:
                logger.info("Creating FAISS from documents")
                loaded = FAISS.from_documents(documents, embeddings)
                loaded.save_local(settings.VECTOR_STORE_PATH)
                return FAISSService(
                    embedding_function=embeddings,
                    index=loaded.index,
                    docstore=loaded.docstore,
                    index_to_docstore_id=loaded.index_to_docstore_id
                )
      
        # Return empty index
        return faiss_service
