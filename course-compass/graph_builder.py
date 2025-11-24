"""
Build course dependency graph using NetworkX
Combines prerequisite extraction with course matching
"""

import networkx as nx
from typing import List, Dict, Tuple
from langchain_community.vectorstores import FAISS

from prerequisite_extractor import extract_prerequisites, ConceptExtractor
from course_matcher import match_prerequisites_to_courses


def build_course_graph(
    courses: List[Dict],
    vectorstore: FAISS,
    min_similarity: float = 0.4
) -> nx.DiGraph:
    """
    Build directed graph of course dependencies
    
    Args:
        courses: List of course dictionaries
        vectorstore: FAISS vector store for matching
        min_similarity: Minimum similarity for edge creation
        
    Returns:
        NetworkX directed graph with course dependencies
    """
    print("Building course dependency graph...")
    
    G = nx.DiGraph()
    extractor = ConceptExtractor()
    
    # Add all courses as nodes
    for course in courses:
        code = course.get('course_code', '')
        G.add_node(code, **{
            'title': course.get('title', ''),
            'ects': course.get('fields', {}).get('Point( ECTS )', 0),
            'responsible': course.get('fields', {}).get('Responsible', '')
        })
    
    # Build edges based on prerequisites
    for i, course in enumerate(courses, 1):
        course_code = course.get('course_code', '')
        print(f"Analyzing {course_code} ({i}/{len(courses)})...")
        
        # Extract prerequisites
        prerequisites = extract_prerequisites(course, extractor)
        
        if not prerequisites:
            continue
        
        # Find courses teaching these prerequisites
        concept_matches, prereq_courses = match_prerequisites_to_courses(
            vectorstore,
            prerequisites
        )
        
        # Add edges from prerequisite courses to this course
        for prereq_course in prereq_courses:
            prereq_code = prereq_course['course_code']
            
            # Don't add self-loops
            if prereq_code == course_code:
                continue
            
            # Only add if similarity is high enough
            if prereq_course['avg_similarity'] >= min_similarity:
                # Weight by similarity and number of concepts
                weight = prereq_course['avg_similarity'] * len(prereq_course['concepts_taught'])
                
                G.add_edge(prereq_code, course_code, weight=weight)
                print(f"  → {prereq_code} → {course_code} (weight: {weight:.2f})")
    
    print(f"\n✅ Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    return G


def get_graph_statistics(G: nx.DiGraph) -> Dict:
    """
    Calculate graph statistics
    
    Args:
        G: NetworkX directed graph
        
    Returns:
        Dict with statistics
    """
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "is_dag": nx.is_directed_acyclic_graph(G),
        "density": nx.density(G)
    }
    
    # In/out degree statistics
    in_degrees = [d for n, d in G.in_degree()]
    out_degrees = [d for n, d in G.out_degree()]
    
    if in_degrees:
        stats["avg_in_degree"] = sum(in_degrees) / len(in_degrees)
        stats["max_in_degree"] = max(in_degrees)
    
    if out_degrees:
        stats["avg_out_degree"] = sum(out_degrees) / len(out_degrees)
        stats["max_out_degree"] = max(out_degrees)
    
    return stats


if __name__ == "__main__":
    from indexer import build_course_index
    from config import initialize_dspy
    
    # Initialize
    initialize_dspy()
    print("\nBuilding course index...")
    courses, vectorstore = build_course_index()
    
    # Test with subset for speed
    print("\n" + "="*60)
    print("Testing Graph Builder (using subset of courses)")
    print("="*60 + "\n")
    
    test_courses = courses[:10]  # First 10 courses for testing
    
    G = build_course_graph(test_courses, vectorstore)
    
    # Statistics
    print("\n" + "="*60)
    print("Graph Statistics")
    print("="*60)
    
    stats = get_graph_statistics(G)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Show some edges
    print("\n" + "="*60)
    print("Sample Dependencies (first 10)")
    print("="*60 + "\n")
    
    edges = list(G.edges(data=True))[:10]
    for source, target, data in edges:
        source_title = G.nodes[source].get('title', source)[:40]
        target_title = G.nodes[target].get('title', target)[:40]
        weight = data.get('weight', 0)
        print(f"{source} → {target}")
        print(f"  {source_title}...")
        print(f"  → {target_title}...")
        print(f"  Weight: {weight:.2f}\n")