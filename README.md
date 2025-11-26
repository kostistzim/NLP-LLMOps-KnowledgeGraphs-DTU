# NLP, LLMOps & Knowledge Graphs 

This repository collects all assignments and projects from the DTU course **NLP, LLMOps & Knowledge Graphs**, focusing on:

- Classical NLP and sentiment analysis
- LLM-based APIs via CampusAI
- Information retrieval and semantic search
- Wikidata and knowledge graphs
- Retrieval-Augmented Generation (RAG)
- Curriculum planning with knowledge graphs and LLMs

All projects are implemented as **FastAPI** microservices and are container-ready with **Docker**.

---

## Project Overview

In order of progression:

1. `up-and-running/`  
   Course Evaluation Sentiment Analysis API (dictionary-based, bilingual)

2. `pdf-to-sentences/`  
   PDF-to-sentences pipeline using GROBID and spaCy

3. `text-to-persons/`  
   LLM-based person name extraction via CampusAI

4. `person-to-wikidata/`  
   Wikidata entity linking and SPARQL API for people

5. `information-retrieval/`  
   DTU course search (sparse, dense and hybrid retrieval)

6. `rag/`  
   Retrieval-Augmented Generation over documents (RAG pipeline built on previous components)

7. `course-compass/`  
   Intelligent course planning system for DTU students (NLP, LLMs and knowledge graphs)

Each subfolder has its **own** `README.md` with full details; this root README gives a high-level map and quick-start overview.

---

## Common Setup

### Requirements

- Python 3.11
- `conda` (recommended)
- Docker / Docker Compose (for container runs)
- CampusAI API key (for LLM-based projects: `text-to-persons`, `rag`, `course-compass`, parts of `information-retrieval`)

### Conda Environment

The repository assumes a shared environment defined in `llm-operations.yml` (in the repo root or parent directory):

```bash
conda env create -f llm-operations.yml
conda activate llm-operations

# CampusAI Configuration

Some services use DTU's CampusAI as an OpenAI-compatible LLM backend.

1. Get an API key from: https://campusai.compute.dtu.dk  
2. Create a `~/.env` file:
```bash
echo "CAMPUSAI_API_KEY=your_actual_key_here" > ~/.env
```

`~/.env` is never committed to git. Docker services read it via `--env-file ~/.env`.

## Repository Structure
```
.
├── up-and-running/              # 1. Sentiment Analysis API (course evaluations)
├── pdf-to-sentences/           # 2. PDF → sentences extraction (GROBID + spaCy)
├── text-to-persons/            # 3. LLM-based person name extraction
├── person-to-wikidata/         # 4. Wikidata entity linking + SPARQL API
├── information-retrieval/      # 5. DTU course retrieval (sparse/dense/hybrid)
├── rag/                        # 6. Retrieval-Augmented Generation over docs
├── course-compass/             # 7. CourseCompass – course planning system
├── llm-operations.yml          # Shared conda environment
└── README.md                   # This file
```

## 1. Up-and-Running – Course Evaluation Sentiment Analysis API

**Folder:** `up-and-running/`  
**Tech:** FastAPI, pure Python, Docker  
**Goal:** Build a small, interpretable sentiment analysis API under a 200 MB container size.

### Description

A REST API for analyzing sentiment in Danish and English course evaluations, with:

- Bilingual support (automatic detection of Danish and English)
- Dictionary-based sentiment scoring with:
  - Negation handling ("not good", "ikke god")
  - Intensifiers ("very", "meget", "rigtig")
  - Multi-word sentiment scoring
- Score range: -5 (very negative) to 5 (very positive)
- About 95.8% accuracy on 24 test cases (±1 tolerance)
- Lightweight Docker image (about 71 MB total)

### Key Endpoints

- `POST /v1/sentiment` — Returns a single numeric sentiment score.
- `POST /v1/sentiment/detailed` — Returns score, detected language and original text.

### Example
```bash
curl -X POST "http://localhost:8000/v1/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text":"Det var en god lærer."}'
```

### Quick Start
```bash
cd up-and-running
pip install -r requirements.txt
uvicorn main:app --reload

docker build -t sentiment-api .
docker run -p 8000:8000 sentiment-api
```

**Docs:** http://localhost:8000/docs

---

## 2. PDF-to-Sentences – GROBID and spaCy

**Folder:** `pdf-to-sentences/`  
**Tech:** FastAPI, GROBID, spaCy, Docker Compose  
**Goal:** Robustly convert research PDFs to clean sentences as preprocessing for downstream NLP/RAG.

### Description

A REST API that:

- Uses GROBID for high-quality PDF → XML/text extraction
- Uses spaCy for sentence boundary detection
- Returns a list of sentences as JSON

### Endpoint

`POST /v1/extract-sentences`

**Input:** multipart/form-data with a PDF file  
**Output:**
```json
{
  "sentences": [
    "First sentence from the document.",
    "Second sentence from the document."
  ]
}
```

### Quick Start
```bash
cd pdf-to-sentences
conda activate llm-operations
python -m spacy download en_core_web_sm
docker run -p 8070:8070 lfoppiano/grobid:0.8.0
uvicorn main:app --reload
```

Or using Docker Compose:
```bash
docker compose up --build
```

---

## 3. Text-to-Persons – LLM-based Person Name Extraction

**Folder:** `text-to-persons/`  
**Tech:** FastAPI, CampusAI (OpenAI-compatible), Docker  
**Goal:** Extract person names from arbitrary text using LLMs via CampusAI.

### Description

Service that:

- Uses CampusAI through the OpenAI Python SDK
- Uses few-shot prompting for robust extraction
- Handles multiple LLM output formats
- Returns a clean list of person names

### Endpoint

`POST /v1/extract-persons`

### Example
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

### Quick Start
```bash
cd text-to-persons
conda activate llm-operations
uvicorn main:app --reload

