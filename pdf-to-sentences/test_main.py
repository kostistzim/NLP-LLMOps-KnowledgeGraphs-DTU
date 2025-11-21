"""
Tests for PDF to sentences API
"""

import os
from fastapi.testclient import TestClient
from main import app

# Set GROBID URL for testing
os.environ.setdefault("GROBID_URL", "http://localhost:8070")

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


def test_extract_sentences():
    """Test sentence extraction with 2303.15133.pdf"""
    pdf_path = "2303.15133.pdf"
    
    # Check if test file exists
    if not os.path.exists(pdf_path):
        print(f"Warning: Test file {pdf_path} not found. Skipping test.")
        return
    
    # Upload PDF
    with open(pdf_path, "rb") as f:
        files = {"pdf_file": ("2303.15133.pdf", f, "application/pdf")}
        response = client.post("/v1/extract-sentences", files=files)
    
    # Basic checks
    assert response.status_code == 200, response.text
    data = response.json()
    assert "sentences" in data
    assert isinstance(data["sentences"], list)
    
    # Check target sentence exists
    target_sentence = "How language should best be handled is not clear."
    assert target_sentence in data["sentences"], f"Target sentence not found in {len(data['sentences'])} sentences"
    
    print(f"✓ Test passed! Found {len(data['sentences'])} sentences")
    print(f"✓ Target sentence found: '{target_sentence}'")


def test_invalid_file():
    """Test with non-PDF file"""
    files = {"pdf_file": ("test.txt", b"not a pdf", "text/plain")}
    response = client.post("/v1/extract-sentences", files=files)
    assert response.status_code == 400


if __name__ == "__main__":
    print("Running tests...")
    test_root()
    print("✓ Root endpoint test passed")
    
    test_health()
    print("✓ Health endpoint test passed")
    
    test_invalid_file()
    print("✓ Invalid file test passed")
    
    test_extract_sentences()
    print("\n✓ All tests passed!")