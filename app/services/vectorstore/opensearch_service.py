"""OpenSearch vector store service implementation."""
from typing import Any, List, Optional

import boto3
from app import logger
from app.config.settings import settings
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.vectorstore.vectorstore_base import BaseVectorStoreService
from langchain.schema import Document
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import AWSV4SignerAuth


class OpenSearchService(BaseVectorStoreService):
    """OpenSearch vector store service implementation for production."""
    
    def __init__(self):
        """Initialize OpenSearch service."""
        logger.info("Initializing OpenSearch vector store...")
        self.embeddings = BedrockEmbeddingModel(settings.EMBEDDING_DIMENSIONS)
        
        # Get AWS credentials
        credentials = boto3.Session().get_credentials()
        awsauth = AWSV4SignerAuth(
            credentials,
            settings.AWS_DEFAULT_REGION,
            'es'  # 'es' = elasticsearch, 'aoss' = opensearch serverless
        )
        
        # Initialize LangChain OpenSearchVectorSearch
        self.vectorstore = OpenSearchVectorSearch(
            index_name='lorechat-vectorstore',
            embedding_function=self.embeddings,
            opensearch_url=f"https://{settings.OPENSEARCH_ENDPOINT}:443",
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            is_aoss=False
        )

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        """
        Perform similarity search using OpenSearch.
        
        Args:
            query: Query text
            k: Number of results to return
            **kwargs: Additional arguments to pass to underlying vectorstore
            
        Returns:
            List of Documents most similar to the query
        """
        try:
            return self.vectorstore.similarity_search(query, k=k, **kwargs)
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}", exc_info=True)
            return []

    def get_relevant_context(self, query: str) -> Optional[str]:
        """Get relevant context for a query from OpenSearch."""
        try:
            return super().get_relevant_context(query)
        except Exception as e:
            logger.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None
