# LoreChat System Patterns

## Stack Organization
```mermaid
graph TD
    subgraph "Stack Organization"
        A[Infrastructure Stack] --> B[Service Stack]
        A --> C[Data Stack]
        A --> D[Monitoring Stack]
    end
```

## Core Architecture

### System Overview
```mermaid
graph TD
    A[Streamlit UI] --> B[Chat Manager]
    B --> C[LLM Service]
    B --> D[Vector Store]
    
    C --> E[OpenAI/Bedrock]
    D --> F[Upstash Vector]
    
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
        E[Vector Store Service]
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
- Abstract interfaces for LLM with factory-based instantiation
- Factory-based vector store implementation with external Vector DB
- Streaming response handling
- Data processing pipeline with Lambda functions

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
    C->>V: Get Context (Sync)
    V-->>C: Context
    C->>L: Generate
    L-->>UI: Stream Response
```

### 3. Data Processing Pipeline
```mermaid
sequenceDiagram
    participant S as Source Bucket
    participant P as Processing Lambda
    participant B as Processed Bucket
    participant V as Vectorization Lambda
    participant U as Vector DB
    participant BE as Bedrock

    S->>P: New file event
    P->>P: Clean & prepare data
    P->>B: Store processed data
    B->>V: Processed file event
    V->>BE: Generate embeddings
    V->>U: Store vectors
```

### 4. Key Patterns
- Configuration management with Pydantic
- Dependency injection for services
- Repository pattern for vector store
- Error handling and recovery
- State management (session-based)
- Event-driven data processing
- Secure credential management

## Infrastructure

### AWS Integration
```mermaid
graph TD
    subgraph VPC
        A[ECS Service]
        B[Lambda Functions]
    end
    
    subgraph AWS Services
        C[S3 Buckets]
        D[Bedrock]
        E[Secrets Manager]
    end
    
    subgraph External
        F[Upstash Vector]
    end
    
    A -->|Query| F
    B -->|Read/Write| C
    B -->|Generate Embeddings| D
    B -->|Get Credentials| E
    B -->|Store Vectors| F
```

### Development
- Docker-based local environment
- Hot reloading enabled
- Comprehensive testing setup
- Monitoring and logging
- Lambda function development
- Data pipeline testing

### Security
- Environment-based configuration
- Secret management
- Input validation
- Resource limits
- AWS IAM integration
- S3 bucket policies
- Lambda execution roles
