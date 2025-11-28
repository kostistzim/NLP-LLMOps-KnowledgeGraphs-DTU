FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from pyproject.toml first (cache efficient)
COPY pyproject.toml ./
COPY README.md ./
RUN pip install .

# Copy full project
COPY . .

# Ensure data directory exists
RUN mkdir -p data

EXPOSE 8000

# Use urllib (stdlib) instead of requests for healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/healt
