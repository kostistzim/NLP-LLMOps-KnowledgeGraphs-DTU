# DTU Course RAG System

Retrieval-Augmented Generation system for answering questions about DTU courses using semantic search and LLMs.

## Features

- **Search endpoint:** Find courses by keywords or topics
- **RAG endpoint:** Ask natural language questions, get AI-generated answers
- **Streamlit UI:** User-friendly chat interface
- **Multiple retrieval modes:** Sparse (TF-IDF), dense (embeddings), hybrid
- **Teacher queries:** Find courses by instructor name
- **ECTS queries:** Ask about course credits

## Requirements

- Python 3.11
- Docker (optional)
- CampusAI API key
- Conda environment (see `llm-operations.yml`)

## Setup

### CampusAI API Key

Add to `~/.env`:
```bash
CAMPUSAI_API_KEY=your_key_here
```

### Local Development
```bash
# Activate environment
conda activate llm-operations

# Install streamlit
pip install streamlit

# Ensure data file exists
ls data/dtu_courses.jsonl
```

## Running Locally

### With UI (Recommended)

**Terminal 1 - Start API:**
```bash
uvicorn main:app --reload
```

**Terminal 2 - Start UI:**
```bash
streamlit run ui.py
```

**Access:**
- UI: http://localhost:8501
- API docs: http://localhost:8000/docs

### API Only
```bash
uvicorn main:app --reload
```

### Docker
```bash
# Build
docker build -t course-rag:latest .

# Run (need to pass .env)
docker run --rm -p 8000:8000 --env-file ~/.env course-rag:latest
```

Note: Docker runs API only. For UI, run Streamlit locally.

## API Usage

### Search Courses
```bash
curl "http://localhost:8000/v1/search?query=machine%20learning&mode=dense" | jq
```

**Response:**
```json
{
  "query": "machine learning",
  "mode": "dense",
  "results": [
    {
      "course_code": "02460",
      "title": "02460 Advanced Machine Learning",
      "score": 0.89
    }
  ]
}
```

### Ask Questions (RAG)
```bash
curl "http://localhost:8000/v1/ask?query=How%20many%20ECTS%20is%20Tue%20Herlau%27s%20course" | jq
```

**Response:**
```json
{
  "query": "How many ECTS is Tue Herlau's course?",
  "answer": "Tue Herlau is responsible for 02465 Introduction to reinforcement learning and control, which gives 5 ECTS points.",
  "retrieved_courses": [
    {
      "course_code": "02465",
      "title": "02465 Introduction to reinforcement learning and control"
    }
  ]
}
```

## Example Queries
```bash
# Find MRI courses
curl "http://localhost:8000/v1/ask?query=Are%20there%20courses%20about%20MRI" | jq

# Find teacher's course
curl "http://localhost:8000/v1/ask?query=Which%20course%20is%20Hiba%20Nassar%20involved%20in" | jq

# Check co-teaching
curl "http://localhost:8000/v1/ask?query=Does%20Ivana%20Konvalenka%20teach%20with%20another%20teacher" | jq
```

## Testing
```bash
python test_main.py
# or
pytest test_main.py -v
```

## Architecture
```
User Query
  ↓
Retriever (sparse/dense/hybrid)
  ↓
Top-K Courses Retrieved
  ↓
Format as Context
  ↓
LLM (via DSPy + CampusAI)
  ↓
Natural Language Answer
```

## Project Structure
```
course-rag/
├── data/
│   └── dtu_courses.jsonl
├── indexer.py          # Load data, build indices
├── retriever.py        # Search logic
├── rag.py              # LLM integration
├── main.py             # FastAPI app
├── ui.py               # Streamlit interface
├── test_main.py        # Tests
├── Dockerfile
├── .gitignore
└── README.md
```

## Documentation

- Streamlit UI: http://localhost:8501
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

- First startup: ~30-60 seconds (builds indices, loads models)
- Requires active CampusAI API key
- Memory usage: ~200-300 MB
- Query latency: 2-5 seconds (includes LLM call)
- Streamlit runs on port 8501, API on port 8000

## Submission
```bash
git archive -o latest.zip HEAD
```