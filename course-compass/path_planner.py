"""
Find optimal study paths through course graph
Uses NetworkX graph algorithms
"""

import networkx as nx
from typing import List, Dict, Optional


def find_study_path(
    graph: nx.DiGraph,
    target_course: str,
    completed_courses: List[str] = None
) -> Optional[List[str]]:
    """
    Find path from completed courses to target course
    
    Args:
        graph: Course dependency graph
        target_course: Target course code
        completed_courses: List of already completed course codes
        
    Returns:
        Ordered list of courses to take, or None if no path
    """
    if completed_courses is None:
        completed_courses = []
    
    # Check if target exists
    if target_course not in graph:
        return None
    
    # If no courses completed, find all paths from root nodes
    if not completed_courses:
        # Find root nodes (no prerequisites)
        root_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        
        # Try to find path from any root
        for root in root_nodes:
            if nx.has_path(graph, root, target_course):
                path = nx.shortest_path(graph, root, target_course)
                return path
        
        return None
    
    # Find path from last completed course
    last_completed = completed_courses[-1]
    
    if nx.has_path(graph, last_completed, target_course):
        path = nx.shortest_path(graph, last_completed, target_course)
        # Remove first node (already completed)
        return path[1:]
    
    return None


def get_all_prerequisites(graph: nx.DiGraph, course: str) -> List[str]:
    """
    Get all prerequisites for a course (transitive closure)
    
    Args:
        graph: Course dependency graph
        course: Target course code
        
    Returns:
        List of all prerequisite courses
    """
    if course not in graph:
        return []
    
    # Get all ancestors (courses that come before)
    predecessors = nx.ancestors(graph, course)
    
    return list(predecessors)


def get_direct_prerequisites(graph: nx.DiGraph, course: str) -> List[Dict]:
    """
    Get direct prerequisites (immediate dependencies)
    
    Args:
        graph: Course dependency graph
        course: Target course code
        
    Returns:
        List of dicts with prerequisite info
    """
    if course not in graph:
        return []
    
    prereqs = []
    for prereq in graph.predecessors(course):
        edge_data = graph.get_edge_data(prereq, course)
        prereqs.append({
            "course_code": prereq,
            "title": graph.nodes[prereq].get('title', ''),
            "weight": edge_data.get('weight', 0)
        })
    
    # Sort by weight (strongest prerequisites first)
    prereqs.sort(key=lambda x: x['weight'], reverse=True)
    
    return prereqs


def generate_study_plan(
    graph: nx.DiGraph,
    target_course: str,
    completed_courses: List[str] = None,
    courses_per_semester: int = 3
) -> List[Dict]:
    """
    Generate semester-by-semester study plan
    
    Args:
        graph: Course dependency graph
        target_course: Target course code
        completed_courses: Already completed courses
        courses_per_semester: Max courses per semester
        
    Returns:
        List of semesters with courses
    """
    if completed_courses is None:
        completed_courses = []
    
    path = find_study_path(graph, target_course, completed_courses)
    
    if not path:
        return []
    
    # Split into semesters
    semesters = []
    for i in range(0, len(path), courses_per_semester):
        semester_courses = path[i:i + courses_per_semester]
        
        semester = {
            "semester": len(semesters) + 1,
            "courses": []
        }
        
        for course_code in semester_courses:
            semester["courses"].append({
                "course_code": course_code,
                "title": graph.nodes[course_code].get('title', ''),
                "ects": graph.nodes[course_code].get('ects', 0)
            })
        
        semesters.append(semester)
    
    return semesters


if __name__ == "__main__":
    from indexer import build_course_index
    from graph_builder import build_course_graph
    from config import initialize_dspy
    
    # Initialize
    initialize_dspy()
    courses, vectorstore = build_course_index()
    
    # Build graph with subset
    print("\nBuilding graph with subset...")
    test_courses = courses[:20]
    G = build_course_graph(test_courses, vectorstore)
    
    # Test path finding
    print("\n" + "="*60)
    print("Testing Path Planner")
    print("="*60)
    
    # Pick a course with prerequisites
    target = list(G.nodes())[10]  # Some course
    
    print(f"\nTarget course: {target}")
    print(f"Title: {G.nodes[target].get('title', '')}\n")
    
    # Get prerequisites
    direct_prereqs = get_direct_prerequisites(G, target)
    print(f"Direct prerequisites ({len(direct_prereqs)}):")
    for prereq in direct_prereqs[:5]:
        print(f"  → {prereq['course_code']}: {prereq['title'][:40]}...")
    
    all_prereqs = get_all_prerequisites(G, target)
    print(f"\nAll prerequisites: {len(all_prereqs)} courses")
    
    # Find path
    path = find_study_path(G, target)
    if path:
        print(f"\nStudy path to {target}:")
        for i, course in enumerate(path, 1):
            print(f"  {i}. {course}: {G.nodes[course].get('title', '')[:40]}...")
    else:
        print(f"\nNo path found to {target}")