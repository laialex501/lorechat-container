# Development environment
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    # Streamlit configuration
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE=dark \
    STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=true \
    STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements first to leverage layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Setup application directories
RUN mkdir -p logs faiss && \
    chmod -R 777 logs faiss

# Copy application code and development environment file
COPY . .
COPY .env.dev .env

# Expose Streamlit port
EXPOSE 8501

# Development-specific command with auto-reload
CMD ["streamlit", "run", "--server.runOnSave=true", "main.py"]
