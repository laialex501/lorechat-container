# LoreChat Development Guide

This guide covers the technical implementation and development workflow for LoreChat, focusing on the LangGraph-based architecture and core services.

## Prerequisites

### System Requirements
- Python 3.9+ (required for LangGraph compatibility)
- Docker or Finch (for containerized development)
- AWS CLI (configured for Bedrock access)
- Git (for version control)

### Service Dependencies
- OpenAI API key (for GPT models)
- AWS Bedrock access (for Claude models)
  - Required models: Claude 3 Sonnet/Haiku
  - Required regions: us-east-1, us-west-2
- Upstash Vector account
  - Required for production deployments
  - Local development uses FAISS

## Implementation Architecture

```
LoreChat/
├── app/                      # Core application
│   ├── chat/                # Chat implementation
│   │   ├── graph/          # LangGraph components
│   │   │   ├── nodes.py    # Graph node implementations
│   │   │   ├── state.py    # State management
│   │   │   └── workflow.py # Graph configuration
│   │   └── service.py      # High-level chat service
│   ├── config/             # Application settings
│   ├── services/           # Core services
│   │   ├── embeddings/     # Embedding providers
│   │   ├── llm/           # LLM implementations
│   │   ├── prompts/       # System prompts
│   │   └── vectorstore/    # Vector store services
│   ├── monitoring/         # Logging & metrics
│   └── ui/                # Streamlit interface
├── docker/                 # Container configs
├── tests/                 # Test suites
└── sampledata/            # Sample content
```

## Development Setup

### Local Environment

1. Clone the repository:
```bash
git clone <repository-url>
cd LoreChat
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Development Settings
ENV=development
DEBUG=true
LOG_LEVEL=INFO
PYTHONPATH=.

# Vector Store Configuration
VECTOR_STORE_PROVIDER=faiss  # or upstash for production
VECTOR_STORE_PATH=local_vectorstore/faiss
EMBEDDING_DIMENSIONS=1536  # For Claude embeddings

# LLM Configuration
OPENAI_API_KEY=your_key_here  # If using OpenAI

# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=default  # Optional: for multiple AWS profiles

# Upstash Configuration (Production)
VECTOR_STORE_PROVIDER=upstash
UPSTASH_ENDPOINT=your_endpoint
UPSTASH_TOKEN=your_token
```

### Container Development

Using Docker:
```bash
cd docker/dev
docker-compose up --build
```

Using Finch:
```bash
cd docker/dev
finch compose up --build
```

## Core Implementation

### LangGraph Architecture

The chat system uses LangGraph for workflow orchestration. Key components:

1. State Management:
```python
class ChatState(MessagesState):
    """Thread-based chat state."""
    messages: List[BaseMessage]
    retrieved_docs: Optional[List[Document]]
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

2. Graph Nodes:
```python
def retrieve_context(state: ChatState) -> Dict[str, Any]:
    """Retrieve relevant documents for context."""
    latest_message = state["messages"][-1]
    docs = vector_store.invoke(
        latest_message.content,
        search_type="hybrid",  # Uses dense + sparse vectors
        k=1  # Number of documents to retrieve
    )
    return {"retrieved_docs": docs}

def generate_response(state: ChatState) -> Dict[str, Any]:
    """Generate response with source attribution."""
    context = format_context(state["retrieved_docs"])
    messages = create_prompt(
        system_template=prompt.system_template,
        chat_history=state["messages"][:-1],
        context=context,
        query=state["messages"][-1].content
    )
    response = llm_service.invoke(messages)
    return {"messages": [AIMessage(content=response)]}
```

3. Workflow Configuration:
```python
def create_chat_workflow(
    llm_service: BaseLLMService,
    vector_store: BaseVectorStoreService,
    memory: Optional[MemorySaver] = None
) -> Callable:
    """Create and configure the chat workflow."""
    workflow = StateGraph(ChatState)
    
    # Add nodes with error handling
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("respond", generate_response)
    
    # Configure graph flow
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "respond")
    
    # Add memory management
    if memory is None:
        memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)
