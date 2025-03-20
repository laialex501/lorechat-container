from enum import Enum


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ChatRole(str, Enum):
    """Chat message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class VectorStoreType(str, Enum):
    """Vector store types."""
    FAISS = "faiss"
    OPENSEARCH = "opensearch"


class LLMProvider(str, Enum):
    """LLM provider types."""
    OPENAI = "openai"
    BEDROCK = "bedrock"


# LLM Model Constants
OPENAI_MODELS = {
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
}

BEDROCK_MODELS = {
    "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
}

# System Constants
MAX_HISTORY_LENGTH = 10  # Maximum number of messages to keep in chat history
SYSTEM_PROMPT = """You are a helpful AI assistant that provides accurate and 
relevant information from the website content. Please be concise and direct in 
your responses."""

# Performance Constants
CHUNK_SIZE = 1000  # Text chunk size for vectorization
CHUNK_OVERLAP = 200  # Overlap between chunks
MAX_CONCURRENT_REQUESTS = 5  # Maximum number of concurrent API requests

# UI Constants
MAX_RESPONSE_TOKENS = 500  # Maximum number of tokens in response
TEMPERATURE = 0.7  # LLM temperature setting
TOP_K = 4  # Number of relevant chunks to consider
