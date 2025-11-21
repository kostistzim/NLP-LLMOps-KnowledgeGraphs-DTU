"""
FastAPI application for PDF to sentences extraction
"""
import uvicorn

import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from pdf_processor import extract_text_from_pdf
from sentence_extractor import extract_sentences


app = FastAPI(
    title="PDF to Sentences API",
    description="Extract sentences from PDF files using GROBID and spaCy",
    version="1.0.0"
)


class SentencesResponse(BaseModel):
    """Response model with list of sentences"""
    sentences: List[str]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "PDF to Sentences API",
        "version": "1.0.0",
        "endpoint": "/v1/extract-sentences"
    }


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/v1/extract-sentences", response_model=SentencesResponse)
async def extract_sentences_endpoint(pdf_file: UploadFile = File(...)):
    """
    Extract sentences from uploaded PDF
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        JSON with list of sentences
    """
    # Validate file type
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file to temporary location
    temp_path = save_temp_file(pdf_file)
    
    # Extract text from PDF using GROBID
    grobid_url = os.getenv("GROBID_URL", "http://localhost:8070")
    text = extract_text_from_pdf(temp_path, grobid_url)
    
    # Extract sentences using spaCy
    sentences = extract_sentences(text)
    
    # Clean up temp file
    os.remove(temp_path)
    
    return {"sentences": sentences}


def save_temp_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to temporary location
    
    Args:
        upload_file: FastAPI UploadFile object
        
    Returns:
        Path to saved temporary file
    """
    # Create temporary file
    suffix = os.path.splitext(upload_file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        # Write uploaded content to temp file
        content = upload_file.file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    return temp_path


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)