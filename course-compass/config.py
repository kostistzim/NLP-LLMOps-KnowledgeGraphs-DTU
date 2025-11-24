"""
Configuration for CourseCompass
Sets up CampusAI LLM for both LangChain and DSPy
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  
import dspy

# Load environment variables
load_dotenv(os.path.expanduser("~/.env"))

# CampusAI configuration
CAMPUSAI_API_KEY = os.getenv("CAMPUSAI_API_KEY")
CAMPUSAI_API_BASE = "https://campusai.compute.dtu.dk/api/v1"
CAMPUSAI_MODEL = "Qwen3"

if not CAMPUSAI_API_KEY:
    raise ValueError("CAMPUSAI_API_KEY not found in ~/.env file")


def get_langchain_llm(temperature: float = 0.0) -> ChatOpenAI:
    """
    Get LangChain LLM configured for CampusAI
    
    Args:
        temperature: 0.0 = deterministic, 1.0 = creative
        
    Returns:
        ChatOpenAI instance configured for CampusAI
    """
    return ChatOpenAI(
        model=CAMPUSAI_MODEL,
        openai_api_key=CAMPUSAI_API_KEY,
        openai_api_base=CAMPUSAI_API_BASE,
        temperature=temperature
    )


def initialize_dspy():
    """
    Initialize DSPy with CampusAI configuration
    Call this once at startup
    """
    lm = dspy.LM(
        model=f"openai/{CAMPUSAI_MODEL}",
        api_key=CAMPUSAI_API_KEY,
        api_base=CAMPUSAI_API_BASE
    )
    dspy.configure(lm=lm)
    print(f"✅ DSPy configured with CampusAI model: {CAMPUSAI_MODEL}")


# Embedding model for vector search
EMBEDDING_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v2"

# Data paths
DATA_DIR = "data"
COURSES_FILE = os.path.join(DATA_DIR, "dtu_courses.jsonl")


if __name__ == "__main__":
    # Test configuration
    print("Testing CampusAI configuration...")
    
    # Test LangChain
    llm = get_langchain_llm()
    response = llm.invoke("Say 'LangChain works!'")
    print(f"✅ LangChain: {response.content}")
    
    # Test DSPy
    initialize_dspy()
    predictor = dspy.Predict("question -> answer")
    result = predictor(question="Say 'DSPy works!'")
    print(f"✅ DSPy: {result.answer}")