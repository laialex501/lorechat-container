"""FAISS vector store service implementation."""
import os
import pickle
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.embeddings.bedrock import BedrockEmbeddingModel
from app.services.vectorstore.base import BaseVectorStoreService
from langchain.text_splitter import RecursiveCharacterTextSplitter


class FAISSService(BaseVectorStoreService):
    """FAISS vector store service implementation for development."""
    
    def __init__(self):
        """Initialize FAISS service."""
        logger.info("Initializing FAISS vector store...")
        # Initialize embeddings based on provider
        self.embeddings = BedrockEmbeddingModel(settings.EMBEDDING_DIMENSIONS)
        
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

        # Load existing index if available or initialize with sample data
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index, texts, and metadatas from file if it exists.
        In development mode, initialize with sample data if needed."""
        # Try to load existing index if directory exists
        if os.path.exists(settings.VECTOR_STORE_PATH):
            with open(settings.VECTOR_STORE_PATH, 'rb') as f:
                saved_data = pickle.load(f)
                self.index = saved_data['index']
                self.texts = saved_data.get('texts', [])
                self.metadatas = saved_data.get('metadatas', [])
            return

        # Ensure the directory exists
        os.makedirs(os.path.dirname(settings.VECTOR_STORE_PATH), exist_ok=True)

        # In development mode, initialize with sample data if doesn't exist
        if settings.ENV == Environment.DEVELOPMENT:
            self._init_with_sample_data()

    def _init_with_sample_data(self):
        """Initialize development vector store with sample data."""
        logger.info("Initializing development vector store...")
        
        # Read sample data with metadata
        texts_with_metadata = self._read_sample_data()
        if not texts_with_metadata:
            logger.warning("No sample data found to initialize vector store")
            return
        
        # Initialize vector store with sample data and metadata
        logger.info("Adding documents to vector store...")
        texts, metadatas = zip(*texts_with_metadata)
        self.add_texts(texts, metadatas=metadatas)
        
        logger.info(f"Vector store initialized with {len(texts)} documents")

    def _read_sample_data(self):
        """Read content from sample data files with metadata."""
        logger.info("Reading sample data...")
        texts_with_metadata = []
        sample_dir = settings.BASE_DIR / "sampledata"
        
        if not sample_dir.exists():
            logger.warning(f"Sample data directory not found: {sample_dir}")
            return texts_with_metadata
        
        for file_path in sample_dir.glob("*.html"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    metadata = {"file_name": file_path.name}
                    texts_with_metadata.append((content, metadata))
                    logger.info(f"Read content from {file_path.name}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
                continue
        
        return texts_with_metadata
    
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
            logger.error(
                f"Error getting relevant context: {str(e)}", 
                exc_info=True
            )
            return None
