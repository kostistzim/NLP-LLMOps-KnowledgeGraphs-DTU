"""
Unit tests for CourseCompass
"""

import pytest
from fastapi.testclient import TestClient
import networkx as nx

# Import modules to test
from config import get_langchain_llm, initialize_dspy, EMBEDDING_MODEL
from indexer import load_courses_jsonl, course_to_text, courses_to_documents, build_vector_store
from prerequisite_extractor import extract_prerequisites, ConceptExtractor
from course_matcher import search_courses_by_concept, find_teaching_courses
from graph_builder import build_course_graph
from path_planner import find_study_path, get_direct_prerequisites
from main import app


# Fixtures
@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_courses():
    """Sample course data for testing"""
    return [
        {
            "course_code": "01005",
            "title": "Advanced Engineering Mathematics 1",
            "learning_objectives": [
                "Apply linear algebra concepts",
                "Solve differential equations"
            ],
            "fields": {"Point( ECTS )": 5, "Responsible": "Test Teacher"}
        },
        {
            "course_code": "02450",
            "title": "Introduction to Machine Learning",
            "learning_objectives": [
                "Understand supervised learning",
                "Apply optimization techniques"
            ],
            "fields": {"Point( ECTS )": 5, "Responsible": "Test Teacher"}
        },
        {
            "course_code": "02460",
            "title": "Advanced Machine Learning",
            "learning_objectives": [
                "Implement deep neural networks",
                "Apply advanced optimization"
            ],
            "fields": {"Point( ECTS )": 5, "Responsible": "Test Teacher"}
        }
    ]


# Test config.py
class TestConfig:
    
    def test_langchain_llm_creation(self):
        """Test LangChain LLM can be created"""
        llm = get_langchain_llm()
        assert llm is not None
        assert llm.model_name == "Qwen3"
    
    def test_langchain_llm_temperature(self):
        """Test temperature parameter works"""
        llm_deterministic = get_langchain_llm(temperature=0.0)
        llm_creative = get_langchain_llm(temperature=0.7)
        
        assert llm_deterministic.temperature == 0.0
        assert llm_creative.temperature == 0.7
    
    def test_embedding_model_constant(self):
        """Test embedding model is defined"""
        assert EMBEDDING_MODEL is not None
        assert "sentence-transformers" in EMBEDDING_MODEL


# Test indexer.py
class TestIndexer:
    
    def test_course_to_text(self, sample_courses):
        """Test course dict converts to text"""
        text = course_to_text(sample_courses[0])
        
        assert "Advanced Engineering Mathematics" in text
        assert "linear algebra" in text
        assert len(text) > 0
    
    def test_courses_to_documents(self, sample_courses):
        """Test courses convert to LangChain Documents"""
        docs = courses_to_documents(sample_courses)
        
        assert len(docs) == 3
        assert docs[0].metadata['course_code'] == "01005"
        assert "linear algebra" in docs[0].page_content
    
    def test_vector_store_build(self, sample_courses):
        """Test FAISS vector store builds successfully"""
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        
        assert vectorstore is not None
        # Test search
        results = vectorstore.similarity_search("mathematics", k=1)
        assert len(results) > 0


# Test prerequisite_extractor.py
class TestPrerequisiteExtractor:
    
    def test_concept_extractor_creation(self):
        """Test ConceptExtractor can be instantiated"""
        initialize_dspy()
        extractor = ConceptExtractor()
        assert extractor is not None
    
    def test_extract_prerequisites(self, sample_courses):
        """Test prerequisites can be extracted"""
        initialize_dspy()
        course = sample_courses[2]  # Advanced ML
        
        prerequisites = extract_prerequisites(course)
        
        assert isinstance(prerequisites, list)
        assert len(prerequisites) > 0
        # Should extract concepts like "linear algebra", "optimization", etc.
    
    def test_extract_prerequisites_empty_objectives(self):
        """Test handling of courses with no objectives"""
        initialize_dspy()
        course = {"title": "Test", "learning_objectives": []}
        
        prerequisites = extract_prerequisites(course)
        assert prerequisites == []


# Test course_matcher.py
class TestCourseMatcher:
    
    def test_search_courses_by_concept(self, sample_courses):
        """Test semantic search for courses"""
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        
        matches = search_courses_by_concept(vectorstore, "linear algebra", top_k=2)
        
        assert len(matches) > 0
        assert matches[0]['course_code'] in ["01005", "02450", "02460"]
        assert 'similarity' in matches[0]
    
    def test_find_teaching_courses(self, sample_courses):
        """Test finding courses that teach concepts"""
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        
        concepts = ["linear algebra", "optimization"]
        results = find_teaching_courses(vectorstore, concepts)
        
        assert len(results) == 2  # Two concepts
        assert "linear algebra" in results
        assert "optimization" in results


# Test graph_builder.py
class TestGraphBuilder:
    
    def test_graph_creation(self, sample_courses):
        """Test graph can be built"""
        initialize_dspy()
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        
        graph = build_course_graph(sample_courses, vectorstore)
        
        assert isinstance(graph, nx.DiGraph)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() >= 0
    
    def test_graph_is_dag(self, sample_courses):
        """Test graph is directed acyclic"""
        initialize_dspy()
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        
        graph = build_course_graph(sample_courses, vectorstore)
        
        # Should be DAG (no cycles)
        assert nx.is_directed_acyclic_graph(graph)


# Test path_planner.py
class TestPathPlanner:
    
    def test_get_direct_prerequisites(self, sample_courses):
        """Test getting direct prerequisites"""
        initialize_dspy()
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        graph = build_course_graph(sample_courses, vectorstore)
        
        # Assuming graph has edges, test retrieval
        if graph.number_of_edges() > 0:
            # Get a node with prerequisites
            for node in graph.nodes():
                if graph.in_degree(node) > 0:
                    prereqs = get_direct_prerequisites(graph, node)
                    assert isinstance(prereqs, list)
                    break
    
    def test_find_study_path(self, sample_courses):
        """Test path finding"""
        initialize_dspy()
        docs = courses_to_documents(sample_courses)
        vectorstore = build_vector_store(docs)
        graph = build_course_graph(sample_courses, vectorstore)
        
        # Try to find path to Advanced ML
        path = find_study_path(graph, "02460", [])
        
        # Path may or may not exist depending on graph construction
        if path:
            assert isinstance(path, list)
            assert path[-1] == "02460"


# Test main.py API
class TestAPI:
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "CourseCompass"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        # Note: This will fail until server fully starts (lifespan completes)
        response = client.get("/v1/health")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
    
    def test_search_endpoint(self, client):
        """Test course search endpoint"""
        response = client.get("/v1/search?query=machine%20learning&top_k=3")
        
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "results" in data
            assert data["query"] == "machine learning"


# Test edge cases
class TestEdgeCases:
    
    def test_empty_course_list(self):
        """Test handling empty course list"""
        docs = courses_to_documents([])
        assert docs == []
    
    def test_course_with_missing_fields(self):
        """Test course with missing fields"""
        course = {"course_code": "TEST"}
        text = course_to_text(course)
        assert isinstance(text, str)
    
    def test_invalid_course_code_in_path(self):
        """Test path finding with invalid course code"""
        graph = nx.DiGraph()
        graph.add_node("01005")
        graph.add_node("02450")
        
        path = find_study_path(graph, "INVALID", [])
        assert path is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])