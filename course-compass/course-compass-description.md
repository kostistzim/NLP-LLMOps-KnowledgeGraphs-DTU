# DTU Course Prerequisites Analyzer & Study Path Planner

## Title
**Intelligent Course Planning System with Prerequisite Analysis and Study Path Optimization**

## Overview
A web service that analyzes DTU course learning objectives to automatically extract prerequisite knowledge, constructs a dependency graph of courses, and generates optimal study paths for students. The system uses NLP to understand course requirements, knowledge graphs to model dependencies, and LLMs to provide natural language explanations and recommendations.

## Motivation
DTU students often struggle to determine which courses they should take before enrolling in advanced courses. The current course catalog provides limited prerequisite information, and students must manually analyze learning objectives to understand course dependencies. This system automates this process, providing intelligent study path recommendations.

## Course Elements Integration

### Natural Language Processing
- Extract prerequisite concepts from learning objectives using semantic analysis
- Topic modeling to identify course themes and relationships
- Text similarity for finding courses teaching specific concepts
- Named entity recognition for course codes and topics

### Large Language Models
- Generate natural language explanations for why prerequisites are needed
- Provide contextual course recommendations based on student goals
- Answer questions about course sequences and alternatives
- Suggest elective combinations based on specialization interests

### Knowledge Graphs
- Construct directed acyclic graph (DAG) of course dependencies
- Model relationships: "teaches", "requires", "related_to"
- Query prerequisite chains and course clusters
- Visualize course dependency networks

## System Architecture

### Components
1. **Data Ingestion Module**: Load and parse DTU course data (JSONL)
2. **NLP Analysis Engine**: Extract concepts and prerequisites from learning objectives
3. **Knowledge Graph Builder**: Construct course dependency graph using NetworkX
4. **LLM Integration Layer**: Generate explanations and recommendations via LangChain
5. **Path Finding Engine**: Compute optimal study paths using graph algorithms
6. **REST API**: FastAPI endpoints for querying system
7. **Web Interface**: Streamlit UI for interactive course planning

## Tech Stack
- **Backend**: FastAPI, Python 3.11
- **NLP**: spaCy, sentence-transformers, scikit-learn
- **LLM Frameworks**: 
  - LangChain (RAG, chains, agents, document processing)
  - DSPy (prompt optimization, declarative signatures)
