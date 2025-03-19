# SiteChat System Patterns

## Core Architecture

### System Overview
```mermaid
graph TD
    A[Streamlit UI] --> B[Chat Manager]
    B --> C[LLM Service]
    B --> D[Vector Store]
    
    C --> E[OpenAI/Bedrock]
    D --> F[FAISS/AWS Store]
    
    G[Configuration] --> A
    G --> B
    G --> C
    G --> D
```

### Key Components
```mermaid
graph TD
    subgraph Frontend
        A[UI Layer]
        B[Stream Display]
    end
    
    subgraph Backend
        C[Chat Service]
        D[LLM Service]
        E[Vector Store]
    end
    
    subgraph Infrastructure
        F[Logging]
        G[Config]
        H[Monitoring]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    D --> F
    E --> F
```

## Core Design Patterns

### 1. Service Layer
- Abstract interfaces for LLM and vector store
- Provider-agnostic implementations
- Factory-based service instantiation
- Streaming response handling

### 2. Data Flow
```mermaid
sequenceDiagram
    participant U as User
    participant UI as UI
    participant C as Chat
    participant L as LLM
    participant V as VectorStore
    
    U->>UI: Question
    UI->>C: Process
    C->>V: Get Context
    V-->>C: Context
    C->>L: Generate
    L-->>UI: Stream Response
```

### 3. Key Patterns
- Configuration management with Pydantic
- Dependency injection for services
- Repository pattern for vector store
- Error handling and recovery
- State management (session-based)

## Infrastructure

### AWS Integration
```mermaid
graph TD
    A[Container] --> B[ECS]
    B --> C[CloudWatch]
    B --> D[Bedrock]
    B --> E[Vector Store]
```

### Development
- Docker-based local environment
- Hot reloading enabled
- Comprehensive testing setup
- Monitoring and logging

### Security
- Environment-based configuration
- Secret management
- Input validation
- Resource limits
- AWS IAM integration
