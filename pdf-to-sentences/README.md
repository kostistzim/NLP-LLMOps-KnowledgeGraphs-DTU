# PDF to Sentences Extraction

REST API for extracting sentences from PDF files using GROBID and spaCy.

## Overview

This service accepts PDF uploads and returns a list of extracted sentences. It uses GROBID for high-quality PDF text extraction and spaCy for sentence tokenization.

## Requirements

- Python 3.11
- Docker and Docker Compose
- Conda environment (see `llm-operations.yml` in parent directory)

## Installation

### Local Development
```bash
# Activate conda environment
conda activate llm-operations

# Download spaCy model
python -m spacy download en_core_web_sm

# Start GROBID service
docker run -p 8070:8070 lfoppiano/grobid:0.8.0

# Run the API
uvicorn main:app --reload
```

### Docker Compose
```bash
docker compose up --build
```

## API Usage

**Endpoint:** `POST /v1/extract-sentences`

**Request:**
```bash
curl -F pdf_file=@document.pdf http://localhost:8000/v1/extract-sentences
```

**Response:**
```json
{
  "sentences": [
    "First sentence from the document.",
    "Second sentence from the document.",
    ...
  ]
}
```

## Testing
```bash
# Run tests
python test_main.py

# Or with pytest
pytest test_main.py
```

Test file `2303.15133.pdf` should be placed in the project root.

## Architecture

- **FastAPI**: Web framework and API endpoints
- **GROBID**: PDF to XML/text conversion
- **spaCy**: Sentence boundary detection

## Project Structure
```
pdf-to-sentences/
├── main.py                 # FastAPI application
├── pdf_processor.py        # GROBID communication
├── sentence_extractor.py   # spaCy sentence tokenization
├── test_main.py           # Test suite
├── Dockerfile             # API container
├── compose.yaml           # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## Configuration

Environment variables (`.env`):
- `GROBID_URL`: GROBID service endpoint (default: `http://localhost:8070`)

## Submission

Create submission archive:
```bash
# From project root
cd pdf-to-sentences
git archive -o pdf-to-sentences-submission.zip HEAD```

## Notes

- GROBID container may take 30-60 seconds to start
- First request to GROBID may be slower as models load
- PDF extraction quality depends on PDF structure and formatting