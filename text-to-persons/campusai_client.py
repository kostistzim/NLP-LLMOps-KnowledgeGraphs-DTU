"""
CampusAI client using OpenAI-compatible API
"""

import os
import json
import re
from typing import List
from openai import OpenAI

from prompts import get_extract_persons_messages


def get_campusai_client() -> OpenAI:
    """Initialize OpenAI client configured for CampusAI"""
    api_key = os.getenv("CAMPUSAI_API_KEY")
    if not api_key:
        raise ValueError("CAMPUSAI_API_KEY not found in environment variables")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://campusai.compute.dtu.dk/api/v1"
    )


def campusai_extract_persons(text: str, model: str = "Qwen3") -> List[str]:
    """Extract person names from text using CampusAI LLM"""
    client = get_campusai_client()
    messages = get_extract_persons_messages(text)
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=500
    )
    
    content = response.choices[0].message.content
    return parse_persons_response(content)


def parse_persons_response(response: str) -> List[str]:
    """Parse LLM response to extract list of person names"""
    response = response.strip()
    
    # Try direct JSON
    if response.startswith('['):
        return json.loads(response)
    
    # Extract JSON from text
    match = re.search(r'\[.*?\]', response, re.DOTALL)
    if match:
        return json.loads(match.group())
    
    # Fallback: comma-separated
    response = re.sub(r'^(Answer:|Names:|The names are:)\s*', '', response, flags=re.IGNORECASE)
    if ',' in response:
        names = [name.strip().strip('"').strip("'").strip('*').strip() for name in response.split(',')]
        return [n for n in names if n]
    
    return [response] if response else []


if __name__ == "__main__":
    test_texts = [
        "Ms Mette Frederiksen is in New York today.",
        "Einstein and von Neumann meet each other."
    ]
    
    for text in test_texts:
        names = campusai_extract_persons(text)
        print(f"Text: {text}")
        print(f"Names: {names}\n")