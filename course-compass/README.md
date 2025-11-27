# CourseCompass

**Intelligent Course Planning System for DTU Students**

CourseCompass automatically analyzes course information and learning objectives, combines it with official DTU prerequisite data, builds a dependency graph of courses, and generates optimal study paths using NLP, LLMs, and knowledge graphs.

---

##  Project Overview

### Problem

- DTU students struggle to determine which courses they should take before enrolling in advanced courses.
- The course catalog mixes explicit prerequisites (in dense free-text) with implicit expectations in the learning objectives.
- Students must manually inspect many course pages to understand the prerequisite structure.
- It is hard to see end-to-end paths (from basic math/programming to advanced ML/AI courses).

### Solution

CourseCompass automates this process by:

1. **Extracting prerequisite concepts** from course learning objectives using LLMs (offline / precomputation).
2. **Parsing official DTU prerequisite rules** from the course descriptions into structured JSON.
3. **Matching concepts to courses** that teach them using semantic search over embeddings.
4. **Building a knowledge graph** of course dependencies (currently using the official DTU prerequisites).
5. **Finding optimal study paths** using graph algorithms (Dijkstra / shortest path).
6. **Explaining recommendations** in natural language using LLMs, enriched with official prerequisite information.

The current demo graph covers the **full DTU course catalog** (1565 courses, 2397 edges) based on official prerequisites.

---

##  Technology Stack

### Core Frameworks

