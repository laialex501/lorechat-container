"""Unit tests for the base vector store service."""
import pytest
from app.services.vectorstore.vectorstore_base import BaseVectorStoreService
from langchain.schema import Document
from tests.conftest import MockEmbeddings, MockVectorStore


class TestBaseVectorStoreService:
    """Tests for the BaseVectorStoreService abstract base class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_embeddings = MockEmbeddings()
        self.vector_store = MockVectorStore(embedding_function=self.mock_embeddings)
        
        # Add some test documents
        self.docs = [
            Document(page_content="Paris is the capital of France", metadata={"url": "https://example.com/1"}),
            Document(page_content="Berlin is the capital of Germany", metadata={"url": "https://example.com/2"}),
            Document(page_content="Rome is the capital of Italy", metadata={"url": "https://example.com/3"})
        ]
        self.vector_store.docs = self.docs

    def test_initialization(self):
        """Test initialization of BaseVectorStoreService."""
        assert self.vector_store.embedding_function == self.mock_embeddings
        assert self.vector_store.embeddings == self.mock_embeddings

    def test_embeddings_property(self):
        """Test the embeddings property."""
        # Test with a proper Embeddings instance
        assert self.vector_store.embeddings == self.mock_embeddings

    def test_from_texts_not_implemented(self):
        """Test that from_texts raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            BaseVectorStoreService.from_texts(
                texts=["test"],
                embedding=self.mock_embeddings
            )

    def test_add_texts_not_implemented(self):
        """Test that add_texts raises NotImplementedError."""
        # Create a minimal concrete subclass that implements similarity_search
        class MinimalVectorStore(BaseVectorStoreService):
            def similarity_search(self, query, k=4, **kwargs):
                return []
        
        # Create an instance of the concrete subclass
        store = MinimalVectorStore(embedding_function=self.mock_embeddings)
        
        # Verify that add_texts raises NotImplementedError
        with pytest.raises(NotImplementedError):
            store.add_texts(["test"])

    def test_get_relevant_context(self):
        """Test the get_relevant_context method."""
        # Setup
        query = "capital of France"
        
        # Execute
        result = self.vector_store.get_relevant_context(query)
        
        # Verify
        assert "Paris is the capital of France" in result
        assert "Berlin is the capital of Germany" in result
        assert "Rome is the capital of Italy" in result
        assert "Sources:" in result
        assert "https://example.com/1" in result
        assert "https://example.com/2" in result
        assert "https://example.com/3" in result

    def test_get_relevant_context_no_results(self):
        """Test get_relevant_context when no documents are found."""
        # Setup
        query = "capital of France"
        self.vector_store.docs = []  # Clear documents
        
        # Execute
        result = self.vector_store.get_relevant_context(query)
        
        # Verify
        assert result is None

    def test_get_relevant_context_no_urls(self):
        """Test get_relevant_context when documents have no URLs."""
        # Setup
        query = "capital of France"
        self.vector_store.docs = [
            Document(page_content="Paris is the capital of France", metadata={}),
            Document(page_content="Berlin is the capital of Germany", metadata={})
        ]

        # Execute
        result = self.vector_store.get_relevant_context(query)

        # Verify
        assert "Paris is the capital of France" in result
        assert "Berlin is the capital of Germany" in result
        assert "Sources:" not in result  # No sources section when no URLs

    def test_get_relevant_documents(self):
        """Test the _get_relevant_documents method."""
        # Setup
        query = "capital of France"
        
        # Execute
        result = self.vector_store._get_relevant_documents(query)
        
        # Verify
        assert result == self.docs
        assert len(result) == 3
        assert result[0].page_content == "Paris is the capital of France"
