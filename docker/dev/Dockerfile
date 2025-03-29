# Use Python 3.9 as base image
ARG USE_FINCH=true

FROM --platform=linux/amd64 python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    USE_FINCH=${USE_FINCH}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt  ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy .env.dev to .env
COPY .env.dev .env

# Create necessary directories
RUN mkdir -p logs faiss && \
    chmod -R 777 logs faiss

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE="dark" \
    STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=true \
    STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false

# Command to run the application with auto-reload for development
CMD ["streamlit", "run", "--server.runOnSave=true", "main.py"]
