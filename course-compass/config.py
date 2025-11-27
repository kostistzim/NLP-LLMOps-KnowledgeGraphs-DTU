"""
Configuration for CourseCompass.

- Sets up CampusAI LLM for both LangChain and DSPy.
- Defines common file paths (courses JSONL, official prerequisites).
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import dspy

# ---------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------

# Load env from ~/.env (where your CampusAI keys live)
load_dotenv(os.path.expanduser("~/.env"))

# ---------------------------------------------------------------------
# Data file paths
# ---------------------------------------------------------------------

# Main DTU courses catalogue (JSONL)
COURSES_FILE = os.getenv("COURSES_FILE", "data/dtu_courses.jsonl")

# Official prerequisites JSONL produced by precompute_prereqs_official.py
OFFICIAL_PREREQS_FILE = os.getenv(
    "OFFICIAL_PREREQS_FILE", "data/prerequisites_official.jsonl"
)

# Embedding model used by indexer.py
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/distiluse-base-multilingual-cased-v2",
)

# ---------------------------------------------------------------------
# CampusAI configuration (OpenAI-compatible API)
# ---------------------------------------------------------------------

CAMPUSAI_API_KEY = os.getenv("CAMPUSAI_API_KEY")
CAMPUSAI_API_BASE = os.getenv(
    "CAMPUSAI_API_BASE",
    # IMPORTANT: this is the *chat* endpoint with /api/v1, from CampusAI docs
    "https://chat.campusai.compute.dtu.dk/api/v1",
)
CAMPUSAI_MODEL = os.getenv("CAMPUSAI_MODEL", "gpt-oss")


def get_langchain_llm(temperature: float = 0.2) -> ChatOpenAI:
    """
    LangChain ChatOpenAI client pointed at CampusAI.
    Used by explainer.py (LLM explanations).
    """
    if not CAMPUSAI_API_KEY:
        raise RuntimeError("CAMPUSAI_API_KEY is not set in ~/.env")

    return ChatOpenAI(
        model=CAMPUSAI_MODEL,
        api_key=CAMPUSAI_API_KEY,
        base_url=CAMPUSAI_API_BASE,
        temperature=temperature,
    )


def initialize_dspy() -> None:
    """
    Configure DSPy to use CampusAI as an OpenAI-compatible backend.
    This is what your FastAPI app uses in main.py.
    """
    if not CAMPUSAI_API_KEY:
        raise RuntimeError("CAMPUSAI_API_KEY is not set in ~/.env")

    # Generic LM wrapper for OpenAI-compatible backends
    lm = dspy.LM(
        model=f"openai/{CAMPUSAI_MODEL}",  # e.g. "openai/gpt-oss"
        api_key=CAMPUSAI_API_KEY,
        api_base=CAMPUSAI_API_BASE,
    )

    dspy.configure(lm=lm)
    print(f"DSPy configured with CampusAI model: {CAMPUSAI_MODEL}")


# ---------------------------------------------------------------------
# Simple smoke test (optional: python config.py)
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("Testing CampusAI configuration...")

    # Test LangChain
    llm = get_langchain_llm()
    response = llm.invoke("Say 'LangChain works!'")
    print("LangChain response:", response.content)

    # Test DSPy
    initialize_dspy()

    class SimpleEcho(dspy.Signature):
        question: str = dspy.InputField()
        answer: str = dspy.OutputField()

    predictor = dspy.Predict(SimpleEcho)
    result = predictor(question="Say 'DSPy works!'")
    print("DSPy response:", result.answer)
