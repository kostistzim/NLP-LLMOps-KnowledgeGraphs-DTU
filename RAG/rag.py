"""
RAG (Retrieval-Augmented Generation) logic
Combines retrieval results with LLM to generate answers
"""

import os
from typing import List, Dict
import dspy
from dotenv import load_dotenv


def initialize_dspy():
    """
    Initialize DSPy with CampusAI API credentials
    Loads from ~/.env file
    """
    load_dotenv(os.path.expanduser("~/.env"))
    
    api_key = os.getenv("CAMPUSAI_API_KEY")
    if not api_key:
        raise ValueError("CAMPUSAI_API_KEY not found in ~/.env")
    
    # CampusAI endpoint
    api_base = "https://campusai.compute.dtu.dk/api/v1"
    model = "Qwen3"  # or whatever model you prefer
    
    # Configure DSPy
    lm = dspy.LM(
        model=f"openai/{model}",
        api_key=api_key,
        api_base=api_base
    )
    dspy.configure(lm=lm)
    
    print(f"✅ DSPy configured with CampusAI model: {model}")


def format_course_context(courses: List[Dict]) -> str:
    """
    Format retrieved courses into readable context for LLM
    
    Args:
        courses: List of course dicts from retriever
        
    Returns:
        Formatted string with course information
    """
    if not courses:
        return "No relevant courses found."
    
    context_parts = []
    for i, course in enumerate(courses, 1):
        parts = [f"Course {i}:"]
        parts.append(f"Code: {course['course_code']}")
        parts.append(f"Title: {course['title']}")
        
        # Add fields (teacher, ECTS, etc.)
        fields = course.get('fields', {})
        if 'Responsible' in fields:
            parts.append(f"Teacher: {fields['Responsible']}")
        if 'Point( ECTS )' in fields:
            parts.append(f"ECTS: {fields['Point( ECTS )']}")
        if 'Department' in fields:
            parts.append(f"Department: {fields['Department']}")
        
        context_parts.append('\n'.join(parts))
    
    return '\n\n'.join(context_parts)


def build_rag_prompt(query: str, courses: List[Dict]) -> str:
    """
    Build complete prompt for LLM with question and context
    
    Args:
        query: User's question
        courses: Retrieved courses
        
    Returns:
        Complete prompt string
    """
    context = format_course_context(courses)
    
    prompt = f"""You are a helpful assistant for DTU courses.
Use the context below to answer the user's question accurately.
If the answer is not present in the context, say you don't know.

Question: {query}

Context:
{context}

Answer:"""
    
    # Limit prompt size (LLMs have token limits)
    if len(prompt) > 4000:
        prompt = prompt[:4000] + "\n\n[Context truncated]"
    
    return prompt


def generate_answer(query: str, courses: List[Dict]) -> str:
    """
    Generate natural language answer using LLM
    
    Args:
        query: User's question
        courses: Retrieved courses for context
        
    Returns:
        Generated answer string
    """
    prompt = build_rag_prompt(query, courses)
    
    # Use DSPy to generate answer
    # Simple predict: takes prompt, returns completion
    predictor = dspy.Predict("prompt -> answer")
    result = predictor(prompt=prompt)
    
    return result.answer


def answer_question(query: str, courses: List[Dict]) -> Dict:
    """
    Complete RAG pipeline: format context + generate answer
    
    Args:
        query: User's question
        courses: Retrieved courses
        
    Returns:
        Dict with answer and retrieved courses
    """
    answer = generate_answer(query, courses)
    
    # Format retrieved courses for response (without full fields)
    retrieved = [
        {
            "course_code": c['course_code'],
            "title": c['title']
        }
        for c in courses
    ]
    
    return {
        "query": query,
        "answer": answer,
        "retrieved_courses": retrieved
    }


if __name__ == "__main__":
    # Test RAG system
    initialize_dspy()
    
    # Mock retrieved courses for testing
    mock_courses = [
        {
            "course_code": "02465",
            "title": "02465 Introduction to reinforcement learning and control",
            "fields": {
                "Responsible": "Tue Herlau",
                "Point( ECTS )": 5
            },
            "score": 0.95
        }
    ]
    
    query = "How many ECTS points is Tue Herlau's course?"
    
    print(f"\n--- Testing RAG ---")
    print(f"Query: {query}\n")
    
    result = answer_question(query, mock_courses)
    
    print(f"Answer: {result['answer']}\n")
    print(f"Retrieved courses: {result['retrieved_courses']}")