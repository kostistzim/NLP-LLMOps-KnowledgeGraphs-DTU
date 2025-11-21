"""
FastAPI application for DTU course information retrieval
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

from indexer import build_all_indices
from retriever import CourseRetriever, ObjectiveRetriever


# Global retrievers
course_retriever = None
objective_retriever = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build indices on startup"""
    global course_retriever, objective_retriever
    
    print("Building indices on startup...")
    indices = build_all_indices()
    
    course_retriever = CourseRetriever(indices['course_index'])
    objective_retriever = ObjectiveRetriever(indices['objective_index'])
    
    print("✅ Indices ready!")
    yield


app = FastAPI(
    title="DTU Course Information Retrieval API",
    description="Search DTU courses using sparse, dense, or hybrid retrieval",
    version="1.0.0",
    lifespan=lifespan
)


class CourseResult(BaseModel):
    """Course search result"""
    course_id: str
    title: str
    score: float


class ObjectiveResult(BaseModel):
    """Objective search result"""
    course_id: str
    title: str
    objective: str
    score: float


class SimilarCoursesResponse(BaseModel):
    """Response for similar courses endpoint"""
    query_course_id: str
    results: List[CourseResult]
    mode: str
    top_k: int


class SearchCoursesResponse(BaseModel):
    """Response for course search endpoint"""
    query: str
    results: List[CourseResult]
    mode: str


class SearchObjectivesResponse(BaseModel):
    """Response for objective search endpoint"""
    query: str
    results: List[ObjectiveResult]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "DTU Course Information Retrieval API",
        "version": "1.0.0",
        "endpoints": [
            "/v1/courses/{course_id}/similar",
            "/v1/search",
            "/v1/objectives/search",
            "/v1/health"
        ]
    }


@app.get("/v1/health")
def health():
    """Health check with index stats"""
    return {
        "status": "ok",
        "index_sizes": {
            "courses": len(course_retriever.course_ids),
            "objectives": len(objective_retriever.texts)
        }
    }


@app.get("/v1/courses/{course_id}/similar", response_model=SimilarCoursesResponse)
def similar_courses(
    course_id: str,
    top_k: int = Query(10, ge=1, le=50),
    mode: str = Query("dense", regex="^(sparse|dense|hybrid)$"),
    alpha: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Find courses similar to given course
    
    Args:
        course_id: Source course ID (e.g., "02451")
        top_k: Number of results (1-50)
        mode: Retrieval mode (sparse/dense/hybrid)
        alpha: Hybrid weight (alpha*dense + (1-alpha)*sparse)
    """
    if course_id not in course_retriever.course_ids:
        raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")
    
    results = course_retriever.find_similar(
        course_id=course_id,
        mode=mode,
        top_k=top_k,
        alpha=alpha
    )
    
    return {
        "query_course_id": course_id,
        "results": results,
        "mode": mode,
        "top_k": top_k
    }


@app.get("/v1/search", response_model=SearchCoursesResponse)
def search_courses(
    query: str = Query(..., min_length=1),
    top_k: int = Query(10, ge=1, le=50),
    mode: str = Query("dense", regex="^(sparse|dense|hybrid)$"),
    alpha: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Search courses by free text query
    
    Args:
        query: Search query (e.g., "machine learning")
        top_k: Number of results (1-50)
        mode: Retrieval mode (sparse/dense/hybrid)
        alpha: Hybrid weight
    """
    results = course_retriever.search(
        query=query,
        mode=mode,
        top_k=top_k,
        alpha=alpha
    )
    
    return {
        "query": query,
        "results": results,
        "mode": mode
    }


@app.get("/v1/objectives/search", response_model=SearchObjectivesResponse)
def search_objectives(
    query: str = Query(..., min_length=1),
    top_k: int = Query(10, ge=1, le=50),
    mode: str = Query("dense", regex="^(sparse|dense|hybrid)$"),
    alpha: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Search learning objectives by free text query
    
    Args:
        query: Search query (e.g., "dimensionality reduction")
        top_k: Number of results (1-50)
        mode: Retrieval mode (sparse/dense/hybrid)
        alpha: Hybrid weight
    """
    results = objective_retriever.search(
        query=query,
        mode=mode,
        top_k=top_k,
        alpha=alpha
    )
    
    return {
        "query": query,
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)