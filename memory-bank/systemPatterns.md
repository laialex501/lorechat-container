# SiteChat System Patterns

## System Architecture

### High-Level Architecture
```mermaid
graph TD
    A[Streamlit UI] --> B[Chat Manager]
    B --> C[LLM Service]
    B --> D[Vector Store]
    
    C --> E[OpenAI Provider]
    C --> F[Bedrock Provider]
    
    D --> G[FAISS Store]
    D --> H[Future AWS Store]
    
    I[Configuration] --> A
    I --> B
    I --> C
    I --> D

    %% Streaming Flow
    E --> J[Stream Handler]
    F --> J
    J --> A
```

### Component Structure
```mermaid
graph TD
    subgraph UI Layer
        A[Streamlit Pages]
        B[UI Components]
        S[Stream Display]
    end
    
    subgraph Service Layer
        C[Chat Service]
        D[LLM Service]
        E[Vector Store Service]
        T[Stream Handler]
    end
    
    subgraph Infrastructure
        F[Logging]
        G[Configuration]
        H[Monitoring]
    end
    
    A --> B
    B --> S
    S --> T
    B --> C
    C --> D
    C --> E
    D --> T
    D --> F
    D --> G
    E --> F
    E --> G
    F --> H
```

## Design Patterns

### 1. Service Abstraction Pattern
- **Interface Segregation**: Clear service interfaces for LLM and vector store
- **Provider Abstraction**: Unified interface for different LLM providers
- **Factory Pattern**: Service instantiation based on configuration
- **Streaming Pattern**: Async generator pattern for response streaming

Example (LLM Service with Streaming):
```python
class BaseLLMService(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[BaseMessage],
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        pass

class OpenAIService(BaseLLMService):
    async def generate_response(
        self,
        messages: List[BaseMessage],
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        if not stream:
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
        
        async def stream_response() -> AsyncGenerator[str, None]:
            async for chunk in self.llm.astream(messages):
                if isinstance(chunk, AIMessageChunk):
                    yield chunk.content
        
        return stream_response()
```

### 2. Streaming Implementation Pattern
- **Async Generators**: Stream response chunks
- **State Management**: Track streaming state
- **Error Handling**: Graceful error recovery
- **UI Updates**: Real-time content display

Example (Chat Service Streaming):
```python
class ChatService:
    async def process_message(
        self,
        message: str,
        history: List[ChatMessage],
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        # Concurrent context fetching
        context_task = asyncio.create_task(
            self.vector_store.get_relevant_context(message)
        )
        
        # Process history while fetching context
        messages = self._format_history(history)
        context = await context_task
        
        if stream:
            return self._stream_response(messages, context)
        return await self._generate_response(messages, context)
```

### 3. UI Streaming Pattern
- **Progressive Updates**: Show response as it arrives
- **State Management**: Track partial responses
- **Visual Feedback**: Indicate streaming status
- **Error Recovery**: Handle stream interruptions

Example (UI Implementation):
```python
async def handle_streaming_response(generator):
    full_response = []
    async for chunk in generator:
        full_response.append(chunk)
        st.session_state.current_response = "".join(full_response)
        st.experimental_rerun()
```

### 4. Configuration Management
- **Settings Hierarchy**: Environment-based configuration
- **Validation**: Pydantic models for type safety
- **Environment Isolation**: Development vs production settings
- **Streaming Config**: Stream-specific settings

### 5. Dependency Injection
- **Service Registry**: Centralized service management
- **Configuration Injection**: Runtime provider selection
- **Testing Support**: Easy service mocking
- **Stream Handlers**: Pluggable streaming components

### 6. Repository Pattern (Vector Store)
- **Data Access Abstraction**: Unified vector store interface
- **Implementation Swapping**: Easy switching between stores
- **Query Optimization**: Efficient similarity search
- **Concurrent Access**: Parallel context fetching

## Component Relationships

### 1. UI Layer
```mermaid
graph LR
    A[Main Page] --> B[Chat Component]
    B --> C[Message List]
    B --> D[Input Field]
    B --> E[Session State]
    B --> F[Stream Display]
```

### 2. Service Layer
```mermaid
graph TD
    A[Chat Manager] --> B[Message Handler]
    A --> C[Context Manager]
    B --> D[LLM Service]
    C --> E[Vector Store]
    D --> F[Provider Factory]
    D --> G[Stream Handler]
```

### 3. Data Flow with Streaming
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant C as Chat Manager
    participant L as LLM Service
    participant V as Vector Store
    
    U->>UI: Enter Question
    UI->>C: Process Input
    par Concurrent Operations
        C->>V: Get Context
        C->>UI: Show User Message
    end
    V-->>C: Return Context
    C->>L: Generate Response
    loop Streaming
        L-->>C: Yield Chunk
        C->>UI: Update Display
        UI->>U: Show Progress
    end
```

## Technical Decisions

### 1. Framework Selection
- **Streamlit**: Rapid UI development with streaming support
- **LangChain**: LLM integration with async streaming
- **FAISS**: Efficient vector similarity search
- **Docker**: Container-based deployment

### 2. State Management
- Session-based chat history
- Streaming state tracking
- No persistent storage
- In-memory vector store for development

### 3. Error Handling
- Graceful stream interruption
- User-friendly error messages
- Comprehensive logging
- Error recovery strategies

### 4. Performance Optimization
- Concurrent context fetching
- Efficient stream processing
- Resource-aware container configuration
- Optimized vector search

## AWS Integration Design

### 1. Service Integration Points
```mermaid
graph TD
    A[SiteChat Container] --> B[ECS Service]
    B --> C[CloudWatch]
    B --> D[Bedrock]
    B --> E[Future Vector Store]
    D --> F[Stream Processing]
```

### 2. Container Architecture
- ECS task definition
- Resource allocation
- Stream handling
- Health monitoring
- Auto-scaling rules

### 3. Monitoring Integration
- Stream performance metrics
- CloudWatch metrics
- Log aggregation
- Performance monitoring
- Error tracking

## Development Patterns

### 1. Local Development
- Docker Compose setup
- Environment configuration
- Hot reloading
- Stream testing
- Debug logging

### 2. Testing Strategy
- Stream testing framework
- Unit test structure
- Integration testing
- Performance testing
- Mock services

### 3. Deployment Pipeline
- Container building
- Stream testing
- Testing stages
- Environment promotion
- Monitoring setup

## Security Patterns

### 1. Configuration Security
- Environment variable management
- Secret handling
- API key rotation
- Access control
- Stream security

### 2. Runtime Security
- Input validation
- Stream sanitization
- Error sanitization
- Resource limits
- Container isolation

### 3. Integration Security
- AWS IAM roles
- API authentication
- Stream encryption
- Network security
- Data protection
