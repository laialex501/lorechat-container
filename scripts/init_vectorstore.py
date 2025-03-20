"""Initialize vector store with sample data during development."""
from pathlib import Path
from typing import Dict, List, Tuple

from app.config.settings import settings
from app.services.vectorstore.service import get_vector_store


def read_sample_data() -> List[Tuple[str, Dict[str, str]]]:
    """Read content from sample data files with metadata."""
    print("Reading sample data...")
    texts_with_metadata = []
    sample_dir = settings.BASE_DIR / "sampledata"
    
    if not sample_dir.exists():
        print(f"Sample data directory not found: {sample_dir}")
        return texts_with_metadata
    
    for file_path in sample_dir.glob("*.html"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                metadata = {"file_name": file_path.name}
                texts_with_metadata.append((content, metadata))
                print(f"Read content from {file_path.name}")
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            continue
    
    return texts_with_metadata


def init_dev_vectorstore():
    """Initialize development vector store with sample data."""
    # Only initialize in development mode
    if settings.ENV != "development":
        return
    
    # Check if vector store already exists
    vector_store_path = Path(settings.VECTOR_STORE_PATH)
    if vector_store_path.exists():
        print("Vector store already exists, skipping initialization")
        return
    
    print("Initializing development vector store...")
    
    # Read sample data with metadata
    texts_with_metadata = read_sample_data()
    if not texts_with_metadata:
        print("No sample data found to initialize vector store")
        return
    
    # Initialize vector store with sample data and metadata
    print("Adding documents to vector store...")
    vector_store = get_vector_store()
    texts, metadatas = zip(*texts_with_metadata)
    vector_store.add_texts(texts, metadatas=metadatas)
    
    print(f"Vector store initialized with {len(texts)} documents")


if __name__ == "__main__":
    init_dev_vectorstore()
