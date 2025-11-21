FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.115.5 \
    uvicorn[standard]==0.32.1 \
    pydantic==2.10.3 \
    pypdf==4.3.1 \
    pdfplumber==0.11.4 \
    python-multipart==0.0.9 \
    httpx==0.27.2 \
    spacy==3.7.6

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application files
COPY sentence_extractor.py .
COPY pdf_processor.py .
COPY main.py .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]