docker build -t text-to-persons .
docker run --rm -p 8000:8000 --env-file ~/.env text-to-persons
```

**Docs:** http://localhost:8000/docs

---

## 4. Person-to-Wikidata – Entity Linking and SPARQL API

**Folder:** `person-to-wikidata/`  
**Tech:** FastAPI, Wikidata Search API, SPARQL, asyncio, Docker  
**Goal:** Resolve person names to Wikidata entities and query structured information.

### Description

Two-step workflow:

1. **Entity Linking**
   - Uses Wikidata Search API (wbsearchentities)
   - Resolves names → QIDs

2. **SPARQL Property Queries**
   - Date of birth (P569)
   - Doctoral students (P185)
   - Political party (P102)
   - Doctoral advisor (P184)
   - `/v1/all` runs multiple SPARQL queries in parallel with asyncio.

### Endpoints

- `POST /v1/birthday`
- `POST /v1/students`
- `POST /v1/all`
- `POST /v1/political-party`
- `POST /v1/supervisor`

### Example
```bash
curl -X POST http://localhost:8000/v1/birthday \
  -H 'Content-Type: application/json' \
  -d '{"person":"Niels Bohr"}'
```

**Response:**
```json
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "birthday": "1885-10-07"
}
```

### Quick Start
```bash
cd person-to-wikidata
conda activate llm-operations
uvicorn main:app --reload

docker build -t person-to-wikidata .
docker run -p 8000:8000 person-to-wikidata
```

**Docs:** http://localhost:8000/docs

---

## 5. Information-Retrieval – DTU Course Search Engine

**Folder:** `information-retrieval/`  
**Tech:** FastAPI, TF-IDF, sentence-transformers  
**Goal:** Provide search over DTU courses using sparse, dense and hybrid retrieval.

### Description

Features:

- Sparse (TF-IDF) retrieval
- Dense (semantic embeddings) retrieval
- Hybrid scoring combining both
- Course-level indexing
- Learning-objective–level indexing

### Key Endpoints

- `GET /v1/courses/{course_id}/similar`
- `GET /v1/search`
- `GET /v1/objectives/search`
- `GET /v1/health`

### Example
```bash
curl "http://localhost:8000/v1/search?query=machine%20learning&top_k=10&mode=dense"
```

### Quick Start
```bash
cd information-retrieval
conda activate llm-operations
uvicorn main:app --reload

docker build -t course-retrieval .
docker run -p 8000:8000 course-retrieval
```

---

## 6. RAG – Retrieval-Augmented Generation

**Folder:** `rag/`  
**Tech:** FastAPI, PDF-to-sentences, embeddings, vector store, CampusAI  
**Goal:** Provide grounded LLM answers over indexed documents.

### Pipeline

1. Extract sentences from PDFs
2. Chunk & embed text
3. Store in vector index
4. Retrieve relevant chunks
5. Generate answer using CampusAI

### Typical Endpoints

- `POST /v1/index-pdf`
- `POST /v1/query`
- `GET /v1/health`

See `rag/README.md` for exact details.

---

## 7. CourseCompass – Intelligent Course Planning System

**Folder:** `course-compass/`  
**Tech:** FastAPI, LangChain, DSPy, CampusAI, FAISS, NetworkX  
**Goal:** Automatically infer prerequisites from learning objectives and generate study paths.

### Solution Overview

- Extracts prerequisite concepts using DSPy + LLMs
- Matches concepts to courses via FAISS semantic search
- Builds a directed knowledge graph of course dependencies
- Computes optimal prerequisite paths
- Generates natural-language explanations

### Key Endpoints

- `GET /v1/health`
- `GET /v1/search`
- `GET /v1/analyze-prerequisites/{course_code}`
- `POST /v1/generate-path`

### Example
```json
{
  "target_course": "02460",
  "completed_courses": ["01005"]
}
```

**Response:**
```json
{
  "path": [
    {"course_code": "02450", "title": "Introduction to Machine Learning"},
    {"course_code": "02460", "title": "Advanced Machine Learning"}
  ],
  "total_ects": 10
}
```

### Quick Start
```bash
cd course-compass
conda activate llm-operations
pip install -e .
python main.py
```

**Docs:** http://localhost:8000/docs

### Testing
```bash
conda activate llm-operations
pytest test_main.py -v
```

Some tests require:
- CampusAI key (LLM-based APIs)
- Running GROBID (PDF extraction)

---

## Documentation and Credits

Each project folder includes its own README.

CourseCompass also includes:
- `course-compass/TECHNICAL_DOCUMENTATION.md`

**Author:** Konstantinos (Kostis) Tzimoulias  
**Institution:** Technical University of Denmark (DTU)