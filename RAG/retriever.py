"""
Retrieval logic for course search
Supports sparse (TF-IDF), dense (embeddings), and hybrid modes
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


class CourseRetriever:
    """Retriever for course-level search"""
    
    def __init__(self, index: Dict):
        self.texts = index['texts']
        self.metadata = index['metadata']
        self.course_codes = index['course_codes']
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
            List of dicts with course_code, title, score
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
                "course_code": self.course_codes[idx],
                "title": self.metadata[idx]['title'],
                "score": float(scores[idx]),
                "fields": self.metadata[idx].get('fields', {})
            })
        
        return results
    
    def find_similar(self, course_code: str, mode: str = "dense", top_k: int = 10, alpha: float = 0.5) -> List[Dict]:
        """
        Find courses similar to given course
        
        Args:
            course_code: Source course code
            mode: "sparse", "dense", or "hybrid"
            top_k: Number of results
            alpha: Weight for hybrid
            
        Returns:
            List of similar courses (excluding the query course itself)
        """
        # Find index of query course
        try:
            query_idx = self.course_codes.index(course_code)
        except ValueError:
            return []
        
        if mode == "sparse":
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
        top_indices = np.argsort(similarities)[::-1][1:top_k+1]
        
        results = []
        for idx in top_indices:
            results.append({
                "course_code": self.course_codes[idx],
                "title": self.metadata[idx]['title'],
                "score": float(similarities[idx]),
                "fields": self.metadata[idx].get('fields', {})
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
    
    print("\n--- Testing Retriever ---")
    retriever = CourseRetriever(indices)
    
    # Test search
    results = retriever.search("machine learning", mode="dense", top_k=3)
    print("\nSearch 'machine learning':")
    for r in results:
        print(f"  {r['course_code']}: {r['title'][:60]}... (score: {r['score']:.3f})")
    
    # Test teacher search
    results = retriever.search("Tue Herlau", mode="dense", top_k=3)
    print("\nSearch 'Tue Herlau':")
    for r in results:
        teacher = r['fields'].get('Responsible', 'N/A')
        print(f"  {r['course_code']}: {r['title'][:40]}... Teacher: {teacher}")