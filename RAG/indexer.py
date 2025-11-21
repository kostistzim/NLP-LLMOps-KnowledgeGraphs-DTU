"""
Build search indices from DTU course data (JSONL format)
Creates both course-level indices with TF-IDF and embeddings
"""



"""
my idea on how to structure the functions .
1. Load data → load_courses_jsonl()
2. Build text per course → build_course_text()
3. Process all courses → build_course_documents()
4. Build indices → build_tfidf/dense_index()
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer


def load_courses_jsonl(filepath: str = "data/dtu_courses.jsonl") -> List[Dict]:
    """
    Load courses from JSONL file
    Each line is a separate JSON object
    """
    courses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                courses.append(json.loads(line))
    return courses


def build_course_text(course: Dict) -> str:
    """
    Combine all course fields into searchable text
    Includes: title, teacher, ECTS, objectives, content
    """
    parts = []
    
    # Title
    parts.append(course.get('title', ''))
    
    # Fields (teacher, ECTS, department, etc.)
    fields = course.get('fields', {})
    if fields:
        # Add teacher name prominently
        if 'Responsible' in fields:
            parts.append(f"Taught by {fields['Responsible']}")
        # Add other fields as JSON
        parts.append(json.dumps(fields))
    
    # Learning objectives
    objectives = course.get('learning_objectives', [])
    if objectives:
        parts.append(' '.join(objectives))
    
    # Content
    content = course.get('content', '')
    if content:
        # Limit content to 2KB to avoid overwhelming embeddings
        parts.append(content[:2000])
    
    return '\n'.join(parts)


def build_course_documents(courses: List[Dict]) -> Tuple[List[str], List[Dict], List[str]]:
    """
    Build course-level documents for indexing
    
    Returns:
        texts: List of searchable texts
        metadata: List of dicts with course info
        course_codes: List of course codes
    """
    texts = []
    metadata = []
    course_codes = []
    
    for course in courses:
        text = build_course_text(course)
        
        texts.append(text)
        metadata.append({
            "course_code": course.get('course_code', ''),
            "title": course.get('title', ''),
            "fields": course.get('fields', {})
        })
        course_codes.append(course.get('course_code', ''))
    
    return texts, metadata, course_codes


def build_tfidf_index(texts: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    """
    Build TF-IDF index for sparse retrieval
    
    Returns:
        vectorizer: Fitted TfidfVectorizer
        matrix: TF-IDF matrix (n_docs x n_features)
    """
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=10000,
        stop_words='english'
    )
    
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def build_dense_index(texts: List[str], model_name: str = "distiluse-base-multilingual-cased-v2") -> Tuple[SentenceTransformer, np.ndarray]:
    """
    Build dense embedding index
    
    Returns:
        model: SentenceTransformer model
        embeddings: Dense embeddings (n_docs x embedding_dim)
    """
    model = SentenceTransformer(f"sentence-transformers/{model_name}")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return model, embeddings


def build_all_indices(courses_path: str = "data/dtu_courses.jsonl") -> Dict:
    """
    Build all indices from JSONL file
    
    Returns:
        Dictionary containing all indices and metadata
    """
    print("Loading courses from JSONL...")
    courses = load_courses_jsonl(courses_path)
    print(f"Loaded {len(courses)} courses")
    
    print("\nBuilding course documents...")
    texts, metadata, course_codes = build_course_documents(courses)
    
    print("Building TF-IDF index...")
    tfidf_vectorizer, tfidf_matrix = build_tfidf_index(texts)
    
    print("Building dense embeddings...")
    model, embeddings = build_dense_index(texts)
    
    print("\n✅ All indices built successfully!")
    
    return {
        "texts": texts,
        "metadata": metadata,
        "course_codes": course_codes,
        "tfidf_vectorizer": tfidf_vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "model": model,
        "embeddings": embeddings
    }


if __name__ == "__main__":
    # Test building indices
    indices = build_all_indices()
    
    print("\n--- Index Stats ---")
    print(f"Courses: {len(indices['course_codes'])}")
    print(f"Embedding shape: {indices['embeddings'].shape}")
    print(f"\nSample course text (first 200 chars):")
    print(indices['texts'][0][:200] + "...")