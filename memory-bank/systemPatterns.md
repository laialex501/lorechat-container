# LoreChat System Patterns

## Architectural Layers

```mermaid
graph TD
    subgraph "Frontend Layer"
        A[Streamlit UI]
        B[Session State]
    end
    
    subgraph "Service Layer"
        C[ChatServiceFactory]
        D[BaseChatService]
        E[AgenticChatService]
    end
    
    subgraph "LangGraph Layer"
        F[Enhanced State]
        G[Graph Nodes]
        H[Checkpointer]
    end
    
    subgraph "Infrastructure Layer"
        I[Vector Store]
        J[LLM Provider]
        K[LLM Configuration]
        L[Monitoring]
    end
    
    A --> B
    B --> C
    C --> E
    E --> F
    F --> G
    G --> I
    G --> J
    K --> G
    H --> F
```

## Core Design Patterns

### 1. Interface Segregation Pattern

The system uses clear interface boundaries to separate concerns and enable flexible implementations:

```mermaid
graph TD
    A[BaseChatService] -->|Interface| B[AgenticChatService]
    A -->|Interface| C[Future Implementations]
    
    D[BaseVectorStore] -->|Interface| E[UpstashVectorStore]
    D -->|Interface| F[FAISSVectorStore]
    
    G[BaseLLMService] -->|Interface| H[OpenAIService]
    G -->|Interface| I[BedrockService]
    G -->|Interface| J[AnthropicService]
```

**Key Benefits**:
- Decouples implementation from interface
- Enables runtime provider swapping
- Simplifies testing with mock implementations
- Provides clear contract boundaries

### 2. Factory Pattern

Factories handle the complexity of object creation and dependency management:

```mermaid
graph TD
    A[ChatServiceFactory] --> B[AgenticChatService]
    A --> C[VectorStoreFactory]
    A --> D[LLMFactory]
    
    C --> E[Vector Store Instance]
    D --> F[LLM Service Instance]
    
    B --> E
    B --> F
```

**Key Benefits**:
- Centralizes creation logic
- Handles dependency injection
- Abstracts infrastructure details
- Simplifies client code

### 3. Enhanced State Management Pattern

The system uses a rich state model that extends LangGraph's base state:

```mermaid
graph TD
    A[EnhancedChatState] --> B[Messages]
    A --> C[Subqueries]
    A --> D[Original Query]
    A --> E[Query Complexity]
    A --> F[Combined Answer]
    A --> G[Thread ID]
    
    C --> H[SubQuery 1]
    C --> I[SubQuery 2]
    C --> J[SubQuery N]
    
    subgraph "SubQuery State"
        K[Unique ID]
        L[Query Text]
        M[Processing Status]
        N[Retrieved Documents]
        O[Refinement Count]
        P[Result]
        Q[Sources]
    end
    
    H --> K
    H --> L
    H --> M
    H --> N
    H --> O
    H --> P
    H --> Q
```

**Key Benefits**:
- Explicit state tracking
- Comprehensive error handling
- Clear state transitions
- Support for complex workflows

### 4. Strategy Pattern for LLM Selection

The system dynamically selects appropriate LLMs for different reasoning tasks:

```mermaid
graph TD
    A[LLM Configuration] --> B[Node Type]
    B --> C{Selection Strategy}
    
    C -->|Decomposition| D[Reasoning-optimized LLM]
    C -->|Processing| E[Balanced LLM]
    C -->|Evaluation| F[Efficient LLM]
    C -->|Refinement| G[Creative LLM]
    C -->|Answer| H[Comprehensive LLM]
    C -->|Combination| I[Synthesis LLM]
    C -->|Response| J[User-selected LLM]
    
    K[Fallback Mechanism] --> C
```

**Key Benefits**:
- Optimized model selection
- Cost-performance balance
- Specialized reasoning capabilities
- Graceful fallback mechanisms

### 5. Agentic Workflow Pattern

