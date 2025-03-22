"""Upstash vector store service implementation."""
import json
from typing import Optional

import boto3
from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.vectorstore.base import BaseVectorStoreService
from upstash_vector import Index


class UpstashService(BaseVectorStoreService):
    """Upstash vector store service implementation for production."""
    
    def __init__(self):
        """Initialize Upstash service."""
        logger.info("Initializing Upstash vector store...")
        self.embeddings = BedrockEmbeddingModel(settings.EMBEDDING_DIMENSIONS)
        
        # Validate required settings
        if (settings.ENV == Environment.PRODUCTION):
            # Production uses secrets
            if not settings.UPSTASH_ENDPOINT_SECRET_NAME:
                raise ValueError("UPSTASH_ENDPOINT_SECRET_NAME is required")
            if not settings.UPSTASH_TOKEN_SECRET_NAME:
                raise ValueError("UPSTASH_TOKEN_SECRET_NAME is required")

            # Get secrets from AWS Secrets Manager
            secrets = boto3.client(
                'secretsmanager',
                region_name=settings.AWS_DEFAULT_REGION
            )
            
            # Get Upstash endpoint
            endpoint_secret = secrets.get_secret_value(
                SecretId=settings.UPSTASH_ENDPOINT_SECRET_NAME
            )
            endpoint = json.loads(endpoint_secret['SecretString'])['endpoint']
            
            # Get Upstash token
            token_secret = secrets.get_secret_value(
                SecretId=settings.UPSTASH_TOKEN_SECRET_NAME
            )
            token = json.loads(token_secret['SecretString'])['token']

        # We can specify directly in local dev
        elif (settings.ENV == Environment.DEVELOPMENT):
            if not settings.UPSTASH_ENDPOINT:
                raise ValueError("UPSTASH_ENDPOINT is required")
            if not settings.UPSTASH_TOKEN:
                raise ValueError("UPSTASH_TOKEN is required")
            
            endpoint = settings.UPSTASH_ENDPOINT
            token = settings.UPSTASH_TOKEN
            
        # Initialize Upstash client
        self.index = Index(url=endpoint, token=token)
    
    def get_relevant_context(self, query: str) -> Optional[str]:
        """Get relevant context for a query.
        
        Args:
            query: The query string
            
        Returns:
            str: Relevant context if found, None otherwise
        """
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search index
            results = self.index.query(
                vector=query_embedding,
                top_k=3,  # Get top 3 most similar
                include_metadata=True
            )
            
            if not results:
                return None
            
            # Extract and combine the content from results
            relevant_texts = []
            for result in results:
                metadata = result.metadata or {}
                context = f"Document: {metadata.get('doc_id', 'Unknown')}\n"
                context += f"Chunk: {metadata.get('chunk', 'Unknown')}\n"
                context += f"Content: {result.vector}\n\n"
                relevant_texts.append(context)
            
            return "".join(relevant_texts)
            
        except Exception as e:
            # Log error and return None
            logger.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None
