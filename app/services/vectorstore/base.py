"""Base class for vector store services."""
from enum import Enum
from typing import Any, Iterable, List, Optional

from langchain.embeddings.base import Embeddings
from langchain.schema import BaseRetriever, Document
from langchain.vectorstores.base import VectorStore
from pydantic import BaseModel, ConfigDict, Field


class VectorStoreProvider(str, Enum):
    """Enum for vector store providers."""

    FAISS = "faiss"
    OPENSEARCH = "opensearch"
    UPSTASH = "upstash"


class BaseVectorStoreService(VectorStore, BaseRetriever, BaseModel):
    """
    Base class for vector store services using LangChain's VectorStore.
    This is a retrieval-only implementation that doesn't support adding texts
    except for FAISS which inherits implementation from LangChain.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    embedding_function: Embeddings = Field(description="Embedding function to use")

    def __init__(self, embedding_function: Embeddings, **kwargs):
        """Initialize with embedding function."""
        super().__init__(embedding_function=embedding_function, **kwargs)

    @property
    def embeddings(self) -> Optional[Embeddings]:
        """Return the embedding model if it's a proper Embeddings instance."""
        return (
            self.embedding_function
            if isinstance(self.embedding_function, Embeddings)
            else None
        )

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Any,
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> VectorStore:
        """
        Create vector store from texts. Required by LangChain's VectorStore.
        By default, this is not implemented as we're retrieval-only.
        FAISS implementation inherits this from LangChain's FAISS class.
        
        Args:
            texts: List of texts to add
            embedding: Embedding function to use
            metadatas: Optional list of metadatas
            **kwargs: Additional arguments
            
        Raises:
            NotImplementedError: This is a retrieval-only service
        """
        raise NotImplementedError(
            "This is a retrieval-only service. Documents should be added through the ingestion pipeline."
        )
    
    def get_relevant_context(self, query: str) -> Optional[str]:
        """
        Get relevant context for a query from the vector store.
        This is our simplified interface that returns formatted context.
        
        Args:
            query: The query string
            
        Returns:
            Optional[str]: Relevant context if found, None otherwise
        """
        # Use LangChain's similarity_search under the hood
        docs = self.similarity_search(query, k=1)
        if not docs:
            return None
            
        # Format the results
        relevant_texts = []
        source_urls = set()
        
        for doc in docs:
            relevant_texts.append(f"{doc.page_content}\n")
            if doc.metadata.get('url'):
                source_urls.add(doc.metadata['url'])
        
        # Combine content and add sources
        combined_text = "".join(relevant_texts)
        if source_urls:
            combined_text += "\nSources:\n"
            for url in source_urls:
                combined_text += f"- {url}\n"
                
        return combined_text

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Not implemented - this is a retrieval-only service.
        Adding documents should be handled by the ingestion pipeline.
        """
        raise NotImplementedError(
            "This is a retrieval-only service. Documents should be added through the ingestion pipeline."
        )
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Required implementation of BaseRetriever.get_relevant_documents.
        Uses similarity_search under the hood.
        """
        return self.similarity_search(query)
