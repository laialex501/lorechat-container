"""Unit tests for the vector store factory."""
from unittest.mock import MagicMock, patch

import pytest
from app.services.embeddings.embeddings_base import BaseEmbeddingModel
from app.services.vectorstore.faiss_service import FAISSService
from app.services.vectorstore.opensearch_service import OpenSearchService
from app.services.vectorstore.upstash_service import UpstashService
from app.services.vectorstore.vectorstore_base import VectorStoreProvider
from app.services.vectorstore.vectorstore_factory import VectorStoreFactory

# Test constants
TEST_INVALID_PROVIDER = "unknown_provider"


class TestVectorStoreFactory:
    """Tests for the VectorStoreFactory class."""

    @patch("app.services.vectorstore.vectorstore_factory.FAISSService")
    @patch("app.services.vectorstore.vectorstore_factory.BedrockEmbeddingModel")
    def test_create_faiss_vector_store(self, mock_embeddings_class, mock_faiss_class):
        """Test creating a FAISS vector store."""
        # Setup
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings
        mock_instance = MagicMock(spec=FAISSService)
        mock_faiss_class.return_value = mock_instance
        
        # Execute
        result = VectorStoreFactory.create_vector_store(provider=VectorStoreProvider.FAISS)
        
        # Verify
        assert result == mock_instance
        mock_embeddings_class.assert_called_once()
        mock_faiss_class.assert_called_once()

    @patch("app.services.vectorstore.vectorstore_factory.OpenSearchService")
    def test_create_opensearch_vector_store(self, mock_opensearch_class):
        """Test creating an OpenSearch vector store."""
        # Setup
        mock_instance = MagicMock(spec=OpenSearchService)
        mock_opensearch_class.return_value = mock_instance
        
        # Execute
        result = VectorStoreFactory.create_vector_store(provider=VectorStoreProvider.OPENSEARCH)
        
        # Verify
        assert result == mock_instance
        mock_opensearch_class.assert_called_once()

    @patch("app.services.vectorstore.vectorstore_factory.UpstashService")
    def test_create_upstash_vector_store(self, mock_upstash_class):
        """Test creating an Upstash vector store."""
        # Setup
        mock_instance = MagicMock(spec=UpstashService)
        mock_upstash_class.return_value = mock_instance
        
        # Execute
        result = VectorStoreFactory.create_vector_store(provider=VectorStoreProvider.UPSTASH)
        
        # Verify
        assert result == mock_instance
        mock_upstash_class.assert_called_once()

    def test_create_with_unknown_provider(self):
        """Test creating a vector store with an unknown provider raises ValueError."""
        # Execute and verify
        with pytest.raises(ValueError, match=f"Invalid vector store provider: {TEST_INVALID_PROVIDER}"):
            VectorStoreFactory.create_vector_store(provider=TEST_INVALID_PROVIDER)

    @patch("app.services.vectorstore.vectorstore_factory.os.path.exists")
    @patch("app.services.vectorstore.vectorstore_factory.BedrockEmbeddingModel")
    @patch("app.services.vectorstore.vectorstore_factory.FAISS.load_local")
    @patch("app.services.vectorstore.vectorstore_factory.FAISSService")
    @patch("app.services.vectorstore.vectorstore_factory.settings")
    def test_create_faiss_with_existing_index(self, mock_settings, mock_faiss_service_class, mock_load_local,
                                              mock_embeddings_class, mock_exists):
        """Test creating a FAISS vector store with an existing index."""
        # Setup
        mock_exists.return_value = True
        mock_embeddings = MagicMock(spec=BaseEmbeddingModel)
        mock_embeddings_class.return_value = mock_embeddings
        mock_settings.VECTOR_STORE_PATH = "/mock/path"
        
        # Create mock FAISS index with required attributes
        mock_loaded = MagicMock()
        mock_loaded.index = MagicMock()
        mock_loaded.docstore = MagicMock()
        mock_loaded.index_to_docstore_id = MagicMock()
        mock_load_local.return_value = mock_loaded
        
        # Mock the FAISSService constructor
        mock_faiss_instance = MagicMock(spec=FAISSService)
        mock_faiss_service_class.return_value = mock_faiss_instance
        
        # Execute
        result = VectorStoreFactory._create_faiss_service()
        
        # Verify
        mock_exists.assert_called_once_with(mock_settings.VECTOR_STORE_PATH)
        mock_load_local.assert_called_once_with(
            mock_settings.VECTOR_STORE_PATH,
            mock_embeddings,
            allow_dangerous_deserialization=True
        )
        mock_faiss_service_class.assert_called_once()
        assert result == mock_faiss_instance

    @patch("app.services.vectorstore.vectorstore_factory.os.path.exists")
    @patch("app.services.vectorstore.vectorstore_factory.BedrockEmbeddingModel")
    @patch("app.services.vectorstore.vectorstore_factory.FAISSService._get_sample_documents")
    @patch("app.services.vectorstore.vectorstore_factory.FAISS.from_documents")
    @patch("app.services.vectorstore.vectorstore_factory.Environment")
    @patch("app.services.vectorstore.vectorstore_factory.FAISSService")
    def test_create_faiss_with_sample_documents(self, mock_faiss_service_class, mock_env_class, mock_from_docs, 
                                                mock_get_docs, mock_embeddings_class, mock_exists):
        """Test creating a FAISS vector store with sample documents."""
        # Setup
        mock_exists.return_value = False
        mock_embeddings = MagicMock(spec=BaseEmbeddingModel)
        mock_embeddings_class.return_value = mock_embeddings
        mock_docs = [MagicMock(), MagicMock()]
        mock_get_docs.return_value = mock_docs
        
        # Create mock FAISS index with required attributes
        mock_loaded = MagicMock()
        mock_loaded.index = MagicMock()
        mock_loaded.docstore = MagicMock()
        mock_loaded.index_to_docstore_id = MagicMock()
        mock_from_docs.return_value = mock_loaded
        
        # Mock Environment enum
        mock_dev_env = "DEVELOPMENT"
        mock_env_class.DEVELOPMENT = mock_dev_env
        
        # Mock the FAISSService constructor
        mock_faiss_instance = MagicMock(spec=FAISSService)
        mock_faiss_service_class.return_value = mock_faiss_instance
        
        # Execute
        with patch("app.services.vectorstore.vectorstore_factory.settings.ENV", mock_dev_env):
            result = VectorStoreFactory._create_faiss_service()
        
        # Verify
        assert mock_exists.call_count == 3
        mock_get_docs.assert_called_once()
        mock_from_docs.assert_called_once_with(mock_docs, mock_embeddings)
        assert mock_faiss_service_class.call_count == 2
        assert result == mock_faiss_instance
