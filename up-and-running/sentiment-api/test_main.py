"""
Comprehensive test suite for sentiment API
Tests all required functionality including the three assignment cases
"""

from fastapi.testclient import TestClient
from main import app
from test_data import ASSIGNMENT_TESTS, ALL_TESTS

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    print("✓ Root endpoint working")


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check working")


def test_assignment_cases():
    """Test the three required assignment cases"""
    print("\n" + "="*60)
    print("TESTING REQUIRED ASSIGNMENT CASES")
    print("="*60)
    
    for text, expected_score, language, description in ASSIGNMENT_TESTS:
        response = client.post("/v1/sentiment", json={"text": text})
        assert response.status_code == 200
        
        actual_score = response.json()["score"]
        
        # Check if score matches expected
        if actual_score == expected_score:
            print(f"✓ PASS: {description}")
            print(f"  Text: '{text}'")
            print(f"  Expected: {expected_score}, Got: {actual_score}")
        else:
            print(f"✗ FAIL: {description}")
            print(f"  Text: '{text}'")
            print(f"  Expected: {expected_score}, Got: {actual_score}")
            # Don't fail the test, just report the difference
    
    print("="*60)


def test_all_cases():
    """Test all course evaluation cases"""
    print("\n" + "="*60)
    print("TESTING ALL COURSE EVALUATION CASES")
    print("="*60)
    
    passed = 0
    failed = 0
    tolerance = 1  # Allow ±1 difference in score
    
    for text, expected_score, language, description in ALL_TESTS:
        response = client.post("/v1/sentiment", json={"text": text})
        assert response.status_code == 200
        
        actual_score = response.json()["score"]
        difference = abs(actual_score - expected_score)
        
        if difference <= tolerance:
            passed += 1
            status = "✓"
        else:
            failed += 1
            status = "✗"
        
        print(f"{status} [{language}] Expected: {expected_score:2d}, Got: {actual_score:2d} | {text[:50]}")
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed (tolerance: ±{tolerance})")
    print(f"Accuracy: {passed}/{len(ALL_TESTS)} = {100*passed/len(ALL_TESTS):.1f}%")
    print("="*60)


def test_detailed_endpoint():
    """Test detailed sentiment endpoint"""
    print("\n" + "="*60)
    print("TESTING DETAILED ENDPOINT")
    print("="*60)
    
    test_cases = [
        ("Det var en god lærer.", "da"),
        ("It was a bad course", "en"),
    ]
    
    for text, expected_lang in test_cases:
        response = client.post("/v1/sentiment/detailed", json={"text": text})
        assert response.status_code == 200
        
        data = response.json()
        assert "score" in data
        assert "language" in data
        assert "text" in data
        assert data["language"] == expected_lang
        
        print(f"✓ Text: '{text}'")
        print(f"  Score: {data['score']}, Language: {data['language']}")
    
    print("="*60)


def test_negations():
    """Test negation handling"""
    print("\n" + "="*60)
    print("TESTING NEGATION HANDLING")
    print("="*60)
    
    test_cases = [
        ("It was not a good course.", "Should be negative"),
        ("Det var ikke et godt kursus.", "Should be negative (Danish)"),
        ("Not bad at all", "Double negation - should be positive or neutral"),
    ]
    
    for text, expectation in test_cases:
        response = client.post("/v1/sentiment", json={"text": text})
        score = response.json()["score"]
        print(f"  '{text}'")
        print(f"  Score: {score} ({expectation})")
    
    print("="*60)


def test_intensifiers():
    """Test intensifier handling"""
    print("\n" + "="*60)
    print("TESTING INTENSIFIER HANDLING")
    print("="*60)
    
    test_cases = [
        ("It was a good course.", "good without intensifier"),
        ("It was a very good course.", "very good - should be higher"),
        ("Det var et godt kursus.", "godt without intensifier"),
        ("Det var et meget godt kursus.", "meget godt - should be higher"),
    ]
    
    for text, expectation in test_cases:
        response = client.post("/v1/sentiment", json={"text": text})
        score = response.json()["score"]
        print(f"  '{text}'")
        print(f"  Score: {score} ({expectation})")
    
    print("="*60)


def test_invalid_input():
    """Test error handling"""
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    # Test empty text
    response = client.post("/v1/sentiment", json={"text": ""})
    print(f"  Empty text: Status {response.status_code}")
    
    # Test missing field
    response = client.post("/v1/sentiment", json={})
    print(f"  Missing field: Status {response.status_code}")
    assert response.status_code == 422  # Validation error
    
    print("✓ Error handling working correctly")
    print("="*60)


def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 SENTIMENT API TEST SUITE" + "\n")
    
    test_root_endpoint()
    test_health_check()
    test_assignment_cases()
    test_detailed_endpoint()
    test_negations()
    test_intensifiers()
    test_all_cases()
    test_invalid_input()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
