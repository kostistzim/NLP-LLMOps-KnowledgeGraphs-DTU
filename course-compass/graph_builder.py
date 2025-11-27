"""
Build course dependency graphs using NetworkX.

1. Official graph:
   - build_official_course_graph:
       Uses precomputed prerequisite course codes from
       prerequisites_official.jsonl (no LLM calls).

2. LLM-based graph:
   - build_course_graph:
       Uses prerequisite extraction and semantic matching.
"""

import json
from typing import List, Dict, Any

import networkx as nx
from langchain_community.vectorstores import FAISS

from prerequisite_extractor import extract_prerequisites, ConceptExtractor
from course_matcher import match_prerequisites_to_courses


# ---------------------------------------------------------------------------
# Helper: load official prereqs
# ---------------------------------------------------------------------------

def load_official_prereqs(path: str) -> Dict[str, List[str]]:
    """
    Load prerequisites_official.jsonl into a mapping:
        { course_code: [prereq_code1, prereq_code2, ...] }
    """
    mapping: Dict[str, List[str]] = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)
            code = obj.get("course_code")
            prereq_codes = obj.get("prereq_course_codes") or []

            if code:
                mapping[code] = prereq_codes

    return mapping


# ---------------------------------------------------------------------------
# 1. OFFICIAL PREREQUISITE GRAPH  (no LLM)
# ---------------------------------------------------------------------------

def build_official_course_graph(
    courses: List[Dict[str, Any]],
    official_prereqs: Dict[str, List[str]],
) -> nx.DiGraph:
    """
    Build a directed graph of course dependencies using ONLY the official
    prerequisite course codes extracted from the DTU course catalog.

    Nodes: course_code (with attributes: title, ects, responsible)
    Edges: prereq_code -> course_code (weight=1.0)
    """
    print("Building official course dependency graph...")

    G = nx.DiGraph()

    # Index courses for lookup
    courses_by_code: Dict[str, Dict[str, Any]] = {
        c.get("course_code"): c for c in courses if c.get("course_code")
    }

    # Create nodes
    for code, course in courses_by_code.items():
        fields = course.get("fields", {}) or {}
        ects = fields.get("Point( ECTS )", 0)
        responsible = fields.get("Responsible", "")

        G.add_node(
            code,
            title=course.get("title", ""),
            ects=ects,
            responsible=responsible,
        )

    # Create edges from official prereqs
    edge_count = 0

    for course_code, prereq_list in official_prereqs.items():
        # Only consider courses that exist in the dataset
        if course_code not in courses_by_code:
            continue

        for prereq_code in prereq_list:
            if prereq_code == course_code:
                continue

            if prereq_code not in courses_by_code:
                continue

            G.add_edge(
                prereq_code,
                course_code,
                weight=1.0,
                source="official",
            )
            edge_count += 1

    print(f"Official graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


# ---------------------------------------------------------------------------
# 2. LLM-BASED GRAPH (your original implementation)
# ---------------------------------------------------------------------------

def build_course_graph(
    courses: List[Dict],
    vectorstore: FAISS,
    min_similarity: float = 0.4,
) -> nx.DiGraph:
    """
    Build directed graph of course dependencies using LLM-based extraction.
    This is more expensive and is not used in the main API anymore.
    """
    print("Building LLM-based course dependency graph...")

    G = nx.DiGraph()
    extractor = ConceptExtractor()

    for course in courses:
        code = course.get("course_code", "")
        fields = course.get("fields", {}) or {}
        G.add_node(
            code,
            title=course.get("title", ""),
            ects=fields.get("Point( ECTS )", 0),
            responsible=fields.get("Responsible", ""),
        )

    for i, course in enumerate(courses, 1):
        course_code = course.get("course_code", "")
        print(f"Analyzing {course_code} ({i}/{len(courses)})...")

        prerequisites = extract_prerequisites(course, extractor)
        if not prerequisites:
            continue

        concept_matches, prereq_courses = match_prerequisites_to_courses(
            vectorstore,
            prerequisites,
        )

        for prereq_course in prereq_courses:
            prereq_code = prereq_course["course_code"]

            if prereq_code == course_code:
                continue

            if prereq_course["avg_similarity"] >= min_similarity:
                weight = prereq_course["avg_similarity"] * len(prereq_course["concepts_taught"])

                G.add_edge(
                    prereq_code,
                    course_code,
                    weight=weight,
                    source="inferred",
                )
                print(f"  {prereq_code} -> {course_code} (weight: {weight:.2f})")

    print(f"LLM-based graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


# ---------------------------------------------------------------------------
# 3. Stats
# ---------------------------------------------------------------------------

def get_graph_statistics(G: nx.DiGraph) -> Dict[str, Any]:
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "is_dag": nx.is_directed_acyclic_graph(G),
        "density": nx.density(G),
    }

    in_degrees = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]

    if in_degrees:
        stats["avg_in_degree"] = sum(in_degrees) / len(in_degrees)
        stats["max_in_degree"] = max(in_degrees)

    if out_degrees:
        stats["avg_out_degree"] = sum(out_degrees) / len(out_degrees)
        stats["max_out_degree"] = max(out_degrees)

    return stats