```

### Vector Store Implementation

The system supports both local and cloud vector stores:

1. Local Development (FAISS):
```python
class FAISSService(BaseVectorStoreService):
    """Local vector store for development."""
    def __init__(
        self,
        embedding_model: Optional[BaseEmbeddingModel] = None,
        persist_path: str = "local_vectorstore/faiss"
    ):
        super().__init__(embedding_model)
        self.persist_path = persist_path
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize or load existing store."""
        if os.path.exists(self.persist_path):
            self._index = FAISS.load_local(
                self.persist_path,
                self.embeddings
            )
        else:
            self._index = FAISS.from_documents(
                [],  # Empty initial index
                self.embeddings
            )
```

2. Production (Upstash Vector):
```python
class UpstashService(BaseVectorStoreService):
    """Production vector store with hybrid search."""
    def __init__(
        self,
        embedding_model: Optional[BaseEmbeddingModel] = None,
        **kwargs: Any
    ):
        super().__init__(embedding_model)
        self._setup_upstash()
        
    def similarity_search(
        self,
        query: str,
        k: int = 3,
        **kwargs: Any,
    ) -> List[Document]:
        """Hybrid search with dense and sparse vectors."""
        query_embedding = self.embeddings.embed_query(query)
        sparse_vector = self.create_sparse_vector(query_embedding)
        
        results = self._index.query(
            vector=query_embedding,
            sparse_vector=sparse_vector,
            top_k=k,
            query_mode=QueryMode.HYBRID,
            fusion_algorithm=FusionAlgorithm.RRF
        )
        
        return self._process_results(results)
```

### LLM Service Architecture

The system uses a factory pattern for LLM provider management:

1. Provider Interface:
```python
class BaseLLMService(ABC):
    """Abstract base for LLM providers."""
    @abstractmethod
    def invoke(
        self,
        messages: List[BaseMessage],
        **kwargs: Any
    ) -> Union[str, BaseMessage]:
        """Generate LLM response."""
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[BaseMessage],
        **kwargs: Any
    ) -> Iterator[str]:
        """Stream LLM response."""
        pass
```

2. Factory Implementation:
```python
class LLMFactory:
    """Factory for creating LLM services."""
    @staticmethod
    def create_llm_service(
        provider: LLMProvider,
        model_name: Union[ClaudeModel, OpenAIModel],
        **kwargs: Any
    ) -> BaseLLMService:
        """Create appropriate LLM service."""
        if provider == LLMProvider.Anthropic:
            return BedrockService(model_name, **kwargs)
        elif provider == LLMProvider.OpenAI:
            return OpenAIService(model_name, **kwargs)
        elif provider == LLMProvider.Deepseek:
            return BedrockService(model_name, **kwargs)
        raise ValueError(f"Unsupported provider: {provider}")
```

3. Usage Example:
```python
# Initialize service
llm_service = LLMFactory.create_llm_service(
    provider=LLMProvider.Anthropic,
    model_name=ClaudeModel.CLAUDE3_5_HAIKU,
    streaming=True,
    temperature=0.7
)

# Create chat service
chat_service = ChatService(
    llm_service=llm_service,
    vector_store=vectorstore,
    persona_type=PersonaType.SCRIBE
)
```

## Development Process

### Running the Application

1. Start in development mode:
```bash
# Direct start
streamlit run main.py --server.port=8501 --server.address=0.0.0.0

# Or via Docker
docker-compose -f docker/dev/docker-compose.yml up
```

2. Development server features:
- Hot reload enabled
- Debug logging
- Memory profiling
- Local vector store

### Content Management

1. Adding new content:
```bash
# Add HTML files
cp your_content.html sampledata/

### 4. Testing

The project uses pytest for testing. Tests are organized into unit tests and integration tests.

#### Test Structure

```
tests/
├── conftest.py           # Common test fixtures and utilities
├── unit/                 # Unit tests
│   ├── chat/             # Tests for chat components
│   │   ├── graph/        # Tests for graph components
│   │   └── ...
│   └── services/         # Tests for service components
│       ├── llm/          # Tests for LLM services
│       ├── vectorstore/  # Tests for vector store services
│       └── ...
└── integration/          # Integration tests
```

#### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run tests for a specific component
pytest tests/unit/services/llm

# Run a specific test file
pytest tests/unit/services/llm/test_parser.py

# Run with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

#### Test Categories

**Unit Tests**

Unit tests focus on testing individual components in isolation. They use mocks to replace dependencies and focus on the behavior of the component being tested.

Key unit test areas:
- **LLM Services**: Tests for the LLM service implementations and utilities
- **Vector Store Services**: Tests for the vector store service implementations
- **Graph Components**: Tests for the LangGraph nodes and workflow
- **Chat Services**: Tests for the chat service implementations

**Integration Tests**

Integration tests focus on testing the interaction between components. They use real or realistic implementations of dependencies and focus on the behavior of the system as a whole.

#### Test Fixtures

Common test fixtures are defined in `conftest.py`. These include:

- `mock_embeddings`: A mock implementation of the Embeddings interface
- `mock_llm_service`: A mock implementation of the BaseLLMService interface
- `mock_vector_store`: A mock implementation of the BaseVectorStoreService interface
- `mock_prompt`: A mock implementation of the BasePrompt interface
- `sample_subquery`: A sample SubQuery object for testing
- `sample_enhanced_state`: A sample EnhancedChatState object for testing

#### Async Testing

Many components in LoreChat use asyncio for concurrent operations. The tests use pytest-asyncio to test these components. Async tests are marked with the `@pytest.mark.asyncio` decorator.

#### Mocking Strategy

The tests use the following mocking strategy:

1. **External Services**: External services like LLM APIs are always mocked
2. **Internal Dependencies**: Internal dependencies are mocked for unit tests but may use real implementations for integration tests
3. **State**: State objects are created fresh for each test to ensure isolation

#### Adding New Tests

When adding new tests:

1. Follow the existing directory structure
2. Use the appropriate fixtures from `conftest.py`
3. Mock external dependencies
4. Test both success and error cases
5. Add appropriate markers (e.g., `@pytest.mark.asyncio` for async tests)

### 5. Code Style

The project uses:
- flake8 for linting
- black for formatting
- mypy for type checking

Run style checks:
```bash
flake8 app/
black app/
mypy app/
```

## System Monitoring

### Logging System

1. Configuration:
```python
# config/logging.py
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "json"
        }
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    }
}
```

2. Usage:
```python
from app.monitoring import logger

# Component logging
logger.info("Processing message", extra={
    "thread_id": state.thread_id,
    "component": "chat_service",
    "action": "process_message"
})

# Error tracking
try:
    result = llm_service.invoke(messages)
except Exception as e:
    logger.error(
        "LLM invocation failed",
        exc_info=True,
        extra={
            "component": "llm_service",
            "provider": llm_service.provider
        }
    )
    raise
```

### Performance Metrics

1. Key Metrics:
```python
METRICS = {
    "response_time": Histogram(
        "chat_response_time_seconds",
        "Time taken to generate response",
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
    ),
    "token_usage": Counter(
        "llm_token_usage_total",
        "Total tokens used by LLM",
        ["model", "type"]
    ),
    "vector_ops": Counter(
        "vector_store_operations_total",
        "Vector store operation count",
        ["operation", "status"]
    ),
    "memory_usage": Gauge(
        "chat_memory_bytes",
        "Memory usage per chat session",
        ["thread_id"]
    )
}
```

2. Collection:
```python
# Measure response time
with METRICS["response_time"].time():
    response = chat_service.process_message(query)

# Track token usage
METRICS["token_usage"].labels(
    model=llm_service.model_name,
    type="completion"
).inc(response.usage.completion_tokens)

# Monitor vector operations
METRICS["vector_ops"].labels(
    operation="search",
    status="success"
).inc()
```

## Deployment

### Local Docker Build

Build production image:
```bash
cd docker/prod
docker build -t lorechat:latest .
```

### AWS Deployment

See [LoreChatCDK](https://github.com/laialex501/lorechat-cdk) for cloud deployment.

## Troubleshooting

### Common Issues

1. Vector Store Initialization
```bash
# Clear local store
rm -rf local_vectorstore/faiss/*
```

2. Session State
```bash
# Clear Streamlit cache
streamlit cache clear
```

3. Container Issues
```bash
# Rebuild with no cache
docker-compose build --no-cache
```

## Architecture

See [README.md](README.md) for architecture details.
