"""
FastAPI application for CourseCompass
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
import networkx as nx

from config import initialize_dspy, COURSES_FILE
from indexer import build_course_index
from graph_builder import build_course_graph
from path_planner import find_study_path, get_direct_prerequisites, generate_study_plan
from explainer import explain_study_path

# Global state
courses_data = None
vectorstore = None
course_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup"""
    global courses_data, vectorstore, course_graph
    
    print("Initializing CourseCompass...")
    
    initialize_dspy()
    courses_data, vectorstore = build_course_index()
    
    print("\nBuilding course dependency graph...")
    course_graph = build_course_graph(courses_data, vectorstore)
    
    print("\n✅ CourseCompass ready!")
    yield


app = FastAPI(
    title="CourseCompass",
    description="Intelligent Course Planning System",
    version="1.0.0",
    lifespan=lifespan
)


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


@app.get("/")
def root():
    return {
        "name": "CourseCompass",
        "version": "1.0.0",
        "endpoints": [
            "/v1/analyze-prerequisites",
            "/v1/generate-path",
            "/v1/search",
            "/v1/health"
        ]
    }


@app.get("/v1/health")
def health():
    return {
        "status": "healthy",
        "courses": len(courses_data),
        "graph_nodes": course_graph.number_of_nodes(),
        "graph_edges": course_graph.number_of_edges()
    }


@app.get("/v1/analyze-prerequisites/{course_code}")
def analyze_prerequisites(course_code: str):
    """Get direct prerequisites for a course"""
    
    if course_code not in course_graph:
        raise HTTPException(status_code=404, detail=f"Course {course_code} not found")
    
    prereqs = get_direct_prerequisites(course_graph, course_code)
    
    return {
        "course_code": course_code,
        "title": course_graph.nodes[course_code].get('title', ''),
        "prerequisites": prereqs
    }


@app.post("/v1/generate-path", response_model=PathResponse)
def generate_path(request: PathRequest):
    """Generate study path to target course"""
    
    if request.target_course not in course_graph:
        raise HTTPException(status_code=404, detail=f"Course {request.target_course} not found")
    
    path = find_study_path(
        course_graph,
        request.target_course,
        request.completed_courses
    )
    
    if not path:
        raise HTTPException(status_code=404, detail="No path found")
    
    # Build response
    path_courses = []
    total_ects = 0
    
    for course_code in path:
        node = course_graph.nodes[course_code]
        ects = node.get('ects', 0)
        path_courses.append(CourseInfo(
            course_code=course_code,
            title=node.get('title', ''),
            ects=ects
        ))
        total_ects += ects
    
    # Generate explanation
    explanation = explain_study_path(path, course_graph)
    
    return PathResponse(
        target_course=request.target_course,
        path=path_courses,
        explanation=explanation,
        total_ects=total_ects
    )


@app.get("/v1/search")
def search_courses(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20)
):
    """Search courses by semantic query"""
    
    results = vectorstore.similarity_search(query, k=top_k)
    
    courses = []
    for doc in results:
        courses.append({
            "course_code": doc.metadata['course_code'],
            "title": doc.metadata['title'],
            "responsible": doc.metadata.get('responsible', ''),
            "ects": doc.metadata.get('ects', 0)
        })
    
    return {
        "query": query,
        "results": courses
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)