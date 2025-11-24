"""
Load DTU courses and build searchable vector store
Uses LangChain for document loading and FAISS for vector search
"""

import json
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings  
from langchain_core.documents import Document

from config import COURSES_FILE, EMBEDDING_MODEL


def load_courses_jsonl(filepath: str = COURSES_FILE) -> List[Dict]:
    """
    Load courses from JSONL file
    Each line is a separate JSON object
    
    Returns:
        List of course dictionaries
    """
    courses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                course = json.loads(line)
                courses.append(course)
    
    print(f"✅ Loaded {len(courses)} courses from {filepath}")
    return courses


def course_to_text(course: Dict) -> str:
    """
    Convert course dict to searchable text
    Combines title, objectives, content for semantic search
    
    Args:
        course: Course dictionary
        
    Returns:
        Combined text string
    """
    parts = []
    
    # Title
    parts.append(course.get('title', ''))
    
    # Learning objectives (most important for prerequisites)
    objectives = course.get('learning_objectives', [])
    if objectives:
        parts.append("Learning objectives: " + " ".join(objectives))
    
    # Content
    content = course.get('content', '')
    if content:
        # Limit to 1000 chars for efficiency
        parts.append(content[:1000])
    
    # Fields (teacher, ECTS, etc.)
    fields = course.get('fields', {})
    if 'Responsible' in fields:
        parts.append(f"Taught by {fields['Responsible']}")
    
    return '\n'.join(parts)


def courses_to_documents(courses: List[Dict]) -> List[Document]:
    """
    Convert courses to LangChain Document objects
    
    Args:
        courses: List of course dictionaries
        
    Returns:
        List of LangChain Documents with metadata
    """
    documents = []
    
    for course in courses:
        # Create searchable text
        text = course_to_text(course)
        
        # Store important metadata
        metadata = {
            "course_code": course.get('course_code', ''),
            "title": course.get('title', ''),
            "ects": course.get('fields', {}).get('Point( ECTS )', 0),
            "responsible": course.get('fields', {}).get('Responsible', ''),
            "department": course.get('fields', {}).get('Department', '')
        }
        
        # Create LangChain Document
        doc = Document(page_content=text, metadata=metadata)
        documents.append(doc)
    
    return documents


def build_vector_store(documents: List[Document]) -> FAISS:
    """
    Build FAISS vector store from documents
    Uses sentence-transformers for embeddings
    
    Args:
        documents: List of LangChain Documents
        
    Returns:
        FAISS vector store ready for semantic search
    """
    print(f"Building embeddings with model: {EMBEDDING_MODEL}")
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Build FAISS index
    print("Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    print(f"✅ Vector store built with {len(documents)} documents")
    return vectorstore


def build_course_index(filepath: str = COURSES_FILE) -> tuple:
    """
    Complete pipeline: Load courses → Build vector store
    
    Args:
        filepath: Path to courses JSONL file
        
    Returns:
        Tuple of (courses_list, vectorstore)
    """
    # Load courses
    courses = load_courses_jsonl(filepath)
    
    # Convert to LangChain documents
    documents = courses_to_documents(courses)
    
    # Build vector store
    vectorstore = build_vector_store(documents)
    
    return courses, vectorstore


if __name__ == "__main__":
    # Test indexing
    print("Testing course indexing...\n")
    
    courses, vectorstore = build_course_index()
    
    # Test search
    print("\n--- Testing Semantic Search ---")
    query = "machine learning"
    results = vectorstore.similarity_search(query, k=3)
    
    print(f"\nQuery: '{query}'")
    print("Top 3 results:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.metadata['course_code']}: {doc.metadata['title']}")
        print(f"   Content preview: {doc.page_content[:100]}...")
    
    # Test with teacher name
    print("\n--- Testing Teacher Search ---")
    query = "Tue Herlau"
    results = vectorstore.similarity_search(query, k=2)
    
    print(f"\nQuery: '{query}'")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.metadata['course_code']}: {doc.metadata['title']}")
        print(f"   Teacher: {doc.metadata['responsible']}")