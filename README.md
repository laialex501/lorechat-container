# SiteChat

A Streamlit-based chatbot for providing a conversational interface to website content.

## Features

- Real-time chat interaction with website content
- Development mode with local vector database (FAISS)
- OpenAI integration for development
- Containerized deployment ready
- Comprehensive logging and monitoring
- AWS service integration ready

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- OpenAI API key

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SiteChat
```

2. Create a `.env` file in the project root:
```bash
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=INFO
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
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
