"""
FastAPI application for person name extraction using LLM
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Load environment variables from ~/.env
load_dotenv(os.path.expanduser("~/.env"))

from campusai_client import campusai_extract_persons


app = FastAPI(
    title="Person Name Extraction API",
    description="Extract person names from text using CampusAI LLM",
    version="1.0.0"
)


class TextInput(BaseModel):
    """Input model for text"""
    text: str


class PersonsResponse(BaseModel):
    """Response model with list of person names"""
    persons: List[str]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Person Name Extraction API",
        "version": "1.0.0",
        "endpoint": "/v1/extract-persons"
    }


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/v1/extract-persons", response_model=PersonsResponse)
def extract_persons(input_data: TextInput):
    """
    Extract person names from text
    
    Args:
        input_data: JSON with 'text' field
        
    Returns:
        JSON with 'persons' field containing list of names
    """
    if not os.getenv("CAMPUSAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="CAMPUSAI_API_KEY not configured"
        )
    
    persons = campusai_extract_persons(input_data.text)
    return {"persons": persons}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)