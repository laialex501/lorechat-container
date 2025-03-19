# SiteChat Project Brief

## Overview
SiteChat is a Streamlit-based chatbot application for accessing and querying website content. It features a containerized Python Streamlit frontend deployable to AWS ECS, with backend LLM hosting and RAG handled separately.

## Core Requirements
- Real-time chat interaction with website content
- Session-based user interactions (no persistence)
- Local vector database (FAISS) for development
- Python 3.9+ with Streamlit, LangChain, and Docker
- Flexible LLM integration (OpenAI or Amazon Bedrock)
- AWS service integration readiness
- Support for ~1000 concurrent users

## Project Scope
- Streamlit chat interface
- LLM integration (OpenAI/Bedrock)
- Local vector store (FAISS)
- Docker development environment
- Logging, monitoring, and testing
- AWS integration preparation

## Key Technologies
- Frontend: Streamlit
- LLM Integration: LangChain
- Vector Store: FAISS (dev)
- Containerization: Docker
- Cloud: AWS (ECS target)

## Deployment
- Dev: Local Docker, FAISS, OpenAI/Bedrock
- Prod (Planned): AWS ECS, scalability optimizations

## Success Criteria
1. Functional real-time chat interface
2. LLM integration (OpenAI and Bedrock)
3. Efficient local dev environment
4. Comprehensive testing
5. Production-ready containerization
6. AWS deployment readiness

## Timeline
6-week plan: Setup, Core Dev, Features, Docker, Production Prep, AWS Integration

## Key Challenges
- LLM API reliability and costs
- Container performance
- AWS integration complexity
- Scalability
- Dev environment consistency

## Project Governance
Git version control, Docker workflow, testing, documentation, code reviews
