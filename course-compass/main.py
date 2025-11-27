"""
FastAPI application for CourseCompass
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from config import initialize_dspy, COURSES_FILE
from indexer import build_course_index
from graph_builder import build_official_course_graph  
from graph_builder import load_official_prereqs

from path_planner import (
    find_study_path,
    get_direct_prerequisites,
)
from explainer import explain_study_path


# -------- Global state --------
courses_data = None          # List[Dict[str, Any]]
vectorstore = None           # FAISS / LangChain vector store
course_graph = None          # Official prerequisite graph (NetworkX DiGraph)
official_prereqs = None      # Dict[str, List[str]]


# -------- Helpers --------
def load_official_prereqs(path: str) -> Dict[str, List[str]]:
    """
    Load prerequisites_official.jsonl into a mapping:
        { course_code: [prereq_code1, prereq_code2, ...] }
    """
    import json

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize on startup:
    - Initialize DSPy (if needed elsewhere)
    - Build course index (FAISS + documents)
    - Load official prerequisites file
    - Build official prerequisite graph (no LLM calls)
    """
    global courses_data, vectorstore, course_graph, official_prereqs

    print("🚀 Initializing CourseCompass...")

    # 1) (Optional) DSPy init – harmless to keep even if not used directly here
    initialize_dspy()

    # 2) Build vector index over all courses (for /v1/search)
    print("📚 Loading courses and building vector index...")
    courses_data, vectorstore = build_course_index()

    # 3) Load official prerequisites extracted by precompute_prereqs_official.py
    # Adjust this path if you keep the file somewhere else.
    prereq_file = "data/prerequisites_official.jsonl"
    print(f"📄 Loading official prerequisites from {prereq_file}...")
    official_prereqs = load_official_prereqs(prereq_file)

    # 4) Build the official course dependency graph (no LLM)
    print("🧠 Building official course dependency graph...")
    course_graph = build_official_course_graph(courses_data, official_prereqs)

    print("\n✅ CourseCompass ready!")
    yield


app = FastAPI(
    title="CourseCompass",
    description="Intelligent Course Planning System",
    version="1.0.0",
    lifespan=lifespan,
)


# -------- Pydantic models --------
class CourseInfo(BaseModel):
    course_code: str
    title: str
    ects: int = 0


class PathRequest(BaseModel):
    target_course: str
    completed_courses: List[str] = []


class PathResponse(BaseModel):
    target_course: str
    path: List[CourseInfo]
    explanation: str
    total_ects: int


# -------- Endpoints --------
@app.get("/")
def root():
    return {
        "name": "CourseCompass",
        "version": "1.0.0",
        "endpoints": [
            "/v1/analyze-prerequisites/{course_code}",
            "/v1/generate-path",
            "/v1/search",
            "/v1/health",
        ],
    }


@app.get("/v1/health")
def health():
    if courses_data is None or course_graph is None:
        return {
            "status": "initializing",
            "courses": 0,
            "graph_nodes": 0,
            "graph_edges": 0,
        }

    return {
        "status": "healthy",
        "courses": len(courses_data),
        "graph_nodes": course_graph.number_of_nodes(),
        "graph_edges": course_graph.number_of_edges(),
    }


@app.get("/v1/analyze-prerequisites/{course_code}")
def analyze_prerequisites(course_code: str):
    """
    Get direct prerequisites for a course (from the official graph).
    """

    if course_graph is None or course_code not in course_graph:
        raise HTTPException(status_code=404, detail=f"Course {course_code} not found")

    prereqs = get_direct_prerequisites(course_graph, course_code)

    return {
        "course_code": course_code,
        "title": course_graph.nodes[course_code].get("title", ""),
        "prerequisites": prereqs,
    }


@app.post("/v1/generate-path", response_model=PathResponse)
def generate_path(request: PathRequest):
    """
    Generate a study path to the target course based on the official prerequisite graph.
    """

    if course_graph is None or request.target_course not in course_graph:
        raise HTTPException(
            status_code=404,
            detail=f"Course {request.target_course} not found",
        )

    path = find_study_path(
        course_graph,
        request.target_course,
        request.completed_courses,
    )

    if not path:
        raise HTTPException(status_code=404, detail="No path found")

    # Build response path info
    path_courses: List[CourseInfo] = []
    total_ects = 0

    for course_code in path:
        node: Dict[str, Any] = course_graph.nodes[course_code]
        ects = node.get("ects", 0)
        path_courses.append(
            CourseInfo(
                course_code=course_code,
                title=node.get("title", ""),
                ects=ects,
            )
        )
        total_ects += ects

    # LLM-based natural language explanation (same as before)
    explanation = explain_study_path(path, course_graph)

    return PathResponse(
        target_course=request.target_course,
        path=path_courses,
        explanation=explanation,
        total_ects=total_ects,
    )


@app.get("/v1/search")
def search_courses(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
):
    """
    Search courses by semantic query using the FAISS vector store.
    """

    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    results = vectorstore.similarity_search(query, k=top_k)

    courses = []
    for doc in results:
        courses.append(
            {
                "course_code": doc.metadata["course_code"],
                "title": doc.metadata["title"],
                "responsible": doc.metadata.get("responsible", ""),
                "ects": doc.metadata.get("ects", 0),
            }
        )

    return {
        "query": query,
        "results": courses,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
