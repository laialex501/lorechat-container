"""Upstash vector store service implementation."""

import json
import math
from typing import List, Optional

import boto3
from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.vectorstore.base import BaseVectorStoreService
from upstash_vector import Index
from upstash_vector.types import FusionAlgorithm, QueryMode, SparseVector


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

    def create_sparse_vector(
        self,
        vector: List[float], 
        top_k: int = 32, 
        threshold: float = 0.1
    ) -> SparseVector:
        """Create sparse vector using both top-k and threshold with validation"""
        # Validate input
        if not vector:
            raise ValueError("Empty embeddings list")
        
        # Create indexed values and filter out NaN values
        indexed_values = [
            (i, v) for i, v in enumerate(vector) 
            if isinstance(v, float) and not math.isnan(v)  # Explicit NaN check using math.isnan()
        ]
        
        if not indexed_values:
            raise ValueError("No valid values in embeddings (all NaN)")
        
        # Filter by threshold and ensure positive values
        significant_values = [
            (i, abs(v)) for i, v in indexed_values 
            if abs(v) > threshold
        ]
        
        if not significant_values:
            # If no values meet threshold, take top k of absolute values
            significant_values = sorted(
                [(i, abs(v)) for i, v in indexed_values],
                key=lambda x: x[1],
                reverse=True
            )[:top_k]
        
        # Take top-k of remaining values
        top_indices = sorted(
            significant_values, 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        if not top_indices:
            raise ValueError("No significant values found in embeddings")
        
        indices = [i for i, _ in top_indices]
        values = [v for _, v in top_indices]
        
        # Validate final values
        if any(v <= 0 for v in values):
            raise ValueError("Negative or zero values in sparse vector")
        
        return SparseVector(indices, values)
    
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

            # Get sparse vector
            sparse_vector = self.create_sparse_vector(query_embedding)
            logger.info(f"Sparsity ratio: {len(sparse_vector.indices) / len(query_embedding)}")
            
            # Search index
            results = self.index.query(
                vector=query_embedding,
                sparse_vector=sparse_vector,
                top_k=3,  # Get top 3 most similar
                include_metadata=True,
                query_mode=QueryMode.HYBRID,
                fusion_algorithm=FusionAlgorithm.RRF,
            )
            
            if not results:
                return None
            
            # Extract and combine the content from results with metadata
            relevant_texts = []
            source_urls = set()  # Track unique URLs
            
            for result in results:
                metadata = result.metadata or {}
                content = result.vector
                url = metadata.get('url', 'Unknown source')
                
                # Add content with minimal metadata inline
                relevant_texts.append(f"{content}\n")
                
                # Track URL if available
                if url != 'Unknown source':
                    source_urls.add(url)
            
            # Combine content and add sources at the end
            combined_text = "".join(relevant_texts)
            if source_urls:
                combined_text += "\nSources:\n"
                for url in source_urls:
                    combined_text += f"- {url}\n"
            
            return combined_text
            
        except Exception as e:
            # Log error and return None
            logger.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None
