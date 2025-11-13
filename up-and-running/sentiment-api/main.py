"""
FastAPI Sentiment Analysis Service for Course Evaluations
Supports Danish and English text with advanced sentiment scoring
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sentiment_analyzer import SentimentAnalyzer

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Course Evaluation Sentiment API",
    description="""
    Sentiment analysis API for Danish and English course evaluations.
    
    ## Features
    - Automatic language detection (Danish/English)
    - Advanced sentiment scoring (-5 to 5)
    - Handles negations ("not good", "ikke god")
    - Handles intensifiers ("very", "meget")
    - Multi-word sentiment analysis
    
    ## Scoring Scale
    - **5**: Very positive (e.g., "Fantastisk kursus!")
    - **3**: Positive (e.g., "Det var en god lærer")
    - **0**: Neutral (e.g., "Kurset var okay")
    - **-3**: Negative (e.g., "It was a bad course")
    - **-5**: Very negative (e.g., "Forfærdelig!")
    """,
    version="1.0.0",
    contact={
        "name": "DTU NLP Course Project",
    },
)

# Initialize sentiment analyzer
analyzer = SentimentAnalyzer()


class TextInput(BaseModel):
    """Input model for sentiment analysis"""
    text: str = Field(
        ...,
        description="Course evaluation text in Danish or English",
        example="Det var en god lærer."
    )


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis"""
    score: int = Field(
        ...,
        description="Sentiment score from -5 (very negative) to 5 (very positive)",
        ge=-5,
        le=5,
        example=3
    )


class DetailedSentimentResponse(BaseModel):
    """Detailed response with language information"""
    score: int = Field(..., description="Sentiment score", ge=-5, le=5)
    language: str = Field(..., description="Detected language (da/en)")
    text: str = Field(..., description="Input text")


@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "name": "Course Evaluation Sentiment API",
        "version": "1.0.0",
        "endpoints": {
            "/v1/sentiment": "POST - Analyze sentiment (returns score only)",
            "/v1/sentiment/detailed": "POST - Analyze sentiment (returns score + details)",
            "/health": "GET - Health check",
            "/docs": "GET - Swagger documentation"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sentiment-api",
        "version": "1.0.0"
    }


@app.post("/v1/sentiment", response_model=SentimentResponse)
def analyze_sentiment(input_data: TextInput):
    """
    Analyze sentiment of course evaluation text
    
    Returns only the sentiment score as required by the assignment.
    
    - **text**: Course evaluation text in Danish or English
    
    Returns:
    - **score**: Integer from -5 to 5
    """
    try:
        score = analyzer.analyze(input_data.text)
        return {"score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.post("/v1/sentiment/detailed", response_model=DetailedSentimentResponse)
def analyze_sentiment_detailed(input_data: TextInput):
    """
    Analyze sentiment with detailed information
    
    Returns sentiment score along with detected language and original text.
    
    - **text**: Course evaluation text in Danish or English
    
    Returns:
    - **score**: Integer from -5 to 5
    - **language**: Detected language code (da/en)
    - **text**: Original input text
    """
    try:
        result = analyzer.analyze_detailed(input_data.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
