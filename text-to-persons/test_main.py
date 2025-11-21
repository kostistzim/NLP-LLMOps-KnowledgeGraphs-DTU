"""
Tests for person name extraction API
"""

import os
from fastapi.testclient import TestClient
from main import app

# Set fake API key for testing
os.environ.setdefault("CAMPUSAI_API_KEY", "test-key-12345")

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_extract_persons_format():
    """Test endpoint returns correct format"""
    response = client.post(
        "/v1/extract-persons",
        json={"text": "Einstein met Bohr."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "persons" in data
    assert isinstance(data["persons"], list)


def test_examples_from_prompt():
    """Test with assignment examples (requires real API key)"""
    examples = [
        "Ms Mette Frederiksen is in New York today.",
        "Einstein and von Neumann meet each other.",
    ]
    expected = [
        ["Mette Frederiksen"],
        ["Einstein", "von Neumann"],
    ]
    
    # Skip if no real API key
    if os.getenv("CAMPUSAI_API_KEY") == "test-key-12345":
        print("Skipping - requires real CAMPUSAI_API_KEY")
        return
    
    for text, exp in zip(examples, expected):
        response = client.post(
            "/v1/extract-persons",
            json={"text": text}
        )
        assert response.status_code == 200
        assert response.json()["persons"] == exp


if __name__ == "__main__":
    print("Running tests...")
    test_root()
    print("✓ Root endpoint")
    
    test_health()
    print("✓ Health endpoint")
    
    test_extract_persons_format()
    print("✓ Response format")
    
    test_examples_from_prompt()
    print("\n✓ All tests passed!")