"""
Generate natural language explanations for study paths
Uses LangChain for prompt chaining
"""

from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain
import networkx as nx

from config import get_langchain_llm


def explain_prerequisite(
    prereq_course: Dict,
    target_course: Dict,
    concepts: List[str]
) -> str:
    """
    Explain why one course is prerequisite for another
    
    Args:
        prereq_course: Prerequisite course info
        target_course: Target course info
        concepts: Concepts that link them
        
    Returns:
        Natural language explanation
    """
    llm = get_langchain_llm(temperature=0.3)
    
    prompt = PromptTemplate(
        input_variables=["prereq_title", "target_title", "concepts"],
        template="""Explain in 2-3 sentences why a student should take "{prereq_title}" before "{target_title}".

The prerequisite course teaches: {concepts}

Provide a clear, helpful explanation for a student planning their courses."""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    result = chain.run(
        prereq_title=prereq_course['title'],
        target_title=target_course['title'],
        concepts=", ".join(concepts)
    )
    
    return result.strip()


def explain_study_path(
    path: List[str],
    graph: nx.DiGraph
) -> str:
    """
    Explain complete study path
    
    Args:
        path: Ordered list of course codes
        graph: Course dependency graph
        
    Returns:
        Natural language explanation of the path
    """
    llm = get_langchain_llm(temperature=0.3)
    
    # Build path description
    path_description = []
    for i, course_code in enumerate(path, 1):
        title = graph.nodes[course_code].get('title', course_code)
        ects = graph.nodes[course_code].get('ects', 0)
        path_description.append(f"{i}. {course_code} - {title} ({ects} ECTS)")
    
    prompt = PromptTemplate(
        input_variables=["path", "target"],
        template="""Generate a helpful study plan explanation for a DTU student.

Study path to reach {target}:
{path}

Provide:
1. Brief overview of the learning progression
2. Why the sequence makes sense
3. Estimated timeline

Keep it concise (3-4 sentences) and encouraging."""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    result = chain.run(
        path="\n".join(path_description),
        target=path[-1] if path else "target course"
    )
    
    return result.strip()


if __name__ == "__main__":
    from config import initialize_dspy
    
    initialize_dspy()
    
    print("Testing Explainer\n")
    print("="*60)
    
    # Test prerequisite explanation
    prereq = {
        "course_code": "02450",
        "title": "Introduction to Machine Learning"
    }
    
    target = {
        "course_code": "02460",
        "title": "Advanced Machine Learning"
    }
    
    concepts = ["optimization theory", "neural networks", "model evaluation"]
    
    print("Test 1: Prerequisite Explanation")
    print(f"Why take {prereq['title']} before {target['title']}?\n")
    
    explanation = explain_prerequisite(prereq, target, concepts)
    print(explanation)