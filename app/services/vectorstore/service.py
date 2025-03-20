"""Vector store service implementations for SiteChat."""
import os
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import boto3
import faiss
import numpy as np
from app.config.settings import settings
from app.services.llm import TitanModel
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import AWSV4SignerAuth


class BaseVectorStoreService(ABC):
    """Abstract base class for vector store services."""
    
    @abstractmethod
    def get_relevant_context(self, query: str) -> Optional[str]:
        """Get relevant context for a query from the vector store."""
        pass


class FAISSService(BaseVectorStoreService):
    """FAISS vector store service implementation for development."""
    
    def __init__(self):
        """Initialize FAISS service."""
        # Initialize embeddings based on provider
        self.embeddings = self._get_embeddings("document")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize empty FAISS index
        self.index = None
        self.texts = []
        self.metadatas = []
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(settings.VECTOR_STORE_PATH), exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def _get_embeddings(self, input_type: str) -> Embeddings:
        """Get Bedrock embeddings model."""
        return BedrockEmbeddings(
            model_id=TitanModel.TITAN_EMBED_V2,
            region_name=settings.AWS_DEFAULT_REGION
        )
    
    def _load_index(self):
        """Load FAISS index, texts, and metadatas from file if it exists."""
        if os.path.exists(settings.VECTOR_STORE_PATH):
            with open(settings.VECTOR_STORE_PATH, 'rb') as f:
                saved_data = pickle.load(f)
                self.index = saved_data['index']
                self.texts = saved_data.get('texts', [])
                self.metadatas = saved_data.get('metadatas', [])
    
    def _save_index(self):
        """Save FAISS index, texts, and metadatas to file."""
        with open(settings.VECTOR_STORE_PATH, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'texts': self.texts,
                'metadatas': self.metadatas
            }, f)
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts for each text
        """
        if not texts:
            return
        
        # Split texts into chunks
        all_chunks = []
        all_metadatas = []
        for i, text in enumerate(texts):
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)
            if metadatas:
                chunk_metadatas = [
                    {**metadatas[i], 'chunk': j} for j in range(len(chunks))
                ]
                all_metadatas.extend(chunk_metadatas)
            else:
                chunk_metadatas = [{'chunk': j} for j in range(len(chunks))]
                all_metadatas.extend(chunk_metadatas)
        
        # Get embeddings for chunks
        embeddings = self.embeddings.embed_documents(all_chunks)
        
        # Initialize index if needed
        if self.index is None:
            dimension = len(embeddings[0])
            self.index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to index
        self.index.add(np.array(embeddings))
        
        # Store chunks and metadatas
        self.texts.extend(all_chunks)
        self.metadatas.extend(all_metadatas)
        
        # Save updated index, texts, and metadatas
        self._save_index()
    
    def get_relevant_context(self, query: str) -> Optional[str]:
        """Get relevant context for a query.
        
        Args:
            query: The query string
            
        Returns:
            str: Relevant context if found, None otherwise
        """
        if not self.index or not self.texts:
            return None
        
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search index
            distances, indices = self.index.search(
                np.array([query_embedding]), 
                k=5  # Get top 5 most similar chunks
            )
            
            # Get relevant chunks and their metadatas
            relevant_chunks = []
            seen_documents = set()
            for i in indices[0]:
                if i < len(self.texts):
                    chunk = self.texts[i]
                    metadata = self.metadatas[i]
                    # Use a unique identifier for each document
                    doc_id = metadata.get('doc_id', i)
                    if doc_id not in seen_documents:
                        relevant_chunks.append((chunk, metadata))
                        seen_documents.add(doc_id)
                if len(relevant_chunks) == 3:  # Limit to 3 unique documents
                    break
            
            if not relevant_chunks:
                return None
            
            # Combine chunks with metadata
            combined_context = []
            for chunk, metadata in relevant_chunks:
                context = f"Document: {metadata.get('doc_id', 'Unknown')}\n"
                context += f"Chunk: {metadata.get('chunk', 'Unknown')}\n"
                context += f"Content: {chunk}\n\n"
                combined_context.append(context)
            
            return "".join(combined_context)
            
        except Exception as e:
            # Log error and return None
            import logging
            logging.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None


class OpenSearchService(BaseVectorStoreService):
    """OpenSearch vector store service implementation for production."""
    
    def __init__(self):
        """Initialize OpenSearch service."""
        self.embeddings = BedrockEmbeddings(
            model_id=TitanModel.TITAN_EMBED_V2,
            region_name=settings.AWS_DEFAULT_REGION
        )
        
        # Get AWS credentials
        credentials = boto3.Session().get_credentials()
        awsauth = AWSV4SignerAuth(
            credentials,
            settings.AWS_DEFAULT_REGION,
            'es'  # 'es' = elasticsearch, 'aoss' = opensearch serverless
        )
        
        # Initialize LangChain OpenSearchVectorSearch
        self.vectorstore = OpenSearchVectorSearch(
            index_name='sitechat-vectorstore',
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
            import logging
            logging.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None


def get_vector_store() -> BaseVectorStoreService:
    """Factory function to get vector store service."""
    if settings.VECTOR_STORE_PROVIDER == "opensearch":
        return OpenSearchService()
    else:
        return FAISSService()
