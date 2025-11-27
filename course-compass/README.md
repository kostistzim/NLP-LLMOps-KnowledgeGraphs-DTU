# CourseCompass

**Intelligent Course Planning System for DTU Students**

*Backend • NLP • Knowledge Graphs • LLM Integration • Study Path Planning*

---

## Overview

CourseCompass is an intelligent course planning system designed for DTU students. It automatically analyzes course learning objectives, processes official DTU prerequisite information, builds a full knowledge graph representing course dependencies, and generates optimal study paths using graph algorithms combined with LLM-generated explanations.

The system integrates classical NLP, modern LLM reasoning (via CampusAI), vector semantic search (FAISS), and NetworkX graph algorithms. It is designed as a production-quality academic project meeting requirements for NLP experimentation, LLM pipeline design, knowledge graph construction, and backend API development.

---

## Table of Contents

- [Motivation](#motivation)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Data Sources](#data-sources)
- [NLP and Embedding Pipeline](#nlp-and-embedding-pipeline)
- [Prerequisite Extraction](#prerequisite-extraction)
- [Semantic Course Matching](#semantic-course-matching)
- [Knowledge Graph Construction](#knowledge-graph-construction)
- [Path Planning Algorithms](#path-planning-algorithms)
- [LLM-Based Explanation System](#llm-based-explanation-system)
- [API (FastAPI)](#api-fastapi)
- [Frontend (Streamlit)](#frontend-streamlit)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Setup and Installation](#setup-and-installation)
- [Running the API](#running-the-api)
- [Running the Frontend](#running-the-frontend)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)
- [Performance Characteristics](#performance-characteristics)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [Project Information](#project-information)
- [License](#license)

---

## Motivation

DTU students often struggle to determine which courses they must take before higher-level courses. Although official prerequisites exist, they are embedded in text, inconsistent across courses, and rarely sufficient for complete planning. Students must manually browse dozens of course pages to understand dependencies.

CourseCompass automates this process by:

- Analyzing learning objectives
- Extracting prerequisite concepts with LLMs
- Matching concepts to courses using semantic search
- Constructing a full dependency graph (based on official prerequisites)
- Computing optimal study paths using graph algorithms
- Generating natural language explanations of the recommended path

---

## Features

### Core Capabilities

- Full DTU course catalog indexing (over 1500 courses)
- Semantic search over course descriptions using embeddings
- Official prerequisite parsing and transformation into structured JSON
- Knowledge graph construction using official prerequisites
- Fast shortest-path computation (Dijkstra) for study planning
- LLM-generated explanations via CampusAI
- Search-by-topic over embeddings using FAISS
- Full REST API with FastAPI
- Frontend UI in Streamlit (search, path planning, graph visualization)

### NLP and LLM Features

- DSPy-based prerequisite extraction
- LangChain processing pipeline
- Structured extraction signatures
- Natural language explanations for study paths
- RAG-style similarity search for course queries

---

## System Architecture
```
User → FastAPI Backend →
  Data Layer (course loading, FAISS index) →
  Prerequisite Extraction Layer →
  Knowledge Graph Builder →
  Path Planning Engine →
  LLM Explanation Layer →
  JSON Response
```

The architecture integrates NLP, vector search, knowledge graphs, and LLMs into a single coherent pipeline.

---

## Data Sources

### Primary Data: `dtu_courses.jsonl`

Contains course codes, titles, ECTS, objectives, content, teacher, department, language, semester.

### Derived Data: `prerequisites_official.jsonl`

Parsed from official DTU prerequisite text using `precompute_prereqs_official.py`.

---

## NLP and Embedding Pipeline

- Embeddings generated using a multilingual sentence-transformer model
- 512-dimensional vectors
- FAISS FlatL2 index for exact similarity search
- Documents constructed from title, learning objectives, truncated content, teacher info
- Query latency typically under 10 ms

---

## Prerequisite Extraction

`precompute_prereqs_official.py` parses DTU's official prerequisite free text into structured JSON with course codes.

**Example:**
```
01002 requires 01001 and 01003
```

LLM-based DSPy extraction is available but not required for official data.

---

## Semantic Course Matching

`course_matcher.py` implements:

- Concept-to-course mapping
- Ranking based on similarity
- Aggregation of concept coverage across courses

Used for generating explanation context and identifying where a concept is taught.

---

## Knowledge Graph Construction

`graph_builder.py` creates a directed acyclic graph (DAG) from official prerequisites.

**Graph properties:**
- 1565 nodes
- 2397 edges
- Directed, acyclic, stable

Edges represent prerequisite relationships. Nodes store metadata.

---

## Path Planning Algorithms

`path_planner.py` includes:

- Dijkstra's algorithm for shortest path
- BFS for collecting all prerequisites
- ECTS total computation
- Handling cases where the student has completed courses or has none

Paths returned as sequences of course codes plus metadata.

---

## LLM-Based Explanation System

`explainer.py` generates natural-language explanations for the study plan.

Uses LangChain with CampusAI:
- Temperature 0.3 for balanced determinism
- Template describes learning progression, reasoning, and timeline

The LLM summarizes why the recommended path makes sense.

---

## API (FastAPI)

`main.py` provides the backend service with major endpoints:

- `GET /v1/health`
- `GET /v1/search`
- `GET /v1/analyze-prerequisites/{course_code}`
- `POST /v1/generate-path`

Responses include course metadata, prerequisite analysis, computed path, and LLM explanations.

OpenAPI documentation is available at `/docs`.

---

## Frontend (Streamlit)

A lightweight frontend can be built using Streamlit.

**Core features:**
- Search for similar courses
- Form to select completed courses and target course
- Display recommended plan
- Graph visualization using pyvis or Streamlit network visualization libraries

The frontend sends API requests to the backend and displays results interactively.

---

## Technology Stack

- **Backend:** FastAPI, Pydantic, Python 3.11
- **NLP:** sentence-transformers, scikit-learn
- **Vector Search:** FAISS
- **LLM Integration:** LangChain, DSPy, CampusAI
- **Graph Processing:** NetworkX
- **Frontend:** Streamlit
- **Testing:** pytest
- **Containerization:** Docker
- **Deployment:** Uvicorn

---

## Directory Structure
```
├── config.py
├── indexer.py
├── prerequisite_extractor.py
├── precompute_prereqs_official.py
├── course_matcher.py
├── graph_builder.py
├── path_planner.py
├── explainer.py
├── main.py
├── test_main.py
├── Dockerfile
├── pyproject.toml
├── README.md
├── data/
└── frontend/ (optional Streamlit UI)
```

---

## Setup and Installation

Requires Python 3.11 and a CampusAI API key.

**Install dependencies:**
```bash
pip install -e .
pip install -e ".[dev]"
```

**Create a `~/.env` file with:**
```
CAMPUSAI_API_KEY=your_key
CAMPUSAI_API_BASE=your_base_url
CAMPUSAI_MODEL=your_model
```

---

## Running the API

**Development:**
```bash
uvicorn main:app --reload
```

**Production:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

API documentation at `/docs`.

---

## Running the Frontend

In `frontend/` directory:
```bash
streamlit run app.py
```

The frontend communicates with the backend API.

---

## Docker Deployment

**Build image:**
```bash
docker build -t course-compass .
```

**Run container:**
```bash
docker run -p 8000:8000 \
  -e CAMPUSAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  course-compass
```

---

## Testing

Execute:
```bash
pytest -v
pytest --cov=. --cov-report=html
```

Includes tests for vector search, graph integrity, endpoints, and prerequisite logic.

---

## Performance Characteristics

- **Vector search latency:** under 50 ms
- **Path planning:** under 1 ms
- **LLM explanation:** 1 to 3 seconds
- **Startup:** loads embeddings, graph, and course metadata
- **Memory usage:** under 100 MB

---

## Limitations

- Static data (must be regenerated when DTU updates course catalog)
- Does not include semester scheduling
- Only official prerequisites
- Does not recommend specializations automatically
- Front-end prototype is minimal

---

## Future Work

### Short-term
- Better UI
- Graph visualization
- Caching LLM responses

### Medium-term
- Implicit prerequisite extraction
- Specialization paths
- Danish language support

### Long-term
- Integration with DTU's semester schedule
- Career-path advisor
- Collaborative filtering

---

## Project Information

**Academic project at Technical University of Denmark (DTU)**

- **Student:** Konstantinos Tzimoulias
- **Supervisor:** Finn Årup Nielsen

---

## License

MIT License