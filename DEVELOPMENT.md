# LoreChat Development Guide

This guide covers the development setup, workflow, and deployment process for LoreChat.

## Prerequisites

- Docker and Docker Compose (or Finch as alternative)
- Python 3.9+
- OpenAI API key (if using OpenAI)
- AWS Account with Bedrock access (if using Bedrock)
- AWS CLI installed and configured (if using Bedrock)

## Environment Setup

### Container Build Systems

The application supports two container build systems:

#### Docker
Traditional Docker setup using Docker Desktop and docker-compose.

#### Finch
Alternative container build system that doesn't require Docker Desktop:

1. Install Finch:
```bash
brew install finch
```

2. Start Finch:
```bash
finch vm start
```

The application's Dockerfiles and docker-compose files work with both systems, controlled via the `USE_FINCH` build argument (defaults to true).

### LLM Configuration

#### OpenAI Setup

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the key in your environment file

#### Amazon Bedrock Setup

1. Verify AWS CLI installation:
```bash
aws --version
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Enable Bedrock Model Access:
   - AWS Console > Amazon Bedrock
   - Navigate to "Model access"
   - Click "Manage model access"
   - Enable "Anthropic Claude 3 Sonnet"
   - Save changes

4. Verify access:
```bash
aws bedrock list-foundation-models --region us-east-1
```

## Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd LoreChat
```

2. Create `.env` file:
```bash
# Environment
ENV=development
DEBUG=true
LOG_LEVEL=INFO
VECTOR_STORE_PATH=dev_vectorstore/faiss

# OpenAI Settings (if using openai provider)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# AWS Bedrock Settings (if using bedrock provider)
AWS_DEFAULT_REGION=us-east-1

# Upstash Vector Settings (optional for development)
UPSTASH_VECTOR_URL=your_upstash_url
UPSTASH_VECTOR_TOKEN=your_upstash_token
```

3. Start development environment:

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

Access the application at http://localhost:8501

## Vector Store Development

### Development Mode
- Uses FAISS for local development
- Initializes with content from `sampledata/`
- Configurable via `VECTOR_STORE_PATH`
- Persists between application restarts

### Production Mode
- Uses Upstash Vector
- Integrates with AWS Lambda pipeline
- Requires Upstash Vector credentials

## Testing

Run the test suite:
```bash
pytest tests/
```

Test categories:
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`

## Logging

- Logs stored in `logs/` directory
- Console output in development mode
- Configurable via LOG_LEVEL environment variable

## Container Development

Build and run development container:

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

Note: Configured for ARM64 architecture for optimal performance.

## CDK Deployment

The CDK stack supports both Docker and Finch.

Using Docker:
```bash
unset CDK_DOCKER
export USE_FINCH=false
cdk deploy
```

Using Finch:
```bash
# Start Finch VM if needed
finch vm start

# Configure CDK
export CDK_DOCKER=finch
export USE_FINCH=true
cdk deploy
```

Environment variables:
- CDK_DOCKER: Container build tool selection
- USE_FINCH: Container build process configuration

## Project Structure

```
LoreChat/
├── app/
│   ├── chat/           # Chat session management
│   ├── config/         # Configuration settings
│   ├── services/       # Core services
│   │   ├── embeddings/ # Embedding services
│   │   ├── llm/       # LLM providers
│   │   └── vectorstore/# Vector store implementations
│   ├── monitoring/     # Logging and metrics
│   └── ui/            # Streamlit UI components
├── docker/
│   ├── dev/           # Development environment
│   └── prod/          # Production environment
├── tests/             # Test suites
│   ├── integration/   # Integration tests
│   └── unit/         # Unit tests
├── sampledata/        # Sample HTML content
└── main.py           # Application entry point
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

For detailed architecture and design information, see the [README.md](README.md).
