"""
Retrieval logic for course search
Supports sparse (TF-IDF), dense (embeddings), and hybrid modes
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple


class CourseRetriever:
    """Retriever for course-level search"""
    
    def __init__(self, index: Dict):
        self.texts = index['texts']
        self.metadata = index['metadata']
        self.course_ids = index['course_ids']
        self.tfidf_vectorizer = index['tfidf_vectorizer']
        self.tfidf_matrix = index['tfidf_matrix']
        self.model = index['model']
        self.embeddings = index['embeddings']
    
    def search(self, query: str, mode: str = "dense", top_k: int = 10, alpha: float = 0.5) -> List[Dict]:
        """
        Search for courses matching query
        
        Args:
            query: Search query text
            mode: "sparse", "dense", or "hybrid"
            top_k: Number of results to return
            alpha: Weight for hybrid (alpha * dense + (1-alpha) * sparse)
            
        Returns:
            List of dicts with course_id, title, score
        """
        if mode == "sparse":
            scores = self._sparse_search(query)
        elif mode == "dense":
            scores = self._dense_search(query)
        elif mode == "hybrid":
            sparse_scores = self._sparse_search(query)
            dense_scores = self._dense_search(query)
            scores = alpha * dense_scores + (1 - alpha) * sparse_scores
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Get top K indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            results.append({
                "course_id": self.course_ids[idx],
                "title": self.metadata[idx]['title'],
                "score": float(scores[idx])
            })
        
        return results
    
    def find_similar(self, course_id: str, mode: str = "dense", top_k: int = 10, alpha: float = 0.5) -> List[Dict]:
        """
        Find courses similar to given course
        
        Args:
            course_id: Source course ID
            mode: "sparse", "dense", or "hybrid"
            top_k: Number of results
            alpha: Weight for hybrid
            
        Returns:
            List of similar courses (excluding the query course itself)
        """
        # Find index of query course
        try:
            query_idx = self.course_ids.index(course_id)
        except ValueError:
            return []
        
        if mode == "sparse":
            # Compute similarity with all courses
            query_vector = self.tfidf_matrix[query_idx]
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        elif mode == "dense":
            query_embedding = self.embeddings[query_idx].reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        elif mode == "hybrid":
            # Sparse
            query_vector = self.tfidf_matrix[query_idx]
            sparse_sim = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            # Dense
            query_embedding = self.embeddings[query_idx].reshape(1, -1)
            dense_sim = cosine_similarity(query_embedding, self.embeddings).flatten()
            # Combine
            similarities = alpha * dense_sim + (1 - alpha) * sparse_sim
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Get top K (excluding itself)
        top_indices = np.argsort(similarities)[::-1][1:top_k+1]  # Skip first (itself)
        
        results = []
        for idx in top_indices:
            results.append({
                "course_id": self.course_ids[idx],
                "title": self.metadata[idx]['title'],
                "score": float(similarities[idx])
            })
        
        return results
    
    def _sparse_search(self, query: str) -> np.ndarray:
        """TF-IDF search"""
        query_vector = self.tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        return similarities
    
    def _dense_search(self, query: str) -> np.ndarray:
        """Dense embedding search"""
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        return similarities


class ObjectiveRetriever:
    """Retriever for objective-level search"""
    
    def __init__(self, index: Dict):
        self.texts = index['texts']
        self.metadata = index['metadata']
        self.tfidf_vectorizer = index['tfidf_vectorizer']
        self.tfidf_matrix = index['tfidf_matrix']
        self.model = index['model']
        self.embeddings = index['embeddings']
    
    def search(self, query: str, mode: str = "dense", top_k: int = 10, alpha: float = 0.5) -> List[Dict]:
        """
        Search for learning objectives matching query
        
        Args:
            query: Search query text
            mode: "sparse", "dense", or "hybrid"
            top_k: Number of results
            alpha: Weight for hybrid
            
        Returns:
            List of dicts with course_id, title, objective, score
        """
        if mode == "sparse":
            scores = self._sparse_search(query)
        elif mode == "dense":
            scores = self._dense_search(query)
        elif mode == "hybrid":
            sparse_scores = self._sparse_search(query)
            dense_scores = self._dense_search(query)
            scores = alpha * dense_scores + (1 - alpha) * sparse_scores
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Get top K
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            meta = self.metadata[idx]
            results.append({
                "course_id": meta['course_id'],
                "title": meta['title'],
                "objective": meta['objective'],
                "score": float(scores[idx])
            })
        
        return results
    
    def _sparse_search(self, query: str) -> np.ndarray:
        """TF-IDF search"""
        query_vector = self.tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        return similarities
    
    def _dense_search(self, query: str) -> np.ndarray:
        """Dense embedding search"""
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        return similarities


if __name__ == "__main__":
    from indexer import build_all_indices
    
    print("Building indices...")
    indices = build_all_indices()
    
    print("\n--- Testing Course Retriever ---")
    course_retriever = CourseRetriever(indices['course_index'])
    
    # Test search
    results = course_retriever.search("machine learning", mode="dense", top_k=3)
    print("\nSearch 'machine learning':")
    for r in results:
        print(f"  {r['course_id']}: {r['title'][:50]}... (score: {r['score']:.3f})")
    
    # Test similar courses
    results = course_retriever.find_similar("02402", mode="dense", top_k=3)
    print("\nSimilar to 02402:")
    for r in results:
        print(f"  {r['course_id']}: {r['title'][:50]}... (score: {r['score']:.3f})")
    
    print("\n--- Testing Objective Retriever ---")
    objective_retriever = ObjectiveRetriever(indices['objective_index'])
    
    results = objective_retriever.search("dimensionality reduction", mode="dense", top_k=3)
    print("\nSearch 'dimensionality reduction':")
    for r in results:
        print(f"  {r['course_id']}: {r['objective'][:60]}... (score: {r['score']:.3f})")