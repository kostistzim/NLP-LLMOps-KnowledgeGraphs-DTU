"""
Tests for DTU Course Information Retrieval API
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
    data = response.json()
    assert data["status"] == "ok"
    assert "index_sizes" in data
    assert data["index_sizes"]["courses"] > 0
    assert data["index_sizes"]["objectives"] > 0


def test_similar_courses():
    """Test similar courses endpoint"""
    response = client.get("/v1/courses/02402/similar?top_k=5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["query_course_id"] == "02402"
    assert len(data["results"]) == 5
    assert data["mode"] == "dense"
    
    # Check result structure
    result = data["results"][0]
    assert "course_id" in result
    assert "title" in result
    assert "score" in result


def test_similar_courses_modes():
    """Test different retrieval modes"""
    for mode in ["sparse", "dense", "hybrid"]:
        response = client.get(f"/v1/courses/02402/similar?mode={mode}&top_k=3")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == mode
        assert len(data["results"]) == 3


def test_similar_courses_not_found():
    """Test with non-existent course"""
    response = client.get("/v1/courses/99999/similar")
    assert response.status_code == 404


def test_search_courses():
    """Test course search endpoint"""
    response = client.get("/v1/search?query=machine%20learning&top_k=5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "machine learning"
    assert len(data["results"]) <= 5
    assert data["mode"] == "dense"
    
    # Results should be sorted by score
    scores = [r["score"] for r in data["results"]]
    assert scores == sorted(scores, reverse=True)


def test_search_courses_modes():
    """Test course search with different modes"""
    for mode in ["sparse", "dense", "hybrid"]:
        response = client.get(f"/v1/search?query=statistics&mode={mode}")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == mode


def test_search_objectives():
    """Test objective search endpoint"""
    response = client.get("/v1/objectives/search?query=dimensionality%20reduction&top_k=5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "dimensionality reduction"
    assert len(data["results"]) <= 5
    
    # Check result structure
    if len(data["results"]) > 0:
        result = data["results"][0]
        assert "course_id" in result
        assert "title" in result
        assert "objective" in result
        assert "score" in result


def test_search_empty_query():
    """Test search with empty query"""
    response = client.get("/v1/search?query=")
    assert response.status_code == 422  # Validation error


def test_hybrid_alpha():
    """Test hybrid mode with different alpha values"""
    for alpha in [0.0, 0.5, 1.0]:
        response = client.get(f"/v1/search?query=statistics&mode=hybrid&alpha={alpha}")
        assert response.status_code == 200


def test_top_k_limits():
    """Test top_k parameter limits"""
    # Valid range
    response = client.get("/v1/search?query=statistics&top_k=10")
    assert response.status_code == 200
    
    # Too large (should be capped or rejected)
    response = client.get("/v1/search?query=statistics&top_k=100")
    assert response.status_code == 422


if __name__ == "__main__":
    print("Running tests...\n")
    print("Note: First test will be slow (building indices)")
    
    test_root()
    print("✓ Root endpoint")
    
    test_health()
    print("✓ Health endpoint")
    
    test_similar_courses()
    print("✓ Similar courses")
    
    test_similar_courses_modes()
    print("✓ Similar courses - all modes")
    
    test_similar_courses_not_found()
    print("✓ Similar courses - not found")
    
    test_search_courses()
    print("✓ Search courses")
    
    test_search_courses_modes()
    print("✓ Search courses - all modes")
    
    test_search_objectives()
    print("✓ Search objectives")
    
    test_search_empty_query()
    print("✓ Empty query validation")
    
    test_hybrid_alpha()
    print("✓ Hybrid alpha parameter")
    
    test_top_k_limits()
    print("✓ Top-k limits")
    
    print("\n✅ All tests passed!")