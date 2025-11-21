"""
Sentence extraction using spaCy
Converts text string into list of sentences
"""

import spacy
from typing import List

# Load spaCy model once at module level
nlp = spacy.load("en_core_web_sm")


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text using spaCy
    
    Args:
        text: Raw text string
        
    Returns:
        List of sentence strings
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    return sentences


if __name__ == "__main__":
    # Test
    test_text = "This is the first sentence. This is the second sentence."
    sentences = extract_sentences(test_text)
    print(f"Found {len(sentences)} sentences:")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")