- **Backend:** FastAPI
- **LLM Orchestration:** LangChain + DSPy
- **LLM Backend:** CampusAI (DTU's OpenAI-compatible LLM service)

### NLP & ML

- **Embeddings:** sentence-transformers (multilingual model)
- **Vector Search:** FAISS (Facebook AI Similarity Search)
- **Text Processing:** spaCy, scikit-learn

### Graph & Data

- **Knowledge Graph:** NetworkX
- **Data Format:**
  - `data/dtu_courses.jsonl` – DTU course catalog
  - `data/prerequisites_official.jsonl` – parsed official prereqs

### Deployment

- **Containerization:** Docker
- **API Docs:** OpenAPI/Swagger (FastAPI `/docs`)
- **Testing:** pytest

---

##  System Architecture

```
User Request (API / UI)
    ↓
FastAPI (main.py)
    ↓
┌─────────────────────────────────────────┐
│ Data Layer (indexer.py)                │
│ - Loads 1565 DTU courses               │
│ - FAISS vector store for semantic      │
│   similarity search                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Official Prereq Layer                  │
│ - prerequisites_official.jsonl         │
│   (parsed DTU prereq text)             │
│ - precompute_prereqs_official.py       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ NLP / LLM Layer                         │
│ - prerequisite_extractor.py (DSPy)      │
│ - course_matcher.py (LangChain)         │
│ - explainer.py (LangChain + CampusAI)   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Graph Layer (graph_builder.py)         │
│ - NetworkX directed graph               │
│ - 1565 nodes, 2397 edges                │
│ - Edges from official DTU prereqs       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Planning Layer                          │
│ - path_planner.py (Dijkstra)            │
│ - Uses completed_courses as constraints │
└─────────────────────────────────────────┘
    ↓
JSON Response  (+ LLM explanation)
```

---

##  Course Requirements Integration

CourseCompass is designed as a course project (e.g. for 02807 / 02456 / similar), and explicitly demonstrates:

### Natural Language Processing

- Semantic similarity search using sentence-transformer embeddings
- Prerequisite concept extraction from learning objectives (LLM + DSPy, offline)
- Text preprocessing and feature engineering

### Large Language Models

- CampusAI integration via OpenAI-compatible API
- LangChain for chains and prompt templating
- DSPy for structured extraction
- Natural-language explanation generation for study paths
- Prompt engineering and temperature control

### Knowledge Graphs

- Directed graph of DTU course dependencies
- Graph construction from official DTU prerequisite data
- Path finding algorithms (Dijkstra, BFS)
- Transitive closure for "all prerequisites of course X"

---

##  Quick Start

### Prerequisites

- Python 3.11+
- (Optional) Docker
- CampusAI API key with access to a model (e.g. gpt-oss / Qwen3)

### 1. Clone Repository

```bash
git clone <repository-url>
cd course-compass
```

### 2. Configure CampusAI

Create a `~/.env` file with your CampusAI API key:

```bash
echo "CAMPUSAI_API_KEY=your_actual_key_here" > ~/.env
# Optionally:
# echo "CAMPUSAI_API_BASE=https://chat.campusai.compute.dtu.dk/api/v1" >> ~/.env
# echo "CAMPUSAI_MODEL=gpt-oss" >> ~/.env
```

The code uses the environment variables in `config.py`:

- `CAMPUSAI_API_KEY`
- `CAMPUSAI_API_BASE` (default: CampusAI base URL)
- `CAMPUSAI_MODEL` (e.g., gpt-oss, Qwen3)

### 3. Install Python Dependencies

```bash
# Install in editable mode
pip install -e .

# With development dependencies (if defined)
pip install -e ".[dev]"
```

### 4. Prepare Data

Make sure you have:

- `data/dtu_courses.jsonl` – full DTU course catalog
- `data/prerequisites_official.jsonl` – generated via:

```bash
python precompute_prereqs_official.py \
  --input data/dtu_courses.jsonl \
  --output data/prerequisites_official.jsonl
```

This script parses official `prereq_text` and stores structured:

```json
{"course_code": "...", "title": "...", "prereq_text": "...", "prereq_course_codes": [...]}
```

### 5. Run the API

Development mode (with auto-reload):

```bash
uvicorn main:app --reload
```

or:

```bash
python main.py
```

- **Server:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

---

## 🐳 Docker Deployment

Build the image:

```bash
docker build -t course-compass .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e CAMPUSAI_API_KEY=your_key_here \
  -e CAMPUSAI_API_BASE=https://chat.campusai.compute.dtu.dk/api/v1 \
  -e CAMPUSAI_MODEL=gpt-oss \
  -v $(pwd)/data:/app/data \
  course-compass
```

---

##  API Endpoints

### 1. Health Check

```http
GET /v1/health
```

Example response:

```json
{
  "status": "healthy",
  "courses": 1565,
  "graph_nodes": 1565,
  "graph_edges": 2397
}
```

### 2. Search Courses

```http
GET /v1/search?query=machine%20learning&top_k=5
```

Example response:

```json
{
  "query": "machine learning",
  "results": [
    {
      "course_code": "02460",
      "title": "Advanced Machine Learning",
      "responsible": "Ole Winther",
      "ects": 5
    }
  ]
}
```

### 3. Analyze (Official) Prerequisites

```http
GET /v1/analyze-prerequisites/02460
```

Example response (shape):

```json
{
  "course_code": "02460",
  "title": "Advanced Machine Learning",
  "official_prereq_text": "02450. Basic knowledge of ...",
  "official_prereq_course_codes": [
    "02450"
  ]
}
```

### 4. Generate Study Path

```http
POST /v1/generate-path
Content-Type: application/json

{
  "target_course": "02460",
  "completed_courses": ["01005"]
}
```

Example response:

```json
{
  "target_course": "02460",
  "path": [
    {
      "course_code": "02450",
      "title": "Introduction to Machine Learning",
      "ects": 5
    },
    {
      "course_code": "02460",
      "title": "Advanced Machine Learning",
      "ects": 5
    }
  ],
  "explanation": "To reach 02460 Advanced Machine Learning, you should first take 02450 Introduction to Machine Learning, which covers optimization, basic neural networks, and probabilistic modelling. The official DTU prerequisites require ML background before 02460, and this path satisfies that requirement while keeping the total number of courses minimal. Make sure you also meet the general math and statistics prerequisites from the DTU course base.",
  "total_ects": 10
}
```

The explanation is generated by `explainer.py` + CampusAI, and is medium length and explicitly mentions that the official prerequisite list may include alternative options.

---

##  Testing

Run tests:

```bash
pytest -v
```

Coverage:

```bash
pytest --cov=. --cov-report=html
```

---

## 📈 Performance Characteristics

### Current Configuration

- **Courses indexed:** 1565
- **Graph size:** 1565 nodes, 2397 edges (from official prerequisites)
- **Average query time:**
  - Vector search: <50 ms
  - Path generation + explanation: typically <3 seconds (dominated by LLM call)
- **Embedding dimension:** 512 (multilingual)

### Scalability Notes

- Vector index easily scales to 10k+ courses (FAISS Flat is fine at this size).
- Graph building at runtime is now fast, because it consumes precomputed official prerequisites.
- The expensive part is offline precomputation:
  - Running `precompute_prereqs_official.py` once with LLMs (if used) and then reusing the JSONL.
- Possible optimizations:
  - Caching precomputed embeddings and prerequisite JSON.
  - Parallelizing any remaining LLM calls with rate limiting.
  - Incremental updates when DTU changes a course.

---

##  Project Structure

```
course-compass/
├── config.py                     # CampusAI & model configuration
├── indexer.py                    # Course loading & FAISS vector store
├── prerequisite_extractor.py     # DSPy-based concept extraction (offline)
├── precompute_prereqs_official.py# Build prerequisites_official.jsonl
├── course_matcher.py             # Semantic search for teaching courses
├── graph_builder.py              # NetworkX graph construction (from official prereqs)
├── path_planner.py               # Study path algorithms (Dijkstra)
├── explainer.py                  # LLM-based explanation generation (with official prereqs)
├── main.py                       # FastAPI application
├── test_main.py                  # Unit tests
├── Dockerfile                    # Container configuration
├── pyproject.toml                # Python project metadata
├── data/
│   ├── dtu_courses.jsonl         # Course catalog
│   └── prerequisites_official.jsonl # Official prereq structure
├── README.md                     # This file
└── TECHNICAL_DOCUMENTATION.md    # Detailed technical explanation
```

---

##  Example Use Cases

### Use Case 1: Check Prerequisites for an Advanced Course

**"What do I need before taking Advanced ML (02460)?"**

- CourseCompass looks up official DTU prerequisites for 02460.
- Shows course codes + free-text prereq description.
- Optionally suggests a minimal path from your existing courses.

### Use Case 2: Generate a Study Plan from Scratch

**"I haven't taken any courses yet; how do I reach 02451 Introduction to Machine Learning?"**

- Use `/v1/generate-path` with `completed_courses: []`.
- CourseCompass finds a path anchored in official prerequisites (e.g. math + stats + programming + 02451).
- LLM explanation tells you:
  - Why each step is there.
  - Which groups of official prerequisites you must satisfy.

### Use Case 3: Explore Related Courses

**"Find courses related to NLP"**

- Uses vector search over embeddings of course descriptions.
- Returns top-k similar courses (NLP, text mining, language technology, etc).

---

##  Known Limitations

- **Official prerequisites only:** Graph is based on DTU's explicit prerequisites; implicit skill gaps may still exist.
- **Static data:** Course catalog and official prereqs are loaded from JSONL; they must be regenerated when DTU updates the course base.
- **No semester planning:** The system doesn't yet consider when courses are offered (E1/E2/E3/E4).
- **Single-institution:** Currently tailored to DTU (course codes, structure, CampusAI).

---

## 🔮 Future Enhancements

### Short-term

- Simple Streamlit UI (chat-style study assistant).
- Display alternative prerequisite options clearly (OR-groups).
- Export study plans to PDF / calendar.

### Medium-term

- Multi-language support (full Danish + English).
- Personalized study paths based on previous education (BSc math, EE, CS, etc).
- Integration with DTU semester schedules.

### Long-term

- Integration with DTU registration systems.
- Collaborative filtering ("students who took X also took Y").
- Career path templates ("path to ML engineer / data scientist / control engineer").

---

##  Documentation

- **API Documentation:** http://localhost:8000/docs (when running)
- **Technical Deep Dive:** TECHNICAL_DOCUMENTATION.md
- **Project Context:** DTU course project (e.g., 02807 / 02456 / MSc AI track)

---

##  Project Info

This is an academic project at Technical University of Denmark (DTU).

- **Project:** CourseCompass – Intelligent Course Planning System
- **Student:** Kostis Tzimoulias (s242796)
- **Supervisor:** Finn Årup Nielsen

---

##  License

Academic project – DTU 2024/2025
