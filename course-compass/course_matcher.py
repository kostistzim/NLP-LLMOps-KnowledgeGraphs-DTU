"""
Find courses that teach specific concepts
Uses LangChain vector search for semantic matching
"""

from typing import List, Dict, Tuple
from langchain_community.vectorstores import FAISS


def search_courses_by_concept(
    vectorstore: FAISS,
    concept: str,
    top_k: int = 5,
    score_threshold: float = 0.3
) -> List[Dict]:
    """
    Find courses that teach a specific concept using semantic search
    
    Args:
        vectorstore: FAISS vector store with course embeddings
        concept: Concept to search for (e.g., "linear algebra")
        top_k: Maximum number of results to return
        score_threshold: Minimum similarity score (0-1)
        
    Returns:
        List of dicts with course info and relevance scores
    """
    # Semantic search with scores
    results = vectorstore.similarity_search_with_score(concept, k=top_k)
    
    matches = []
    for doc, score in results:
        # Convert distance to similarity (FAISS returns L2 distance)
        # Lower distance = higher similarity
        similarity = 1 / (1 + score)
        
        if similarity >= score_threshold:
            matches.append({
                "course_code": doc.metadata['course_code'],
                "title": doc.metadata['title'],
                "similarity": similarity,
                "ects": doc.metadata.get('ects', 0),
                "responsible": doc.metadata.get('responsible', ''),
                "content_preview": doc.page_content[:200]
            })
    
    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    
    return matches


def find_teaching_courses(
    vectorstore: FAISS,
    concepts: List[str],
    courses_per_concept: int = 3
) -> Dict[str, List[Dict]]:
    """
    For each concept, find courses that teach it
    
    Args:
        vectorstore: FAISS vector store
        concepts: List of prerequisite concepts
        courses_per_concept: How many courses to find per concept
        
    Returns:
        Dict mapping concept -> list of matching courses
    """
    results = {}
    
    for concept in concepts:
        matches = search_courses_by_concept(
            vectorstore,
            concept,
            top_k=courses_per_concept
        )
        results[concept] = matches
    
    return results


def get_unique_prerequisite_courses(
    concept_matches: Dict[str, List[Dict]],
    min_concepts_taught: int = 1
) -> List[Dict]:
    """
    Get unique courses that teach prerequisite concepts
    
    Args:
        concept_matches: Dict from find_teaching_courses()
        min_concepts_taught: Minimum concepts a course must teach
        
    Returns:
        List of unique courses with aggregated info
    """
    # Track which courses teach which concepts
    course_info = {}
    
    for concept, matches in concept_matches.items():
        for match in matches:
            code = match['course_code']
            
            if code not in course_info:
                course_info[code] = {
                    "course_code": code,
                    "title": match['title'],
                    "ects": match['ects'],
                    "responsible": match['responsible'],
                    "concepts_taught": [],
                    "avg_similarity": 0.0,
                    "total_similarity": 0.0,
                    "match_count": 0
                }
            
            # Add concept and update similarity
            course_info[code]["concepts_taught"].append(concept)
            course_info[code]["total_similarity"] += match['similarity']
            course_info[code]["match_count"] += 1
    
    # Calculate average similarity
    for code, info in course_info.items():
        info["avg_similarity"] = info["total_similarity"] / info["match_count"]
        del info["total_similarity"]  # Remove intermediate field
        del info["match_count"]
    
    # Filter by minimum concepts taught
    filtered = [
        info for info in course_info.values()
        if len(info["concepts_taught"]) >= min_concepts_taught
    ]
    
    # Sort by number of concepts taught, then similarity
    filtered.sort(
        key=lambda x: (len(x["concepts_taught"]), x["avg_similarity"]),
        reverse=True
    )
    
    return filtered


def match_prerequisites_to_courses(
    vectorstore: FAISS,
    prerequisites: List[str]
) -> Tuple[Dict[str, List[Dict]], List[Dict]]:
    """
    Complete matching pipeline: prerequisites -> courses
    
    Args:
        vectorstore: FAISS vector store
        prerequisites: List of prerequisite concepts
        
    Returns:
        Tuple of (concept_matches, unique_courses)
    """
    # Find courses for each concept
    concept_matches = find_teaching_courses(vectorstore, prerequisites)
    
    # Get unique courses
    unique_courses = get_unique_prerequisite_courses(concept_matches)
    
    return concept_matches, unique_courses


if __name__ == "__main__":
    from indexer import build_course_index
    
    print("Building course index...\n")
    courses, vectorstore = build_course_index()
    
    print("\n" + "="*60)
    print("Testing Course Matcher")
    print("="*60)
    
    # Test 1: Single concept search
    print("\n--- Test 1: Search for 'linear algebra' ---")
    concept = "linear algebra"
    matches = search_courses_by_concept(vectorstore, concept, top_k=5)
    
    print(f"\nFound {len(matches)} courses teaching '{concept}':")
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match['course_code']}: {match['title']}")
        print(f"   Similarity: {match['similarity']:.3f}")
        print(f"   Teacher: {match['responsible']}")
    
    # Test 2: Multiple concepts
    print("\n\n--- Test 2: Find courses teaching multiple concepts ---")
    prerequisites = [
        "linear algebra",
        "calculus",
        "optimization theory",
        "programming in Python"
    ]
    
    concept_matches, unique_courses = match_prerequisites_to_courses(
        vectorstore,
        prerequisites
    )
    
    print(f"\nSearching for courses teaching: {', '.join(prerequisites)}")
    print(f"\n📚 Found {len(unique_courses)} unique prerequisite courses:\n")
    
    for i, course in enumerate(unique_courses[:5], 1):  # Top 5
        print(f"{i}. {course['course_code']}: {course['title']}")
        print(f"   Teaches {len(course['concepts_taught'])} concepts: {', '.join(course['concepts_taught'])}")
        print(f"   Average similarity: {course['avg_similarity']:.3f}")
        print(f"   ECTS: {course['ects']}")
        print()
    
    # Test 3: Detailed breakdown
    print("\n--- Test 3: Detailed concept-to-course mapping ---")
    for concept, matches in concept_matches.items():
        print(f"\n'{concept}':")
        for match in matches[:2]:  # Top 2 per concept
            print(f"  → {match['course_code']}: {match['title']} (score: {match['similarity']:.3f})")