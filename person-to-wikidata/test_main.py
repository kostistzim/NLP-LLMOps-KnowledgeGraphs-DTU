"""
Tests for Person to Wikidata API
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
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_birthday_niels_bohr():
    """Test birthday endpoint with Niels Bohr"""
    response = client.post(
        "/v1/birthday",
        json={"person": "Niels Bohr"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["person"] == "Niels Bohr"
    assert data["qid"] == "Q7085"
    assert data["birthday"] == "1885-10-07"


def test_birthday_mette_frederiksen():
    """Test birthday endpoint with Mette Frederiksen"""
    response = client.post(
        "/v1/birthday",
        json={"person": "Mette Frederiksen"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["qid"] == "Q5015"
    assert data["birthday"] == "1977-11-19"


def test_students_niels_bohr():
    """Test students endpoint with Niels Bohr"""
    response = client.post(
        "/v1/students",
        json={"person": "Niels Bohr"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["qid"] == "Q7085"
    assert "students" in data
    assert len(data["students"]) > 0
    
    # Check structure
    student = data["students"][0]
    assert "label" in student
    assert "qid" in student


def test_all_endpoint():
    """Test all endpoint"""
    response = client.post(
        "/v1/all",
        json={"person": "Niels Bohr"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["qid"] == "Q7085"
    assert data["birthday"] == "1885-10-07"
    assert "students" in data
    assert len(data["students"]) > 0


def test_political_party():
    """Test political party endpoint"""
    response = client.post(
        "/v1/political-party",
        json={"person": "Mette Frederiksen"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["qid"] == "Q5015"
    assert data["political_party"] is not None


def test_person_not_found():
    """Test with non-existent person"""
    response = client.post(
        "/v1/birthday",
        json={"person": "Completely Fake Person XYZ123"}
    )
    
    assert response.status_code == 404


def test_with_context():
    """Test that context field is accepted"""
    response = client.post(
        "/v1/birthday",
        json={
            "person": "Niels Bohr",
            "context": "When was Niels Bohr born?"
        }
    )
    
    assert response.status_code == 200


if __name__ == "__main__":
    print("Running tests...\n")
    
    test_root()
    print("✓ Root endpoint")
    
    test_health()
    print("✓ Health endpoint")
    
    test_birthday_niels_bohr()
    print("✓ Birthday: Niels Bohr")
    
    test_birthday_mette_frederiksen()
    print("✓ Birthday: Mette Frederiksen")
    
    test_students_niels_bohr()
    print("✓ Students: Niels Bohr")
    
    test_all_endpoint()
    print("✓ All endpoint")
    
    test_political_party()
    print("✓ Political party")
    
    test_person_not_found()
    print("✓ Person not found handling")
    
    test_with_context()
    print("✓ Context field accepted")
    
    print("\n✅ All tests passed!")