# NLP, LLMOps & Knowledge Graphs - DTU Course Projects

**Course:** LLMoperations-NLP-Knowledge Graphs  
**Institution:** Technical University of Denmark (DTU)  
**Student:** Kostis Tzimoulias  
**Semester:** Fall 2024

---

##  Course Overview

This repository contains all projects completed for the DTU course on Natural Language Processing, Large Language Model Operations, and Knowledge Graphs. Each project demonstrates progressive mastery of modern NLP techniques, LLM integration, and production ML engineering practices.

**Technologies:** Python, FastAPI, LangChain, DSPy, Docker, FAISS, NetworkX, sentence-transformers, CampusAI (DTU's LLM infrastructure)

---

##  Projects

### **Project 1: Sentiment Analysis API** 

**Objective:** Build a RESTful API for sentiment analysis of course evaluation comments in Danish and English.

**Key Features:**
- FastAPI backend with async support
- Multi-language sentiment classification (Danish/English)
- Dictionary-based and ML-based approaches
- Docker containerization

**Technologies:** FastAPI, scikit-learn, NLTK, Docker

**Highlights:**
- Preprocessed and analyzed DTU course evaluation data
- Compared rule-based vs ML classifiers
- Deployed as containerized microservice

**Directory:** `project-1-sentiment-analysis/`

---

### **Project 2: PDF Document Processing with GROBID** 

**Objective:** Extract structured information from academic PDFs using GROBID (GeneRation Of BIbliographic Data).

**Key Features:**
- PDF to XML conversion
- Metadata extraction (authors, abstract, references)
- Section parsing and content extraction
- GROBID API integration

**Technologies:** GROBID, Python, XML parsing, Docker

**Highlights:**
- Processed research papers to structured format
- Extracted bibliographic metadata
- Built pipeline for academic document analysis

**Directory:** `project-2-pdf-processing/`

---

### **Project 3: Named Entity Recognition & Information Extraction** 

**Objective:** Extract and classify named entities from text documents.

**Key Features:**
- NER using spaCy and Hugging Face transformers
- Custom entity recognition for domain-specific terms
- Entity linking and relation extraction
- Visualization of entity networks

**Technologies:** spaCy, transformers, networkx

**Highlights:**
- Implemented multi-model NER pipeline
- Fine-tuned models for course-specific entities
- Built knowledge graph from extracted entities

**Directory:** `project-3-ner-extraction/`

---

### **Project 4: Information Retrieval System** 🔍

**Objective:** Build a semantic search engine for document retrieval using vector embeddings.

**Key Features:**
- Document indexing with sentence-transformers
- FAISS vector store for efficient similarity search
- BM25 + dense retrieval hybrid approach
- Query expansion and re-ranking

**Technologies:** sentence-transformers, FAISS, BM25, scikit-learn

**Highlights:**
- Indexed 1000+ documents for semantic search
- Implemented hybrid retrieval (keyword + semantic)
- Evaluated with NDCG and MAP metrics

**Directory:** `project-4-information-retrieval/`

---

### **Project 5: Retrieval-Augmented Generation (RAG) System** 🤖

**Objective:** Build a question-answering system that retrieves relevant documents and generates answers using LLMs.

**Key Features:**
- Document retrieval with semantic search
- LLM-based answer generation (via CampusAI)
- Context-aware responses with citations
- Evaluation of answer quality

**Technologies:** LangChain, sentence-transformers, FAISS, CampusAI

**Highlights:**
- Integrated retrieval with generation pipeline
- Implemented source attribution for answers
- Compared different LLM prompting strategies

**Directory:** `project-5-rag-system/`

---

### **Project 6: Advanced RAG with Query Optimization** 

**Objective:** Enhance RAG system with query rewriting, multi-hop reasoning, and answer synthesis.

**Key Features:**
- Query decomposition for complex questions
- Multi-document reasoning
- Self-critique and answer refinement
- DSPy for prompt optimization

**Technologies:** LangChain, DSPy, CampusAI, FAISS

**Highlights:**
- Implemented chain-of-thought reasoning
- Built self-correcting answer generation
- Optimized prompts using DSPy signatures

**Directory:** `project-6-advanced-rag/`

---

### **Project 7: CourseCompass - Intelligent Course Planning** 🧭

**Final Project**

**Objective:** Automatically analyze DTU course learning objectives to extract prerequisites, build a knowledge graph of course dependencies, and generate optimal study paths using NLP, LLMs, and graph algorithms.

**Key Features:**
- **Prerequisite Extraction:** DSPy-based concept extraction from course descriptions
- **Semantic Course Matching:** FAISS vector search to find courses teaching specific concepts
- **Knowledge Graph:** NetworkX directed acyclic graph of course dependencies
- **Path Planning:** Dijkstra's algorithm for optimal study paths
- **Natural Language Explanations:** LLM-generated reasoning for recommendations
- **REST API:** FastAPI endpoints for querying and planning
- **Production Ready:** Docker containerization, unit tests, comprehensive documentation

**Technologies:** 
- **Frameworks:** FastAPI, LangChain, DSPy
- **NLP:** sentence-transformers, FAISS
- **Graph:** NetworkX
- **LLM:** CampusAI (Qwen3)
- **Deployment:** Docker, pytest

**System Architecture:**
```
User Query
    ↓
FastAPI Backend
    ↓
┌─────────────────────────────────────┐
│ Data Layer                          │
│ - 1565 DTU courses                  │
│ - FAISS semantic search             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ NLP Layer                           │
│ - Prerequisite extraction (DSPy)   │
│ - Course matching (LangChain)      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Knowledge Graph                     │
│ - Course dependencies (NetworkX)   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Planning & Explanation              │
│ - Path finding (Dijkstra)          │
│ - LLM explanations                  │
└─────────────────────────────────────┘
    ↓
JSON Response
```

**API Endpoints:**
- `GET /v1/health` - System health check
- `GET /v1/search` - Semantic course search
- `GET /v1/analyze-prerequisites/:id` - Get course prerequisites
- `POST /v1/generate-path` - Generate study path

**Performance:**
- Indexes 1565 courses
- <3 second query response time
- 512-dimensional embeddings
- Handles complex multi-hop prerequisite chains

**Documentation:**
- `README.md` - User guide and API documentation
- `TECHNICAL_DOCUMENTATION.md` - In-depth technical analysis
- `project-description.md` - Academic project proposal

**Highlights:**
- Solves real problem: DTU students struggle to identify course prerequisites
- Automatically discovers hidden dependencies from learning objectives
- Combines classical algorithms (graph theory) with modern NLP (transformers, LLMs)
- Production-ready with Docker, tests, and comprehensive documentation
- Demonstrates full MLOps pipeline from data ingestion to API deployment

**Directory:** `course-compass/`

---

## 🛠️ Technical Skills Demonstrated

### Natural Language Processing
- Text preprocessing and tokenization
- Named Entity Recognition (NER)
- Sentiment analysis
- Semantic similarity and embeddings
- Information extraction
- Document retrieval (BM25, dense vectors)

### Large Language Models
- Prompt engineering and optimization
- Chain-of-thought reasoning
- Retrieval-Augmented Generation (RAG)
- Multi-hop reasoning
- LangChain orchestration
- DSPy declarative prompting

### Knowledge Graphs
- Graph construction from text
- Directed acyclic graphs (DAGs)
- Path finding algorithms
- Network analysis
- Relationship extraction

### MLOps & Production
- FastAPI REST APIs
- Docker containerization
- Unit testing with pytest
- Vector databases (FAISS)
- Async programming
- API documentation (OpenAPI/Swagger)

---

##  Repository Structure
```
NLP-LLMOps-KnowledgeGraphs-DTU/
├── README.md                           # This file
├── llm-operations.yml                  # Conda environment
│
├── project-1-sentiment-analysis/
│   ├── main.py
│   ├── Dockerfile
│   └── README.md
│
├── project-2-pdf-processing/
│   ├── main.py
│   ├── Dockerfile
│   └── README.md
│
├── project-3-ner-extraction/
│   ├── main.py
│   ├── Dockerfile
│   └── README.md
│
├── project-4-information-retrieval/
│   ├── indexer.py
│   ├── retriever.py
│   ├── main.py
│   ├── Dockerfile
│   └── README.md
│
├── project-5-rag-system/
│   ├── rag.py
│   ├── main.py
│   ├── Dockerfile
│   └── README.md
│
├── project-6-advanced-rag/
│   ├── advanced_rag.py
│   ├── main.py
│   ├── Dockerfile
│   └── README.md
│
└── course-compass/                     # Final Project ⭐
    ├── config.py
    ├── indexer.py
    ├── prerequisite_extractor.py
    ├── course_matcher.py
    ├── graph_builder.py
    ├── path_planner.py
    ├── explainer.py
    ├── main.py
    ├── test_main.py
    ├── pyproject.toml
    ├── Dockerfile
    ├── README.md
    ├── TECHNICAL_DOCUMENTATION.md
    ├── project-description.md
    └── data/
        └── dtu_courses.jsonl
```

---

##  Getting Started

### Prerequisites
- Python 3.11+
- Conda (recommended) or pip
- Docker (for containerized deployment)
- CampusAI API key (for LLM access)

### Environment Setup

**Option 1: Conda (Recommended)**
```bash
# Create environment from yml
conda env create -f llm-operations.yml
conda activate llm-operations
```

**Option 2: Individual Projects**
```bash
# Each project has its own setup
cd project-X/
pip install -r requirements.txt
# or
pip install -e .  # if using pyproject.toml
```

### Configuration

**Create ~/.env file:**
```bash
echo "CAMPUSAI_API_KEY=your_api_key_here" > ~/.env
```

### Running Projects

**Locally:**
```bash
cd project-X/
python main.py
```

**Docker:**
```bash
cd project-X/
docker build -t project-x .
docker run -p 8000:8000 -e CAMPUSAI_API_KEY=$CAMPUSAI_API_KEY project-x
```

---

##  Project Progression

**Complexity Trajectory:**
```
Project 1: Basic API + ML
    ↓
Project 2: Document Processing
    ↓
Project 3: NLP Techniques
    ↓
Project 4: Vector Search
    ↓
Project 5: RAG Systems
    ↓
Project 6: Advanced RAG
    ↓
Project 7: Full Production System
    (NLP + LLM + KG + Algorithms)
```

---

##  Learning Outcomes

By completing these projects, I have gained hands-on experience with:

1. **Modern NLP Stack:** From traditional NLP (spaCy) to transformers (sentence-transformers) to LLMs (CampusAI)
2. **Production ML:** FastAPI, Docker, testing, documentation, deployment
3. **Vector Databases:** FAISS for efficient similarity search at scale
4. **LLM Integration:** LangChain for orchestration, DSPy for optimization
5. **Knowledge Graphs:** NetworkX for relationship modeling and graph algorithms
6. **System Design:** Building complex, multi-component ML systems
7. **MLOps:** End-to-end pipeline from data to deployment

---

##  Documentation

Each project contains:
- **README.md** - Setup, usage, and examples
- **Code comments** - Inline documentation
- **API docs** - Swagger/OpenAPI (for FastAPI projects)

**CourseCompass (Project 7)** additionally includes:
- **TECHNICAL_DOCUMENTATION.md** - Deep dive for academic review
- **project-description.md** - Formal project proposal

---

##  Testing

Projects include unit tests where applicable:
```bash
# Run tests
cd project-X/
pytest test_*.py -v

# With coverage
pytest --cov=. --cov-report=html
```

---

##  Docker Support

All projects are containerized for reproducible deployment:
```bash
# Build
docker build -t project-name .

# Run
docker run -p 8000:8000 \
  -e CAMPUSAI_API_KEY=$CAMPUSAI_API_KEY \
  project-name

# Access API docs
open http://localhost:8000/docs
```

---







