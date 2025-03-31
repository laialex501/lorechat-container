"""FAISS vector store service implementation."""
from typing import Any, Dict, List, Optional

import faiss
from app import logger
from app.config.settings import settings
from app.services.embeddings.bedrock import BaseEmbeddingModel
from app.services.vectorstore.base import BaseVectorStoreService
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.base import Docstore
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from pydantic import ConfigDict, PrivateAttr


class FAISSService(BaseVectorStoreService):
    """
    FAISS vector store service implementation.
    Uses LangChain's FAISS implementation as an internal implementation.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _faiss: FAISS = PrivateAttr()
    
    def __init__(
        self,
        embedding_function: BaseEmbeddingModel,
        index: Any = None,
        docstore: Docstore = InMemoryDocstore(),
        index_to_docstore_id: Dict[int, str] = {}
    ):
        """Initialize FAISS service."""
        logger.info("Initializing FAISS service")
        # Initialize BaseVectorStoreService first
        super().__init__(embedding_function=embedding_function)
        
        # Initialize internal FAISS instance
        self._faiss = FAISS(
            embedding_function=embedding_function,
            index=index or faiss.IndexFlatL2(settings.EMBEDDING_DIMENSIONS),
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        **kwargs: Any,
    ) -> List[Document]:
        """Perform similarity search using internal FAISS instance."""
        return self._faiss.similarity_search(query, k=k, **kwargs)

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Add texts using internal FAISS instance."""
        return self._faiss.add_texts(texts, metadatas=metadatas, **kwargs)

    def get_relevant_context(self, query: str) -> Optional[str]:
        """
        Get relevant context for a query from the vector store.
        Implements BaseVectorStoreService interface method.
        """
        docs = self.similarity_search(query, k=3)
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

    @staticmethod
    def _get_sample_documents() -> List[Document]:
        """Get sample documents for development initialization."""
        logger.info("Loading sample data for development...")
        documents = []
        sample_dir = settings.BASE_DIR / "sampledata"

        if not sample_dir.exists():
            logger.warning(f"Sample data directory not found: {sample_dir}")
            return documents
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )

        for file_path in sample_dir.glob("*.html"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Split content into chunks
                    chunks = text_splitter.split_text(content)
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
                
        return documents
