"""
Simple language detector for Danish and English
Uses character-based and word-based heuristics
"""

class LanguageDetector:
    """Detect if text is Danish or English"""
    
    # Common Danish words that are distinctive
    DANISH_WORDS = {
        'og', 'en', 'er', 'det', 'var', 'jeg', 'med', 'på', 'af', 'til',
        'ikke', 'der', 'som', 'havde', 'kan', 'også', 'være', 'så',
        'kursus', 'kurset', 'lærer', 'lærte', 'underviser', 'underviseren',
        'pensum', 'forelæsning', 'eksamen', 'godt', 'dårligt', 'meget'
    }
    
    # Common English words
    ENGLISH_WORDS = {
        'the', 'was', 'were', 'is', 'and', 'of', 'to', 'in', 'that',
        'course', 'teacher', 'learned', 'taught', 'instructor', 'lecture',
        'exam', 'good', 'bad', 'very', 'not', 'did', 'much'
    }
    
    # Danish-specific characters
    DANISH_CHARS = {'æ', 'ø', 'å', 'Æ', 'Ø', 'Å'}
    
    def detect(self, text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Input text
            
        Returns:
            'da' for Danish, 'en' for English
        """
        text_lower = text.lower()
        
        # Check for Danish-specific characters (strong signal)
        if any(char in text for char in self.DANISH_CHARS):
            return 'da'
        
        # Split into words
        words = set(text_lower.split())
        
        # Count Danish vs English word matches
        danish_matches = len(words & self.DANISH_WORDS)
        english_matches = len(words & self.ENGLISH_WORDS)
        
        # If clear winner, return that
        if danish_matches > english_matches:
            return 'da'
        elif english_matches > danish_matches:
            return 'en'
        
        # Default to English if unclear (most international contexts)
        return 'en'


if __name__ == "__main__":
    # Test the detector
    detector = LanguageDetector()
    
    test_cases = [
        ("Det var en god lærer.", "da"),
        ("It was a bad course", "en"),
        ("Fantastisk kursus!", "da"),
        ("Very good teacher", "en"),
        ("Jeg lærte meget", "da"),
    ]
    
    print("Testing language detector:")
    for text, expected in test_cases:
        detected = detector.detect(text)
        status = "✓" if detected == expected else "✗"
        print(f"{status} '{text}' -> {detected} (expected: {expected})")
