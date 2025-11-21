"""
Build search indices from DTU course data
Creates both course-level and objective-level indices with TF-IDF and embeddings
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer


def load_courses(filepath: str = "data/courses.json") -> Dict:
    """Load course data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_course_documents(courses: Dict) -> Tuple[List[str], List[Dict], List[str]]:
    """
    Build course-level documents
    
    Returns:
        texts: List of document texts (title + objectives)
        metadata: List of dicts with course_id and title
        course_ids: List of course IDs (same order as texts)
    """
    texts = []
    metadata = []
    course_ids = []
    
    for course_id, course_data in courses.items():
        title = course_data['title']
        objectives = course_data['learning-objectives']
        
        # Combine title and objectives into one document
        text = title + "\n" + "\n".join(objectives)
        
        texts.append(text)
        metadata.append({
            "course_id": course_id,
            "title": title
        })
        course_ids.append(course_id)
    
    return texts, metadata, course_ids


def build_objective_documents(courses: Dict) -> Tuple[List[str], List[Dict]]:
    """
    Build objective-level documents (one per learning objective)
    
    Returns:
        texts: List of document texts (title + objective)
        metadata: List of dicts with course_id, title, and objective
    """
    texts = []
    metadata = []
    
    for course_id, course_data in courses.items():
        title = course_data['title']
        objectives = course_data['learning-objectives']
        
        for objective in objectives:
            # Each objective becomes a separate document
            text = f"{title} - {objective}"
            
            texts.append(text)
            metadata.append({
                "course_id": course_id,
                "title": title,
                "objective": objective
            })
    
    return texts, metadata


def build_tfidf_index(texts: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    """
    Build TF-IDF index for sparse retrieval
    
    Returns:
        vectorizer: Fitted TfidfVectorizer
        matrix: TF-IDF matrix (n_docs x n_features)
    """
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),  # Unigrams and bigrams
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


def build_all_indices(courses_path: str = "data/courses.json") -> Dict:
    """
    Build all indices (course and objective level, sparse and dense)
    
    Returns:
        Dictionary containing all indices and metadata
    """
    print("Loading courses...")
    courses = load_courses(courses_path)
    print(f"Loaded {len(courses)} courses")
    
    # Build course-level index
    print("\nBuilding course-level documents...")
    course_texts, course_metadata, course_ids = build_course_documents(courses)
    print(f"Created {len(course_texts)} course documents")
    
    print("Building course TF-IDF index...")
    course_tfidf_vectorizer, course_tfidf_matrix = build_tfidf_index(course_texts)
    
    print("Building course dense embeddings...")
    course_model, course_embeddings = build_dense_index(course_texts)
    
    # Build objective-level index
    print("\nBuilding objective-level documents...")
    objective_texts, objective_metadata = build_objective_documents(courses)
    print(f"Created {len(objective_texts)} objective documents")
    
    print("Building objective TF-IDF index...")
    objective_tfidf_vectorizer, objective_tfidf_matrix = build_tfidf_index(objective_texts)
    
    print("Building objective dense embeddings...")
    objective_model, objective_embeddings = build_dense_index(objective_texts)
    
    print("\n✅ All indices built successfully!")
    
    return {
        "course_index": {
            "texts": course_texts,
            "metadata": course_metadata,
            "course_ids": course_ids,
            "tfidf_vectorizer": course_tfidf_vectorizer,
            "tfidf_matrix": course_tfidf_matrix,
            "model": course_model,
            "embeddings": course_embeddings
        },
        "objective_index": {
            "texts": objective_texts,
            "metadata": objective_metadata,
            "tfidf_vectorizer": objective_tfidf_vectorizer,
            "tfidf_matrix": objective_tfidf_matrix,
            "model": objective_model,
            "embeddings": objective_embeddings
        }
    }


if __name__ == "__main__":
    # Test building indices
    indices = build_all_indices()
    
    print("\n--- Index Stats ---")
    print(f"Courses: {len(indices['course_index']['course_ids'])}")
    print(f"Objectives: {len(indices['objective_index']['texts'])}")
    print(f"Course embedding shape: {indices['course_index']['embeddings'].shape}")
    print(f"Objective embedding shape: {indices['objective_index']['embeddings'].shape}")