- **LLM Backend**: CampusAI API (DTU's hosted LLM service)
- **Models**: Qwen3, DeepSeek-R1 (via CampusAI)
- **Knowledge Graph**: NetworkX, RDFLib
- **Vector Search**: FAISS (via LangChain)
...

## Data Sources

### Primary Dataset
- **dtu_courses.jsonl**: DTU course catalog with:
  - Course codes, titles, ECTS points
  - Learning objectives (list of strings)
  - Responsible teachers, departments
  - Academic year, language of instruction
  - Course content descriptions

### Derived Data
- **Prerequisite Graph**: Automatically constructed from learning objective analysis
- **Concept Ontology**: Topics and skills extracted from courses
- **Course Embeddings**: Semantic vectors for similarity search

## Methodology

### Phase 1: Prerequisite Extraction (NLP)
1. Parse learning objectives into structured text
2. Extract key concepts using keyword extraction (TF-IDF, KeyBERT)
3. Identify skill requirements (e.g., "understanding of linear algebra")
4. Match concepts to courses teaching them via semantic search

### Phase 2: Graph Construction (Knowledge Graph)
1. Create nodes for each course
2. Add edges for prerequisite relationships
3. Weight edges by prerequisite strength (required vs recommended)
4. Validate graph is acyclic (detect circular dependencies)

### Phase 3: Path Finding (Algorithms)
1. Implement Dijkstra's algorithm for shortest path
2. Support multiple optimization criteria:
   - Minimum number of courses
   - Minimize total ECTS
   - Consider course difficulty
3. Generate alternative paths when conflicts exist

### Phase 4: LLM Enhancement (Generative AI)
1. Chain 1: Extract prerequisites from target course
2. Chain 2: Find prerequisite courses
3. Chain 3: Generate study path explanation
4. Agent: Answer follow-up questions with context

## API Endpoints

### 1. Analyze Course Prerequisites
```
POST /v1/analyze-prerequisites
```

**Request:**
```json
{
  "course_code": "02460",
  "include_recommended": false
}
```

**Response:**
```json
{
  "course_code": "02460",
  "title": "Advanced Machine Learning",
  "prerequisites": [
    {
      "concept": "linear algebra",
      "required_courses": [
        {"code": "01005", "title": "Advanced Engineering Mathematics 1", "match_score": 0.92}
      ]
    },
    {
      "concept": "optimization theory",
      "required_courses": [
        {"code": "02450", "title": "Introduction to Machine Learning", "match_score": 0.88}
      ]
    }
  ]
}
```

### 2. Generate Study Path
```
POST /v1/generate-path
```

**Request:**
```json
{
  "target_course": "02460",
  "completed_courses": ["01005", "02402"],
  "max_courses": 5,
  "optimize_by": "shortest_path"
}
```

**Response:**
```json
{
  "target_course": "02460",
  "study_path": [
    {"semester": 1, "course": "02450", "title": "Introduction to Machine Learning", "ects": 5},
    {"semester": 2, "course": "02451", "title": "Probabilistic Machine Learning", "ects": 5},
    {"semester": 3, "course": "02460", "title": "Advanced Machine Learning", "ects": 5}
  ],
  "total_ects": 15,
  "estimated_semesters": 3,
  "explanation": "To take Advanced ML, you need foundational ML (02450) and probabilistic methods (02451)..."
}
```

### 3. Ask Question (RAG)
```
POST /v1/ask
```

**Request:**
```json
{
  "question": "What courses should I take to specialize in deep learning?",
  "context": {
    "completed_courses": ["02450"],
    "interests": ["computer vision", "NLP"]
  }
}
```

**Response:**
```json
{
  "answer": "For deep learning specialization with interests in CV and NLP, I recommend: 02456 (Deep Learning), 02460 (Advanced ML), 02462 (Signals and Data), and 02457 (Non-linear signal processing)...",
  "recommended_courses": [
    {"code": "02456", "title": "Deep Learning", "relevance": 0.95},
    {"code": "02460", "title": "Advanced Machine Learning", "relevance": 0.89}
  ],
  "study_sequence": ["02456", "02460", "02462"]
}
```

### 4. Search Courses by Topic
```
GET /v1/search?query=reinforcement%20learning&top_k=5
```

**Response:**
```json
{
  "query": "reinforcement learning",
  "results": [
    {"code": "02465", "title": "Introduction to RL and Control", "score": 0.94},
    {"code": "02460", "title": "Advanced Machine Learning", "score": 0.76}
  ]
}
```

### 5. Visualize Dependency Graph
```
GET /v1/graph/{course_code}?depth=2
```

**Response:**
Returns graph visualization data (nodes, edges) for frontend rendering.

### 6. Health Check
```
GET /v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "courses_indexed": 200,
  "graph_nodes": 200,
  "graph_edges": 450
}
```

## Example Use Cases

### Use Case 1: Check Prerequisites
**Input:** Student wants to take "02460 Advanced Machine Learning"

**System Actions:**
1. Analyzes learning objectives of 02460
2. Extracts concepts: "optimization", "neural networks", "probability theory"
3. Searches for courses teaching these concepts
4. Returns: 02450 (Intro ML), 02402 (Statistics), 01005 (Math)

**Output:** List of required prerequisite courses with explanations

### Use Case 2: Generate Study Plan
**Input:** Student completed [02402, 01005], wants to reach 02460

**System Actions:**
1. Builds dependency graph
2. Runs path-finding: 02402 → 02450 → 02460
3. LLM generates explanation of why each step is needed

**Output:** Semester-by-semester plan with 3 courses

### Use Case 3: Specialization Advice
**Input:** "I want to work in NLP, what courses should I take?"

**System Actions:**
1. Retrieves NLP-related courses via semantic search
2. Constructs optimal learning sequence
3. LLM explains career relevance of each course

**Output:** Recommended specialization track with justifications

## Testing Strategy

### Unit Tests
- `test_prerequisite_extraction.py`: Verify concept extraction accuracy
- `test_graph_construction.py`: Validate graph structure (no cycles, correct edges)
- `test_path_finding.py`: Test algorithm correctness with known paths
- `test_api_endpoints.py`: FastAPI endpoint validation

### Integration Tests
- `test_llm_integration.py`: Verify LangChain chains work end-to-end
- `test_vector_search.py`: Validate FAISS retrieval quality

### Example Test Cases
```python
def test_extract_prerequisites():
    course = load_course("02460")
    prereqs = extract_prerequisites(course)
    assert "linear algebra" in prereqs
    assert "optimization" in prereqs

def test_path_finding():
    path = find_study_path(
        start="02402",
        target="02460",
        graph=course_graph
    )
    assert len(path) >= 2
    assert path[-1] == "02460"
    assert is_valid_path(path, course_graph)

def test_api_analyze_endpoint():
    response = client.post("/v1/analyze-prerequisites", 
                          json={"course_code": "02460"})
    assert response.status_code == 200
    assert "prerequisites" in response.json()
```

## Deliverables

### 1. Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn langchain sentence-transformers networkx
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 2. Web Application
- Streamlit interface for course planning
- Interactive graph visualization
- Natural language query input

### 3. Documentation
- API documentation (Swagger/OpenAPI)
- README with setup instructions
- Architecture diagram
- Example queries and responses

### 4. Test Suite
- Minimum 80% code coverage
- CI/CD with GitHub Actions (optional)

## Timeline (4 Weeks)

### Week 1: Data & NLP
- Load and preprocess DTU course data
- Implement prerequisite extraction (NLP)
- Build concept matching system
- Unit tests for extraction logic

### Week 2: Knowledge Graph
- Construct course dependency graph (NetworkX)
- Implement path-finding algorithms
- Validate graph properties
- Graph visualization prototype

### Week 3: LLM Integration
- Integrate LangChain/DSPy
- Build chains for explanation generation
- Implement RAG for Q&A
- Vector search with FAISS

### Week 4: API & Polish
- Complete FastAPI endpoints
- Build Streamlit UI
- Docker containerization
- Testing, documentation, final polish

## Success Metrics

### Functional Requirements
- ✅ Correctly identifies 80%+ of obvious prerequisites
- ✅ Generates valid study paths (no circular dependencies)
- ✅ Answers 90%+ of course-related questions accurately
- ✅ API response time < 3 seconds

### Technical Requirements
- ✅ All endpoints return valid JSON
- ✅ Docker container builds and runs successfully
- ✅ Test coverage > 80%
- ✅ Code follows PEP 8 standards

## Extensions (If Time Permits)

### Advanced Features
- **Course difficulty estimation**: Predict workload based on learning objectives
- **Schedule optimization**: Consider semester availability, time conflicts
- **Personalized recommendations**: Based on student background/interests
- **Multi-language support**: Non-English courses
- **Export study plan**: PDF/calendar integration

### Additional Integrations
- **Wikidata integration**: Link courses to research topics
- **Publication analysis**: Find courses related to research papers
- **Career path mapping**: "Courses needed for ML engineer role"

## Risks & Mitigation

### Risk 1: Prerequisite Extraction Accuracy
**Mitigation:** Use multiple methods (keyword extraction + LLM + embedding similarity), validate against known prerequisites

### Risk 2: Graph Complexity
**Mitigation:** Start simple (binary edges), extend to weighted if time allows

### Risk 3: LLM Response Quality
**Mitigation:** Prompt engineering, fallback to template responses, include citations

## Conclusion

This project comprehensively addresses the course requirements by combining NLP (prerequisite extraction), LLMs (explanations and Q&A), and knowledge graphs (dependency modeling). The system provides genuine value to DTU students while demonstrating production-ready ML engineering skills.

The scope is ambitious but achievable in 4 weeks, with clear milestones and fallback options if advanced features prove too time-consuming. The result will be a deployable, well-tested web service that showcases skills in NLP, LLMs, knowledge graphs, backend development, and MLOps.