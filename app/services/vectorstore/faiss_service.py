"""FAISS vector store service implementation."""
import os
from typing import Any, List, Optional

from app import logger
from app.config.constants import Environment
from app.config.settings import settings
from app.services.embeddings.bedrock import (BaseEmbeddingModel,
                                             BedrockEmbeddingModel)
from app.services.vectorstore.base import BaseVectorStoreService
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS


class FAISSService(FAISS, BaseVectorStoreService):
    """
    FAISS vector store service implementation for development.
    Uses LangChain's FAISS implementation with our custom initialization.
    """
    
    def __init__(self, embedding_model: Optional[BaseEmbeddingModel] = None):
        """Initialize FAISS service with optional embedding model."""
        logger.info("Initializing FAISS vector store...")
        
        # Set up embeddings - either use provided model or create default
        embeddings = embedding_model or BedrockEmbeddingModel(settings.EMBEDDING_DIMENSIONS)
        super().__init__(embedding_function=embeddings)
        
        # Initialize text splitter for sample data
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Load existing index or initialize with sample data
        self._load_or_init_index()
    
    def _load_or_init_index(self):
        """Load existing index or initialize with sample data."""
        try:
            if os.path.exists(settings.VECTOR_STORE_PATH):
                # Load existing index
                self = FAISS.load_local(
                    settings.VECTOR_STORE_PATH,
                    self.embeddings
                )
                logger.info("Loaded existing FAISS index")
                return
            
            # Initialize with sample data in development
            if settings.ENV == Environment.DEVELOPMENT:
                self._init_with_sample_data()
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")

    def _init_with_sample_data(self):
        """Initialize development vector store with sample data."""
        logger.info("Initializing development vector store...")
        
        # Read and process sample data
        documents = []
        sample_dir = settings.BASE_DIR / "sampledata"
        
        if not sample_dir.exists():
            logger.warning(f"Sample data directory not found: {sample_dir}")
            return
        
        for file_path in sample_dir.glob("*.html"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Split content into chunks
                    chunks = self.text_splitter.split_text(content)
                    # Create documents with metadata
                    for i, chunk in enumerate(chunks):
                        documents.append(
                            Document(
                                page_content=chunk,
                                metadata={
                                    "file_name": file_path.name,
                                    "chunk": i
                                }
                            )
                        )
                    logger.info(f"Processed {file_path.name}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
                continue
        
        if documents:
            # Initialize FAISS index with documents
            self = FAISS.from_documents(
                documents,
                self.embeddings
            )
            # Save the index
            self.save_local(settings.VECTOR_STORE_PATH)
            logger.info(f"Vector store initialized with {len(documents)} chunks")
        else:
            logger.warning("No sample data found to initialize vector store")

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Search for similar documents using FAISS.
        
        Args:
            query: Query string
            k: Number of documents to return
            **kwargs: Additional arguments passed to search
            
        Returns:
            List of Documents most similar to the query
        """
        try:
            # Use LangChain's FAISS similarity search
            return super().similarity_search(query, k=k, **kwargs)
            
        except Exception as e:
            logger.error(
                f"Error in similarity search: {str(e)}", 
                exc_info=True
            )
            return []
