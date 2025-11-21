"""
FastAPI application for DTU course RAG system
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

from indexer import build_all_indices
from retriever import CourseRetriever
from rag import initialize_dspy, answer_question


# Global retriever
course_retriever = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build indices and initialize DSPy on startup"""
    global course_retriever
    
    print("Building indices on startup...")
    indices = build_all_indices()
    course_retriever = CourseRetriever(indices)
    
    print("Initializing DSPy...")
    initialize_dspy()
    
    print("✅ System ready!")
    yield


app = FastAPI(
    title="DTU Course RAG System",
    description="Search DTU courses and ask questions with RAG",
    version="1.0.0",
    lifespan=lifespan
)


class CourseResult(BaseModel):
    """Course search result"""
    course_code: str
    title: str
    score: float


class SearchResponse(BaseModel):
    """Response for search endpoint"""
    query: str
    mode: str
    results: List[CourseResult]


class RetrievedCourse(BaseModel):
    """Retrieved course in RAG response"""
    course_code: str
    title: str


class AskResponse(BaseModel):
    """Response for ask endpoint"""
    query: str
    answer: str
    retrieved_courses: List[RetrievedCourse]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "DTU Course RAG System",
        "version": "1.0.0",
        "endpoints": [
            "/v1/search",
            "/v1/ask",
            "/v1/health"
        ]
    }


@app.get("/v1/health")
def health():
    """Health check"""
    return {
        "status": "ok",
        "index_size": len(course_retriever.course_codes)
    }


@app.get("/v1/search", response_model=SearchResponse)
def search_courses(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    mode: str = Query("dense", regex="^(sparse|dense|hybrid)$"),
    alpha: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Search courses by query
    
    Args:
        query: Search text
        top_k: Number of results (1-20)
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
        "mode": mode,
        "results": results
    }


@app.get("/v1/ask", response_model=AskResponse)
def ask_question(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=10),
    mode: str = Query("dense", regex="^(sparse|dense|hybrid)$"),
    alpha: float = Query(0.5, ge=0.0, le=1.0)
):
    """
    Ask natural language question about courses (RAG)
    
    Args:
        query: Natural language question
        top_k: Number of courses to retrieve
        mode: Retrieval mode
        alpha: Hybrid weight
    """
    # Retrieve relevant courses
    courses = course_retriever.search(
        query=query,
        mode=mode,
        top_k=top_k,
        alpha=alpha
    )
    
    if not courses:
        raise HTTPException(status_code=404, detail="No relevant courses found")
    
    # Generate answer with RAG
    result = answer_question(query, courses)
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)