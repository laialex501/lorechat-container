"""OpenSearch vector store service implementation."""
from typing import Optional

import boto3
from app import logger
from app.config.settings import settings
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.vectorstore.base import BaseVectorStoreService
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
    
    def get_relevant_context(self, query: str) -> Optional[str]:
        """Get relevant context for a query from OpenSearch.
        
        Args:
            query: The query string
            
        Returns:
            str: Relevant context if found, None otherwise
        """
        try:
            # Use similarity_search to get relevant documents
            docs = self.vectorstore.similarity_search(
                query,
                k=3  # Get top 3 most similar
            )
            
            if not docs:
                return None
            
            # Extract and combine the page content from documents
            relevant_texts = [doc.page_content for doc in docs]
            return "\n\n".join(relevant_texts)
            
        except Exception as e:
            # Log error and return None
            logger.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None
