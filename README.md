# LoreChat

A Streamlit-based chatbot for providing a conversational interface to website content.

## Features

- Real-time chat interaction with website content
- Development mode with local vector database (FAISS)
- Production mode with Upstash Vector database
- Flexible LLM integration (OpenAI or Amazon Bedrock)
- Containerized deployment ready
- Comprehensive logging and monitoring
- AWS service integration ready

## Prerequisites

- Docker and Docker Compose (or Finch as an alternative)
- Python 3.9+
- OpenAI API key (if using OpenAI)
- AWS Account with Bedrock access (if using Bedrock)
- AWS CLI installed and configured (if using Bedrock)

## Container Build Options

The application supports two container build systems:

### Docker
Traditional Docker setup using Docker Desktop and docker-compose.

### Finch
Alternative container build system that doesn't require Docker Desktop:

1. Install Finch:
```bash
brew install finch
```

2. Start Finch:
```bash
finch vm start
```

The application's Dockerfiles and docker-compose files are configured to work with both Docker and Finch. The build system is controlled via the `USE_FINCH` build argument, which defaults to true.

## LLM Setup

The application supports two LLM providers for development: OpenAI and Amazon Bedrock. Choose your preferred provider by setting the `LLM_PROVIDER` environment variable.

### OpenAI Setup

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the key in your environment file (see Development Setup section)

### Amazon Bedrock Setup

1. Ensure you have AWS CLI installed:
```bash
aws --version
```

2. Configure AWS credentials:
```bash
aws configure
```
Enter your AWS credentials when prompted:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

3. Enable Amazon Bedrock Model Access:
   - Go to AWS Console > Amazon Bedrock
   - Navigate to "Model access"
   - Click "Manage model access"
   - Enable access to "Anthropic Claude 3 Sonnet"
   - Click "Save changes"

4. Verify Bedrock access:
```bash
aws bedrock list-foundation-models --region us-east-1
```

## Development Setup

### Vector Store Configuration
The application supports two vector store modes:

#### Development Mode
- Uses FAISS vector store for local development
- Automatically initializes with content from `sampledata/` directory
- Vector store path configurable via `VECTOR_STORE_PATH` (defaults to `dev_vectorstore/faiss`)
- Processes HTML files from `sampledata/` directory
- Persists between application restarts

#### Production Mode
- Uses Upstash Vector for production deployment
- Integrates with AWS Lambda data processing pipeline
- Efficient vector storage and retrieval
- Automatic scaling and management
- Requires Upstash Vector credentials (see Environment Setup)

1. Clone the repository:
```bash
git clone <repository-url>
cd LoreChat
```

2. Create a `.env` file in the project root based on `.env.dev`:
```bash
# Environment
ENV=development
DEBUG=true
LOG_LEVEL=INFO
VECTOR_STORE_PATH=dev_vectorstore/faiss

# OpenAI Settings (required if using openai provider)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# AWS Bedrock Settings (required if using bedrock provider)
AWS_DEFAULT_REGION=us-east-1  # Your AWS region
# Note: AWS credentials should be configured via aws configure

# Upstash Vector Settings (optional for development)
UPSTASH_VECTOR_URL=your_upstash_url
UPSTASH_VECTOR_TOKEN=your_upstash_token
```

3. Start the development environment:

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

The application will be available at http://localhost:8501

## Project Structure

```
LoreChat/
├── app/
│   ├── chat/           # Chat session management
│   ├── config/         # Configuration settings
│   ├── services/       # Core services (LLM, Vector Store)
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
├── requirements.txt   # Python dependencies
├── main.py           # Application entry point
└── README.md         # Project documentation
```

## Development Workflow

1. Make changes to the code
2. Run tests:
```bash
pytest tests/
```
3. Start the development server:
```bash
streamlit run main.py
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Logging

Logs are stored in the `logs` directory and are also output to the console in development mode.

## Container Development

Build and run the development container:

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

Note: The container is configured to run on ARM64 architecture for optimal performance on modern systems. The platform is automatically set in both development and production environments.

## CDK Deployment

The CDK stack supports both Docker and Finch for building container images. By default, it will use Finch if available.

Using Docker:
```bash
unset CDK_DOCKER
export USE_FINCH=false
cdk deploy
```

Using Finch:
```bash
# Start Finch VM if not running
finch vm start

# Set CDK to use Finch for container builds
export CDK_DOCKER=finch
export USE_FINCH=true
cdk deploy
```

Note: The CDK_DOCKER environment variable tells CDK which container build tool to use, while USE_FINCH configures the container build process itself. Both need to be set correctly for Finch to work properly.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT License
