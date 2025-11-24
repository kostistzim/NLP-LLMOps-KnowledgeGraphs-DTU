# CourseCompass 

**Intelligent Course Planning System for DTU Students**

CourseCompass automatically analyzes course learning objectives to extract prerequisite knowledge, builds a dependency graph of courses, and generates optimal study paths using NLP, LLMs, and knowledge graphs.

---

##  Project Overview

### Problem
DTU students struggle to determine which courses they should take before enrolling in advanced courses. The course catalog provides limited explicit prerequisite information, requiring students to manually analyze learning objectives to understand course dependencies.

### Solution
CourseCompass automates this process by:
1. **Extracting** prerequisite concepts from course learning objectives using LLMs
2. **Matching** concepts to courses that teach them using semantic search
3. **Building** a knowledge graph of course dependencies
4. **Finding** optimal study paths using graph algorithms
5. **Explaining** recommendations in natural language

---

##  System Architecture
```
User Request
    ↓
FastAPI (main.py)
    ↓
┌─────────────────────────────────────────┐
│ Data Layer (indexer.py)                 │
│ - Loads 1565 DTU courses                │
│ - FAISS vector store for semantic search│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ NLP Layer                               │
│ - prerequisite_extractor.py (DSPy)     │
│ - course_matcher.py (LangChain)        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Graph Layer (graph_builder.py)         │
│ - NetworkX directed graph               │
│ - Course dependency edges               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Planning Layer                          │
│ - path_planner.py (Dijkstra algorithm) │
│ - explainer.py (LangChain)             │
└─────────────────────────────────────────┘
    ↓
JSON Response
```

---

##  Technology Stack

### Core Frameworks
- **Backend**: FastAPI 0.115.5
- **LLM Orchestration**: LangChain 0.3.17 + DSPy 2.5.44
- **LLM Backend**: CampusAI (DTU's hosted LLM service)

### NLP & ML
- **Embeddings**: sentence-transformers (multilingual model)
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Text Processing**: spaCy, scikit-learn

### Graph & Data
- **Knowledge Graph**: NetworkX 3.4.2
- **Data Format**: JSONL (1565 DTU courses)

### Deployment
- **Containerization**: Docker
- **Testing**: pytest
- **API Documentation**: OpenAPI/Swagger

---

## 📋 Course Requirements Integration

### Natural Language Processing
- ✅ Semantic similarity search using sentence-transformers embeddings
- ✅ Prerequisite concept extraction from learning objectives
- ✅ Text preprocessing and feature engineering

### Large Language Models
- ✅ CampusAI integration via LangChain and DSPy
- ✅ Chain-of-thought reasoning for prerequisite extraction
- ✅ Natural language explanation generation
- ✅ Prompt engineering and optimization

### Knowledge Graphs
- ✅ Directed acyclic graph (DAG) of course dependencies
- ✅ Graph construction from extracted relationships
- ✅ Path finding algorithms (Dijkstra, BFS)
- ✅ Transitive closure for prerequisite chains

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- CampusAI API key

### Installation

**1. Clone repository**
```bash
git clone <repository-url>
cd course-compass
```

**2. Set up environment**
```bash
# Create .env file in home directory
echo "CAMPUSAI_API_KEY=your_key_here" > ~/.env
```

***3. Install project dependencies**
```bash
# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

**4. Run application**
```bash
python main.py
```

Server starts at: **http://localhost:8000**

API documentation: **http://localhost:8000/docs**

---

## 🐳 Docker Deployment

**Build image**
```bash
docker build -t course-compass .
```

**Run container**
```bash
docker run -p 8000:8000 \
  -e CAMPUSAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  course-compass
```

---

##  API Endpoints

### Health Check
```bash
GET /v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "courses": 1565,
  "graph_nodes": 50,
  "graph_edges": 127
}
```

---

### Search Courses
```bash
GET /v1/search?query=machine%20learning&top_k=5
```

**Response:**
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

---

### Analyze Prerequisites
```bash
GET /v1/analyze-prerequisites/02460
```

**Response:**
```json
{
  "course_code": "02460",
  "title": "Advanced Machine Learning",
  "prerequisites": [
    {
      "course_code": "02450",
      "title": "Introduction to Machine Learning",
      "weight": 0.87
    }
  ]
}
```

---

### Generate Study Path
```bash
POST /v1/generate-path
Content-Type: application/json

