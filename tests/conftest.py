"""Common test fixtures for LoreChat tests."""

from typing import Any, Generator, List, Optional

import pytest
from app.chat.graph.constants import SubqueryStatus
from app.chat.graph.enhanced_state import EnhancedChatState, SubQuery
from app.services.embeddings.embeddings_base import BaseEmbeddingModel
from app.services.llm.llm_base import BaseLLMService
from app.services.prompts import BasePrompt, PersonaType
from app.services.vectorstore import BaseVectorStoreService
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import ChatGeneration, ChatResult, Document
from langchain.schema.messages import AIMessage, AIMessageChunk, BaseMessage
from pydantic import ConfigDict, Field


class MockEmbeddings(BaseEmbeddingModel):
    """Mock implementation of Embeddings for testing."""
    
    def __init__(self, dimensions=512):
        """Initialize with dimensions."""
        super().__init__(dimensions=dimensions)

    def embed_documents(self, texts):
        """Mock implementation of embed_documents."""
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(self, text):
        """Mock implementation of embed_query."""
        return [0.1, 0.2, 0.3]


class MockAsyncIterator:
    """Async iterator for testing async code."""

    def __init__(self, data):
        self.data = data
        self.index = 0

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.data):
            value = self.data[self.index]
            self.index += 1
            return value
        raise StopAsyncIteration


class MockLLMService(BaseLLMService):
    """Mock implementation of BaseLLMService for testing."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    responses: List[str] = Field(default_factory=list)

    def __init__(self, responses=None):
        """Initialize with optional predefined responses."""
        super().__init__()
        self.responses = responses or ["Mock response"]
        self.response_index = 0
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "mock_llm"

    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs: Any
    ) -> Generator[str, None, None]:
        """Generate a mock streaming response."""
        for response in self.responses:
            yield response

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Generator[AIMessageChunk, None, None]:
        """Stream a chat response."""
        for content in self.generate_response(messages, **kwargs):
            yield AIMessageChunk(content=content)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat response."""
        chunks = []
        for chunk in self.generate_response(messages, **kwargs):
            chunks.append(chunk)

        # Create a message with the combined content
        message = AIMessage(content="".join(chunks))
        
        # Create a ChatGeneration object with the message
        generation = ChatGeneration(message=message)
        
        # In newer versions of langchain, ChatResult requires additional fields
        return ChatResult(
            generations=[generation],
            llm_output={
                "token_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "model_name": "mock_model"
            }
        )


class MockVectorStore(BaseVectorStoreService):
    """Mock implementation of BaseVectorStoreService for testing."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    docs: List[Document] = Field(default_factory=list)
    embedding_function: BaseEmbeddingModel = Field(default_factory=lambda: MockEmbeddings(dimensions=512))

    def __init__(self, embedding_function=None, docs=None, **kwargs):
        """Initialize with embedding function and optional documents."""
        # Use MockEmbeddings as default if None is provided
        if embedding_function is None:
            embedding_function = MockEmbeddings(dimensions=512)
        
        # Call parent's init with embedding_function
        super().__init__(embedding_function=embedding_function, **kwargs)
        
        # Initialize docs if provided
        if docs is not None:
            self.docs = docs

    def similarity_search(self, query, k=4, **kwargs):
        """Mock implementation of similarity_search."""
        return self.docs[:k]

    def add_texts(self, texts, metadatas=None, **kwargs):
        """Mock implementation of add_texts for testing."""
        metadatas = metadatas or [{}] * len(list(texts))
        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            self.docs.append(Document(page_content=text, metadata=metadata))
        return ["id-" + str(i) for i in range(len(list(texts)))]


class MockPrompt(BasePrompt):
    """Mock implementation of BasePrompt for testing."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    input_variables: List[str] = Field(default=["input", "context", "chat_history"])
    system_template: str = Field(default="You are a mock assistant.")
    persona_type: PersonaType = Field(default=PersonaType.SCRIBE)

    def __init__(self, persona_type=PersonaType.SCRIBE):
        """Initialize with persona type."""
        super().__init__()
        self.persona_type = persona_type

    def format_response(self, answer, sources=None):
        """Format the response according to the persona."""
        sources = sources or []
        if not sources:
            return f"[MOCK PERSONA: {self.persona_type.value}] {answer}"

        formatted_sources = ", ".join(sources)
        return f"[MOCK PERSONA: {self.persona_type.value}] {answer}\n\nSources: {formatted_sources}"


@pytest.fixture
def mock_embeddings():
    """Fixture for mock embeddings."""
    return MockEmbeddings()


@pytest.fixture
def mock_llm_service():
    """Fixture for mock LLM service."""
    return MockLLMService()


@pytest.fixture
def mock_vector_store():
    """Fixture for mock vector store."""
    docs = [
        Document(page_content="Paris is the capital of France.", metadata={"url": "https://example.com/france"}),
        Document(page_content="Berlin is the capital of Germany.", metadata={"url": "https://example.com/germany"}),
        Document(page_content="Rome is the capital of Italy.", metadata={"url": "https://example.com/italy"})
    ]
    return MockVectorStore(docs=docs)


@pytest.fixture
def mock_prompt():
    """Fixture for mock prompt."""
    return MockPrompt()


@pytest.fixture
def sample_subquery():
    """Fixture for a sample subquery."""
    return SubQuery(
        text="What is the capital of France?",
        status=SubqueryStatus.COMPLETE,
        result="The capital of France is Paris.",
        sources=["https://example.com/france"]
    )


@pytest.fixture
def sample_enhanced_state():
    """Fixture for a sample enhanced state."""
    return EnhancedChatState(
        original_query="What is the capital of France?",
        query_complexity="simple",
        subqueries=[
            SubQuery(
                text="What is the capital of France?",
                status=SubqueryStatus.COMPLETE,
                result="The capital of France is Paris.",
                sources=["https://example.com/france"]
            )
        ],
        combined_answer="The capital of France is Paris."
    )
