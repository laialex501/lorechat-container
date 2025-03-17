# SiteChat

A Streamlit-based chatbot for providing a conversational interface to website content.

## Features

- Real-time chat interaction with website content
- Development mode with local vector database (FAISS)
- Flexible LLM integration (OpenAI or Amazon Bedrock)
- Containerized deployment ready
- Comprehensive logging and monitoring
- AWS service integration ready

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- OpenAI API key (if using OpenAI)
- AWS Account with Bedrock access (if using Bedrock)
- AWS CLI installed and configured (if using Bedrock)

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
- Default region (e.g., us-west-2)
- Default output format (json)

3. Enable Amazon Bedrock Model Access:
   - Go to AWS Console > Amazon Bedrock
   - Navigate to "Model access"
   - Click "Manage model access"
   - Enable access to "Anthropic Claude 3 Sonnet"
   - Click "Save changes"

4. Verify Bedrock access:
```bash
aws bedrock list-foundation-models --region us-west-2
```

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SiteChat
```

2. Create a `.env` file in the project root based on `.env.dev`:
```bash
# Environment
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# LLM Configuration
LLM_PROVIDER=bedrock  # Options: openai, bedrock

# OpenAI Settings (required if using openai provider)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# AWS Bedrock Settings (required if using bedrock provider)
AWS_DEFAULT_REGION=us-west-2  # Your AWS region
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
# Note: AWS credentials should be configured via aws configure
```

3. Start the development environment:
```bash
cd docker/dev
docker-compose up --build
```

The application will be available at http://localhost:8501

## Project Structure

```
SiteChat/
├── app/
│   ├── chat/           # Chat session management
│   ├── config/         # Configuration settings
│   ├── services/       # Core services (LLM, Vector Store)
│   ├── monitoring/     # Logging and metrics
│   └── ui/            # Streamlit UI components
├── docker/
│   ├── dev/           # Development environment
│   └── prod/          # Production environment
├── tests/             # Test suites
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

## Docker Development

Build and run the development container:
```bash
cd docker/dev
docker-compose up --build
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

[Add License Information]
