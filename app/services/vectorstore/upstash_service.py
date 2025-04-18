"""Upstash vector store service implementation."""

import json
import math
from typing import Any, List, Optional

import boto3
from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.embeddings.bedrock import (BaseEmbeddingModel,
                                             BedrockEmbeddingModel)
from app.services.vectorstore.vectorstore_base import BaseVectorStoreService
from langchain.schema import Document
from pydantic import ConfigDict, PrivateAttr
from upstash_vector import Index
from upstash_vector.types import FusionAlgorithm, QueryMode, SparseVector


class UpstashService(BaseVectorStoreService):
    """
    Upstash vector store service implementation using LangChain's VectorStore.
    Optimizes search using sparse vectors and hybrid search.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _index: Index = PrivateAttr()
    
    def __init__(self, embedding_model: Optional[BaseEmbeddingModel] = None):
        """Initialize Upstash service with optional embedding model."""
        logger.info("Initializing Upstash vector store...")
        
        # First initialize Pydantic with embedding model
        embedding = embedding_model or BedrockEmbeddingModel(settings.EMBEDDING_DIMENSIONS)
        super().__init__(embedding_function=embedding)
        
        # Then set up Upstash client
        endpoint, token = self._get_credentials()
        self._index = Index(url=endpoint, token=token)

    def _get_credentials(self) -> tuple[str, str]:
        """Get Upstash credentials based on environment."""
        try:
            if settings.ENV == Environment.PRODUCTION:
                logger.info("Getting credentials for production")
                # Production uses secrets
                if not settings.UPSTASH_ENDPOINT_SECRET_NAME:
                    raise ValueError("UPSTASH_ENDPOINT_SECRET_NAME is required")
                if not settings.UPSTASH_TOKEN_SECRET_NAME:
                    raise ValueError("UPSTASH_TOKEN_SECRET_NAME is required")

                try:
                    # Get secrets from AWS Secrets Manager
                    secrets = boto3.client(
                        'secretsmanager',
                        region_name=settings.AWS_DEFAULT_REGION
                    )
                    
                    # Get Upstash endpoint
                    endpoint_secret = secrets.get_secret_value(
                        SecretId=settings.UPSTASH_ENDPOINT_SECRET_NAME
                    )
                    endpoint = endpoint_secret['SecretString']
                    
                    # Get Upstash token
                    token_secret = secrets.get_secret_value(
                        SecretId=settings.UPSTASH_TOKEN_SECRET_NAME
                    )
                    token = token_secret['SecretString']
                except (json.JSONDecodeError, KeyError) as e:
                    raise ValueError(f"Invalid credential format: {str(e)}")
                except Exception as e:
                    raise ValueError(f"Failed to retrieve credentials: {str(e)}")

            # We can specify directly in local dev
            elif settings.ENV == Environment.DEVELOPMENT:
                logger.info("Using local credentials for development")
                if not settings.UPSTASH_ENDPOINT:
                    raise ValueError("UPSTASH_ENDPOINT is required")
                if not settings.UPSTASH_TOKEN:
                    raise ValueError("UPSTASH_TOKEN is required")
                
                endpoint = settings.UPSTASH_ENDPOINT
                token = settings.UPSTASH_TOKEN
        except Exception as e:
            logger.error(f"Error getting Upstash credentials: {str(e)}")
            raise
            
        return endpoint, token

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
    
    def similarity_search(
        self,
        query: str,
        k: int = 3,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Search for similar documents using hybrid search with sparse vectors.
        
        Args:
            query: Query string
            k: Number of documents to return
            **kwargs: Additional arguments passed to search
            
        Returns:
            List of Documents most similar to the query
        """
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)

            # Get sparse vector for hybrid search
            sparse_vector = self.create_sparse_vector(query_embedding)
            logger.info(f"Sparsity ratio: {len(sparse_vector.indices) / len(query_embedding)}")
            
            # Search index
            results = self._index.query(
                vector=query_embedding,
                sparse_vector=sparse_vector,
                top_k=k,
                include_metadata=True,
                include_data=True,
                query_mode=QueryMode.HYBRID,
                fusion_algorithm=FusionAlgorithm.RRF,
            )
            
            if not results:
                return []
            
            # Convert to LangChain Documents
            documents = []
            for result in results:
                # Get content from data field
                content = result.data
                if not content:
                    logger.warning(f"No content found for document {result.id}")
                    continue
                    
                metadata = result.metadata or {}
                documents.append(
                    Document(
                        page_content=content,
                        metadata=metadata
                    )
                )
            
            return documents
            
        except Exception as e:
            logger.error(
                f"Error in similarity search: {str(e)}", 
                exc_info=True
            )
            return []
