# DTU Course Information Retrieval API

Search engine for DTU courses using sparse (TF-IDF), dense (sentence embeddings), and hybrid retrieval methods.

## Overview

This service provides semantic and keyword-based search over DTU course data, including course titles and learning objectives.

## Features

- **Multiple retrieval modes:**
  - Sparse: TF-IDF keyword matching
  - Dense: Semantic embeddings (sentence-transformers)
  - Hybrid: Weighted combination of both
- **Two indexing levels:**
  - Course-level: Search entire courses
  - Objective-level: Search individual learning objectives
- **Three search types:**
  - Find similar courses by ID
  - Search courses by text query
  - Search learning objectives by text query

## Requirements

- Python 3.11
- Docker (optional)
- Internet connection (first run downloads sentence-transformers model)
- Conda environment (see `llm-operations.yml` in parent directory)

## Installation

### Local Development
```bash
# Activate conda environment
conda activate llm-operations

# Ensure you have courses.json in data/
mkdir -p data
# (place courses.json in data/)

# Run the API (builds indices on startup, takes ~30 seconds)
uvicorn main:app --reload
```

### Docker
```bash
# Build image
docker build -t course-retrieval:latest .

# Run container
docker run --rm -p 8000:8000 course-retrieval:latest
```

**Note:** First startup takes ~30 seconds to build indices.

## API Usage

### 1. Find Similar Courses
```bash
curl "http://localhost:8000/v1/courses/02451/similar?top_k=5&mode=dense" | jq
```

**Parameters:**
- `course_id` (path): Source course ID (e.g., "02451")
- `top_k` (query): Number of results (1-50, default: 10)
- `mode` (query): "sparse", "dense", or "hybrid" (default: "dense")
- `alpha` (query): Hybrid weight, 0.0-1.0 (default: 0.5)

**Response:**
```json
{
  "query_course_id": "02451",
  "results": [
    {
      "course_id": "02460",
      "title": "02460 Advanced Machine Learning",
      "score": 0.873
    }
  ],
  "mode": "dense",
  "top_k": 5
}
```

### 2. Search Courses
```bash
curl "http://localhost:8000/v1/search?query=machine%20learning&top_k=10&mode=dense" | jq
```

**Parameters:**
- `query` (query): Search text (required)
- `top_k` (query): Number of results (1-50, default: 10)
- `mode` (query): "sparse", "dense", or "hybrid" (default: "dense")
- `alpha` (query): Hybrid weight (default: 0.5)

**Response:**
```json
{
  "query": "machine learning",
  "results": [
    {
      "course_id": "02460",
      "title": "02460 Advanced Machine Learning",
      "score": 0.912
    }
  ],
  "mode": "dense"
}
```

### 3. Search Learning Objectives
```bash
curl "http://localhost:8000/v1/objectives/search?query=dimensionality%20reduction&top_k=10" | jq
```

**Parameters:**
- `query` (query): Search text (required)
- `top_k` (query): Number of results (1-50, default: 10)
- `mode` (query): Retrieval mode (default: "dense")
- `alpha` (query): Hybrid weight (default: 0.5)

**Response:**
```json
{
  "query": "dimensionality reduction",
  "results": [
    {
      "course_id": "02451",
      "title": "02451 Introduction to Machine Learning",
      "objective": "Match practical problems to standard...",
      "score": 0.834
    }
  ]
}
```

### 4. Health Check
```bash
curl "http://localhost:8000/v1/health" | jq
```

**Response:**
```json
{
  "status": "ok",
  "index_sizes": {
    "courses": 55,
    "objectives": 600
  }
}
```

## Retrieval Modes

### Sparse (TF-IDF)
- Keyword-based matching
- Fast
- Good for exact terms, acronyms
- Uses: unigrams + bigrams, lowercase, English stop words

### Dense (Sentence Embeddings)
- Semantic understanding
- Handles synonyms ("ML" ~ "machine learning")
- Model: `distiluse-base-multilingual-cased-v2`
- 512-dimensional embeddings

### Hybrid
- Combines both approaches
- Formula: `score = alpha * dense + (1-alpha) * sparse`
- Default alpha = 0.5 (equal weight)
- alpha = 1.0 → pure dense
- alpha = 0.0 → pure sparse

## Testing
```bash
# Run tests (slow first time due to index building)
python test_main.py

# Or with pytest
pytest test_main.py -v
```

## Documentation

Interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
course-retrieval/
├── data/
│   └── courses.json         # DTU course data
├── indexer.py               # Index building logic
├── retriever.py             # Search/retrieval logic
├── main.py                  # FastAPI application
├── test_main.py            # Test suite
├── Dockerfile              # Container configuration
└── README.md               # This file
```

## Architecture

### Data Processing

**Course-level documents:**
```
"02451 Introduction to Machine Learning\nUnderstand neural networks\nApply gradient descent..."
```
One document per course (title + all objectives).

**Objective-level documents:**
```
"02451 Introduction to Machine Learning - Understand neural networks"
"02451 Introduction to Machine Learning - Apply gradient descent"
```
One document per learning objective.

### Indexing

Built once on startup:
1. Load courses.json
2. Create course-level documents
3. Create objective-level documents
4. Build TF-IDF matrices (sparse)
5. Generate embeddings (dense)

**Startup time:** ~30 seconds  
**Memory usage:** ~150 MB  
**Query time:** ~20-100 ms

### Retrieval

Uses cosine similarity:
- Query → vector (TF-IDF or embedding)
- Compare with all documents
- Sort by similarity
- Return top K

## Performance

- **Courses indexed:** ~100-200
- **Objectives indexed:** ~1000-2000
- **Index build time:** 30 seconds
- **Query latency:** 20-100ms
- **Memory footprint:** ~150 MB

## Limitations

- First startup slow (downloads sentence-transformers model)
- Indices built in-memory (no persistence)
- Limited to English text
- No query spelling correction
- No result caching

## Submission

Create submission archive:
```bash
git archive -o latest.zip HEAD
```

## Examples

### Compare retrieval modes:
```bash
# Sparse - keyword matching
curl "http://localhost:8000/v1/search?query=statistics&mode=sparse" | jq

# Dense - semantic matching
curl "http://localhost:8000/v1/search?query=statistics&mode=dense" | jq

# Hybrid - best of both
curl "http://localhost:8000/v1/search?query=statistics&mode=hybrid&alpha=0.7" | jq
```

### Find courses similar to statistics:
```bash
curl "http://localhost:8000/v1/courses/02402/similar?top_k=5" | jq
```

### Search for specific learning objectives:
```bash
curl "http://localhost:8000/v1/objectives/search?query=principal%20component%20analysis" | jq
```

## Notes

- Sentence-transformers model (~100MB) downloads on first run
- Indices rebuild on each server restart
- Results sorted by relevance (highest score first)
- Scores range from 0.0 to 1.0
- Course IDs must match those in courses.json