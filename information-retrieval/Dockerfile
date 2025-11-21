FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.115.5 \
    uvicorn[standard]==0.32.1 \
    pydantic==2.10.3 \
    sentence-transformers==3.3.1 \
    scikit-learn==1.6.0 \
    numpy

# Copy application code
COPY data/ ./data/
COPY indexer.py .
COPY retriever.py .
COPY main.py .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]