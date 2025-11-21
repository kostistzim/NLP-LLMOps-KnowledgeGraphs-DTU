"""
Prompt templates for person name extraction
"""

EXTRACT_PERSONS_SYSTEM = """You are an expert at extracting person names from text.
Extract only person names, not places, organizations, or other entities.
Return the result as a valid JSON array of strings.
Do not include titles like Mr., Ms., Dr. - only the actual names."""


EXTRACT_PERSONS_PROMPT = """Extract all person names from the following text.
Return ONLY a JSON array of name strings, nothing else.

Examples:

Text: "Ms Mette Frederiksen is in New York today."
Answer: ["Mette Frederiksen"]

Text: "Einstein and von Neumann meet each other."
Answer: ["Einstein", "von Neumann"]

Text: "Dr. Smith visited the University of Oxford."
Answer: ["Smith"]

Now extract from:
Text: {text}
Answer:"""


def get_extract_persons_messages(text: str) -> list:
    """
    Build messages for OpenAI chat completion
    
    Args:
        text: Text to extract person names from
        
    Returns:
        List of message dicts for OpenAI API
    """
    return [
        {"role": "system", "content": EXTRACT_PERSONS_SYSTEM},
        {"role": "user", "content": EXTRACT_PERSONS_PROMPT.format(text=text)}
    ]