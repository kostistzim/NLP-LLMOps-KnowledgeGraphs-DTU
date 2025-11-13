"""
Test data for sentiment analysis - Course evaluations in Danish and English
Each tuple: (text, expected_score, language, description)
"""

COURSE_EVALUATIONS = [
    # Very Positive (4-5)
    ("Fantastisk kursus! Jeg lærte utrolig meget og underviseren var inspirerende.", 5, "da", "Very positive Danish"),
    ("This was an absolutely amazing course! Best I've ever taken.", 5, "en", "Very positive English"),
    ("Rigtig godt kursus med en meget engagerende underviser.", 4, "da", "Positive Danish"),
    ("Really good course, learned a lot and the material was excellent.", 4, "en", "Positive English"),
    
    # Positive (2-3)
    ("God underviser og interessant pensum.", 3, "da", "Simple positive Danish"),
    ("It was a good course overall.", 3, "en", "Simple positive English"),
    ("Kurset var lærerigt og godt struktureret.", 3, "da", "Structured positive Danish"),
    ("The lectures were informative and well-organized.", 3, "en", "Organized positive English"),
    
    # Neutral (0-1)
    ("Kurset var okay, men kunne være bedre.", 0, "da", "Neutral Danish"),
    ("The course was average, nothing special.", 0, "en", "Neutral English"),
    ("Det var et standard kursus.", 0, "da", "Standard neutral Danish"),
    
    # Negative (-2 to -3)
    ("Det var et dårligt kursus, meget ustruktureret.", -3, "da", "Negative Danish"),
    ("It was a bad course with poor organization.", -3, "en", "Negative English"),
    ("Kedelig underviser og irrelevant materiale.", -3, "da", "Boring negative Danish"),
    ("Very dry course and I did not learn much.", -3, "en", "Dry negative English"),
    
    # Very Negative (-4 to -5)
    ("Forfærdeligt kursus! Totalt spild af tid.", -5, "da", "Very negative Danish"),
    ("Absolutely terrible course, worst I've ever taken.", -5, "en", "Very negative English"),
    ("Rigtig dårligt kursus med en uengagerende og forvirrende underviser.", -5, "da", "Multiple negatives Danish"),
    
    # Edge cases with negations
    ("Det var ikke et godt kursus.", -3, "da", "Negation Danish"),
    ("It was not a good course.", -3, "en", "Negation English"),
    ("Ikke særlig interessant, men heller ikke dårligt.", -1, "da", "Mixed negation Danish"),
]

# The three original test cases from assignment
ASSIGNMENT_TESTS = [
    ("Det var en god lærer.", 3, "da", "Assignment test 1"),
    ("It was a bad course", -3, "en", "Assignment test 2"),
    ("It was a very dry course and I did not learn much.", -3, "en", "Assignment test 3"),
]

# All tests combined
ALL_TESTS = ASSIGNMENT_TESTS + COURSE_EVALUATIONS


def get_test_cases():
    """Return all test cases"""
    return ALL_TESTS


def get_assignment_tests():
    """Return only the three required assignment tests"""
    return ASSIGNMENT_TESTS


if __name__ == "__main__":
    print(f"Total test cases: {len(ALL_TESTS)}")
    print(f"Assignment tests: {len(ASSIGNMENT_TESTS)}")
    print(f"Additional tests: {len(COURSE_EVALUATIONS)}")
    print("\nTest cases by language:")
    danish = [t for t in ALL_TESTS if t[2] == "da"]
    english = [t for t in ALL_TESTS if t[2] == "en"]
    print(f"  Danish: {len(danish)}")
    print(f"  English: {len(english)}")