The system implements a sophisticated graph-based workflow for query processing:

```mermaid
sequenceDiagram
    participant U as User
    participant D as Decomposition
    participant P as Processing
    participant C as Combination
    participant R as Response
    
    U->>D: Query
    D->>D: Analyze & Decompose
    D->>P: Subqueries
    
    par Process Subqueries
        P->>P: Process Subquery 1
        P->>P: Process Subquery 2
        P->>P: Process Subquery N
    end
    
    P->>C: All Results
    C->>C: Combine Results
    C->>R: Combined Answer
    R->>U: Formatted Response
```

**Key Benefits**:
- Clear reasoning paths
- Parallel processing capabilities
- Explicit state transitions
- Comprehensive error handling

## Architectural Decisions

### 1. Node Responsibility Separation

Each node in the graph has a single, well-defined responsibility:

| Node | Responsibility | Design Pattern |
|------|----------------|----------------|
| Decomposition | Query analysis and breakdown | Strategy Pattern |
| Processing | Parallel subquery handling | Observer Pattern |
| Combination | Result synthesis | Composite Pattern |
| Response | Final formatting | Template Method |

**Rationale**: Clear separation of concerns enables focused testing, easier maintenance, and better error isolation.

### 2. Asynchronous Processing

The system uses asyncio for concurrent subquery processing:

```mermaid
graph TD
    A[Processing Node] --> B[Async Task Manager]
    B --> C{Concurrent Tasks}
    
    C --> D[Subquery 1]
    C --> E[Subquery 2]
    C --> F[Subquery N]
    
    D --> G[Result Collection]
    E --> G
    F --> G
```

**Rationale**: Parallel processing significantly reduces response time for complex queries while maintaining thread safety.

### 3. Specialized LLM Selection

Different reasoning tasks use different LLM models based on their strengths:

| Task | Model Characteristics | Rationale |
|------|----------------------|-----------|
| Decomposition | Strong reasoning | Complex analysis requires sophisticated reasoning |
| Evaluation | Fast, efficient | Quick assessment of document relevance |
| Refinement | Creative, flexible | Query reformulation benefits from creative thinking |
| Answer | Comprehensive | Detailed answer generation needs thorough understanding |
| Combination | Synthesis ability | Combining multiple perspectives requires synthesis skills |

**Rationale**: Matching model capabilities to task requirements optimizes both cost and performance.

## Development Guidelines

### Service Layer Design

1. **Interface First**
   - Define clear service interfaces before implementation
   - Use abstract base classes for common functionality
   - Follow dependency injection principles
   - Design for testability

2. **Factory Implementation**
   - Centralize creation logic in factories
   - Handle dependencies internally
   - Provide simple creation methods
   - Abstract infrastructure details

3. **Provider Abstraction**
   - Create provider-agnostic interfaces
   - Implement provider-specific adapters
   - Enable runtime provider swapping
   - Handle provider-specific error cases

### Graph Layer Design

1. **State Management**
   - Define explicit state schema
   - Use typed state objects
   - Track processing status comprehensively
   - Handle state transitions atomically

2. **Node Implementation**
   - Focus each node on a single responsibility
   - Implement parallel processing where appropriate
   - Use specialized LLMs for different tasks
   - Handle errors gracefully with fallbacks

3. **Error Handling**
   - Implement node-specific error handling
   - Provide graceful degradation paths
   - Preserve partial results when possible
   - Enable comprehensive error reporting

### Testing Approach

1. **Unit Testing**
   - Test each node in isolation
   - Validate state transitions
   - Check error handling paths
   - Mock dependencies for focused testing

2. **Integration Testing**
   - Test node interactions
   - Validate workflow paths
   - Check error propagation
   - Monitor performance metrics

3. **System Testing**
   - Test end-to-end workflows
   - Validate streaming behavior
   - Check thread persistence
   - Verify specialized LLM selection
