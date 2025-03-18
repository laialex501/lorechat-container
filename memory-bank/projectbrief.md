# SiteChat Project Brief

## Overview
SiteChat is a Streamlit-based chatbot application that provides a conversational interface for accessing and querying website content. The project focuses on developing a containerized Python Streamlit frontend that will be deployed to AWS ECS, with the backend (LLM hosting and RAG) handled in a separate package.

## Core Requirements

### Functional Requirements
- Real-time chat interaction with website content
- Single chat session per user with session-based history
- No persistence between sessions
- No user configuration or file upload capabilities
- Development mode with local vector database (FAISS)
- Sample data loading capability

### Technical Requirements
- Python 3.9+ with Streamlit framework
- LangChain for chatbot implementation
- Flexible LLM integration (OpenAI or Amazon Bedrock)
- FAISS vector store for development
- Docker containerization
- AWS service integration readiness

### Performance Requirements
- Support for ~1000 concurrent users
- Optimized response times
- Efficient resource utilization
- Streamlined container performance

## Project Scope

### In Scope
- Streamlit-based chat interface development
- LLM integration (OpenAI/Bedrock)
- Local vector store implementation
- Docker development environment
- Logging and monitoring
- Testing infrastructure
- AWS integration preparation

### Out of Scope
- Backend LLM hosting
- RAG implementation details
- Production vector store
- User authentication
- Long-term chat history persistence

## Development Stack

### Core Technologies
- Frontend: Streamlit
- LLM Integration: LangChain
- Vector Store: FAISS (development)
- Containerization: Docker
- Cloud Platform: AWS (ECS target)

### Development Tools
- Docker and Docker Compose
- Python 3.9+
- AWS CLI
- Git version control

### Key Dependencies
- streamlit>=1.32.0
- langchain>=0.1.0
- langchain-community>=0.0.16
- faiss-cpu>=1.7.4
- pydantic>=2.0.0
- boto3>=1.34.0

## Deployment Strategy

### Development
- Local Docker environment
- FAISS vector store
- OpenAI/Bedrock LLM integration
- Environment-specific configuration

### Production (Planned)
- AWS ECS deployment
- AWS service integration
- Production logging and monitoring
- Scalability optimizations

## Success Criteria
1. Functional chat interface with real-time interaction
2. Successful LLM integration with both providers
3. Efficient local development environment
4. Comprehensive testing coverage
5. Production-ready containerization
6. AWS deployment readiness

## Timeline
6-week development plan divided into phases:
1. Project Setup (Week 1)
2. Core Development (Week 2)
3. Enhanced Features (Week 3)
4. Docker Development (Week 4)
5. Production Preparation (Week 5)
6. AWS Integration (Week 6)

## Risk Factors
1. LLM API reliability and costs
2. Container performance optimization
3. AWS service integration complexity
4. Scalability challenges
5. Development environment consistency

## Project Governance
- Git-based version control
- Docker-based development workflow
- Comprehensive testing requirements
- Documentation standards
- Code review process