{
  "target_course": "02460",
  "completed_courses": ["01005"]
}
```

**Response:**
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
  "explanation": "To reach Advanced Machine Learning, you should first take Introduction to Machine Learning. This foundational course covers optimization techniques and basic neural networks, which are essential prerequisites for the advanced methods. The complete path requires 10 ECTS over approximately 2 semesters.",
  "total_ects": 10
}
```

---

##  Testing

**Run unit tests**
```bash
pytest test_main.py -v
```

**Test coverage**
```bash
pytest --cov=. --cov-report=html
```

---

##  Performance Characteristics

### Current Configuration
- **Courses indexed**: 1565 (full DTU catalog)
- **Graph size**: 50 courses (configurable subset for testing)
- **Average query time**: <3 seconds
- **Embedding dimension**: 512 (multilingual model)

### Scalability Notes
Building the complete dependency graph for all 1565 courses requires ~17 hours due to LLM API calls (40 seconds per course). The system is configured to use a representative subset of 50 courses for demonstration purposes, which completes in ~30 minutes.

**Production optimization strategies:**
- Caching extracted prerequisites
- Parallel API requests with rate limiting
- Incremental graph updates
- Pre-computed embeddings

---

##  Project Structure
```
course-compass/
├── config.py                    # CampusAI & model configuration
├── indexer.py                   # Course loading & FAISS vector store
├── prerequisite_extractor.py    # DSPy-based concept extraction
├── course_matcher.py            # Semantic search for teaching courses
├── graph_builder.py             # NetworkX graph construction
├── path_planner.py              # Study path algorithms
├── explainer.py                 # LLM-based explanation generation
├── main.py                      # FastAPI application
├── test_main.py                 # Unit tests
├── Dockerfile                   # Container configuration
├── requirements.txt             # Python dependencies
├── data/
│   └── dtu_courses.jsonl       # Course catalog
├── README.md                    # This file
└── TECHNICAL_DOCUMENTATION.md  # Detailed technical explanation
```

---

##  Example Use Cases

### Use Case 1: Check Prerequisites
**Student Question:** "What do I need before taking Advanced ML?"

**System Action:**
1. Analyzes learning objectives of 02460
2. Extracts concepts: "optimization", "neural networks", "probability"
3. Searches for courses teaching these concepts
4. Returns: 02450 (Intro ML), 02402 (Statistics), 01005 (Math)

---

### Use Case 2: Generate Study Plan
**Student Input:** Completed [01005, 02402], want to reach 02460

**System Action:**
1. Builds dependency graph
2. Runs path-finding: 01005 → 02450 → 02460
3. Generates explanation of why each step is needed

**Output:** Semester-by-semester plan with 2-3 courses

---

### Use Case 3: Explore Related Courses
**Student Query:** "Find courses related to NLP"

**System Action:**
1. Semantic search in vector store
2. Returns top-k similar courses
3. Ranks by relevance

---

##  Known Limitations

1. **Graph Subset**: Uses 50 courses (not full catalog) due to API rate limits
2. **Implicit Prerequisites Only**: Relies on learning objectives analysis
3. **Single Language**: Optimized for English/Danish course descriptions
4. **No Semester Planning**: Doesn't account for course availability by semester
5. **Static Data**: Course catalog must be manually updated

---

## 🔮 Future Enhancements

### Short-term
- [ ] Streamlit UI for interactive planning
- [ ] Export study plans to PDF/calendar
- [ ] Course difficulty estimation
- [ ] Alternative path suggestions

### Long-term
- [ ] Multi-language support (full Danish integration)
- [ ] Personalized recommendations based on student background
- [ ] Integration with DTU course registration system
- [ ] Real-time course availability checking
- [ ] Collaborative filtering ("Students who took X also took Y")

---

## Documentation

- **API Documentation**: http://localhost:8000/docs (when running)
- **Technical Deep Dive**: See `TECHNICAL_DOCUMENTATION.md`
- **Course Project Description**: See `project-description.md`

---

## Contributing

This is an academic project for DTU course 02807 Computational Tools for Data Science.

**Project Team:** Kostis Tzimoulias(s242796)  
**Supervisor:** Finn Årup Nielsen
**Institution:** Technical University of Denmark (DTU)

---

## License

Academic project - DTU 2024/2025

---

