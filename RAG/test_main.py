"""
Tests for DTU Course RAG System
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_health():
    """Test health endpoint"""
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search():
    """Test search endpoint"""
    response = client.get("/v1/search?query=machine%20learning&top_k=3")
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "machine learning"
    assert len(data["results"]) <= 3
    assert data["mode"] == "dense"


def test_search_modes():
    """Test different retrieval modes"""
    for mode in ["sparse", "dense", "hybrid"]:
        response = client.get(f"/v1/search?query=statistics&mode={mode}")
        assert response.status_code == 200
        assert response.json()["mode"] == mode


def test_ask():
    """Test RAG endpoint"""
    response = client.get("/v1/ask?query=Are%20there%20courses%20about%20MRI")
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "retrieved_courses" in data
    assert len(data["retrieved_courses"]) > 0


def test_ask_teacher():
    """Test teacher-related question"""
    response = client.get("/v1/ask?query=How%20many%20ECTS%20is%20Tue%20Herlau%27s%20course")
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    # Should mention ECTS in answer
    assert "ECTS" in data["answer"] or "5" in data["answer"]


def test_empty_query():
    """Test empty query validation"""
    response = client.get("/v1/search?query=")
    assert response.status_code == 422


if __name__ == "__main__":
    print("Running tests...")
    print("Note: First test will be slow (building indices + DSPy init)\n")
    
    test_root()
    print("✓ Root endpoint")
    
    test_health()
    print("✓ Health endpoint")
    
    test_search()
    print("✓ Search endpoint")
    
    test_search_modes()
    print("✓ Search modes")
    
    test_ask()
    print("✓ Ask endpoint (RAG)")
    
    test_ask_teacher()
    print("✓ Ask teacher question")
    
    test_empty_query()
    print("✓ Empty query validation")
    
    print("\n✅ All tests passed!")