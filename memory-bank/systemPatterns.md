# LoreChat System Patterns

## Core Architecture

```mermaid
graph TD
    subgraph "Frontend"
        A[Streamlit UI]
        B[Session State]
    end
    
    subgraph "LangGraph Layer"
        C[State Manager]
        D[Graph Nodes]
        E[Checkpointer]
    end
    
    subgraph "Infrastructure"
        F[Vector Store]
        G[LLM Provider]
        H[Monitoring]
    end
    
    A --> B
    B --> C
    C --> D
    D --> F
    D --> G
    E --> C
```

## Key Design Patterns

### 1. Graph State
```python
class ChatState(MessagesState):
    messages: List[BaseMessage]
    retrieved_docs: List[Document]
```

### 2. Node Implementation
```python
def retrieve_context(state: ChatState):
    """Get relevant docs from vector store."""
    docs = vector_store.get_relevant_documents(
        state["messages"][-1].content
    )
    return {"retrieved_docs": docs}

def generate_response(state: ChatState):
    """Generate response with sources."""
    sources = [doc.metadata["url"] for doc in state["retrieved_docs"]]
    response = llm.invoke(format_prompt(state))
    return {"messages": [AIMessage(content=response + "\n\nSources: " + sources)]}
```

### 3. Graph Workflow
```mermaid
sequenceDiagram
    participant U as User
    participant S as State
    participant R as Retrieve
    participant G as Generate
    
    U->>S: Message
    S->>R: Get Context
    R-->>S: Update Docs
    S->>G: Generate
    G-->>S: Update Messages
    S->>U: Response
```

## Infrastructure

### Service Integration
```mermaid
graph TD
    subgraph "AWS"
        A[Streamlit App]
        B[Bedrock]
        C[Secrets]
    end
    
    subgraph "Vector Store"
        D[Upstash]
        E[Hybrid Search]
    end
    
    A -->|Query| D
    A -->|Generate| B
    D -->|Metadata| A
```

## Development Guidelines

### Graph Development
1. State Management
   - Define clear state schema
   - Use typed state classes
   - Handle state updates atomically

2. Node Design
   - Pure functions for nodes
   - Clear input/output contracts
   - Handle errors gracefully

3. Checkpointing
   - Use thread IDs for sessions
   - Implement state persistence
   - Handle recovery cases

### Testing Strategy
1. Node Testing
   - Test state transitions
   - Validate metadata handling
   - Check error cases

2. Graph Testing
   - Test workflow paths
   - Validate checkpointing
   - Monitor performance

3. Integration Testing
   - Test source attribution
   - Validate thread persistence
   - Check streaming behavior
