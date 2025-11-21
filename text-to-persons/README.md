# Person Name Extraction API

REST API for extracting person names from text using CampusAI LLM.

## Overview

This service accepts text input and returns a list of extracted person names using large language models via the CampusAI API.

## Requirements

- Python 3.11
- Docker
- CampusAI API key (from campusai.compute.dtu.dk)
- Conda environment (see `llm-operations.yml` in parent directory)

## CampusAI Setup

### Get Access

1. Visit https://campusai.compute.dtu.dk
2. Sign in with DTU credentials
3. Wait for admin approval (account starts in 'pending' mode)
4. Once approved, you can access the service

### Get API Key

1. Log in to CampusAI
2. Go to Settings (upper right corner)
3. Navigate to Account section
4. Generate and copy your OpenAI API Key

### Configure API Key

Create `~/.env` file in your home directory:
```bash
echo "CAMPUSAI_API_KEY=your_actual_key_here" > ~/.env
```

Replace `your_actual_key_here` with your actual API key from CampusAI.

**Important:** Never commit this file to git!

## Installation

### Local Development
```bash
# Activate conda environment
conda activate llm-operations

# Verify API key is set
cat ~/.env

# Run the API
uvicorn main:app --reload
```

### Docker
```bash
# Build image
docker build -t text-to-persons:latest .

# Run container with API key from ~/.env
docker run --rm -p 8000:8000 --env-file ~/.env text-to-persons:latest
```

## API Usage

**Endpoint:** `POST /v1/extract-persons`

**Request:**
```bash
curl -X POST http://localhost:8000/v1/extract-persons \
  -H 'Content-Type: application/json' \
  -d '{"text":"Einstein and von Neumann meet each other."}'
```

**Response:**
```json
{
  "persons": ["Einstein", "von Neumann"]
}
```

## Examples
```bash
# Example 1
curl -X POST http://localhost:8000/v1/extract-persons \
  -H 'Content-Type: application/json' \
  -d '{"text":"Ms Mette Frederiksen is in New York today."}'

# Response: {"persons": ["Mette Frederiksen"]}

# Example 2
curl -X POST http://localhost:8000/v1/extract-persons \
  -H 'Content-Type: application/json' \
  -d '{"text":"Einstein and von Neumann meet each other."}'

# Response: {"persons": ["Einstein", "von Neumann"]}
```

## Testing
```bash
# Run tests (requires valid API key)
python test_main.py

# Or with pytest
pytest test_main.py
```

Note: Tests requiring real API calls will be skipped if using a test API key.

## Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
text-to-persons/
├── main.py                # FastAPI application
├── campusai_client.py     # CampusAI API client
├── prompts.py             # LLM prompt templates
├── test_main.py           # Test suite
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore patterns
└── README.md             # This file
```

## Architecture

- **FastAPI**: Web framework and REST API
- **CampusAI**: DTU's LLM service (OpenAI-compatible API)
- **OpenAI Python SDK**: API client library
- **Few-shot prompting**: Examples in prompt for better accuracy
- **Defensive parsing**: Handles various LLM response formats

## Available Models

Check https://campusai.compute.dtu.dk for current model list. Common models:
- Qwen3 (default)
- gpt-oss
- DeepSeek-R1
- Gemma3
- Llama3.1

## Security

- API key stored in `~/.env` (home directory, not in project)
- Never commit `.env` file to git
- Docker reads API key at runtime via `--env-file`
- API key only accessible on your machine

## Integration with CampusAI

This project uses the CampusAI OpenAI-compatible API:

- **Base URL**: `https://campusai.compute.dtu.dk/api/v1`
- **Authentication**: OpenAI API Key from your CampusAI account
- **Compatibility**: Works with standard OpenAI Python SDK

You can use the same API key in other tools (Cursor, Marimo, etc.) by configuring:
1. Override OpenAI Base URL: `https://campusai.compute.dtu.dk/api/v1`
2. API Key: Your CampusAI OpenAI API Key

## Troubleshooting

### "CAMPUSAI_API_KEY not configured"
- Ensure `~/.env` file exists and contains your API key
- Check: `cat ~/.env`

### "401 Unauthorized"
- Your API key may be invalid or expired
- Generate a new key from CampusAI Settings

### "Account pending"
- Your CampusAI account needs admin approval
- Contact CampusAI administrators

### Docker can't find API key
- Ensure using `--env-file ~/.env` flag
- Check file exists: `ls -la ~/.env`

## Submission

Create submission archive:
```bash
git archive -o latest.zip HEAD
```

**Note:** `.env` file is not included in submission (as per `.gitignore`). Graders must use their own CampusAI API key.

## Notes

- Requires active DTU network connection (or VPN)
- First request may be slower as CampusAI loads models
- Uses temperature=0 for deterministic results
- Prompt uses few-shot learning with examples
- Response parser handles JSON and text formats
- Model availability may change - check CampusAI for current list