"""
Extract prerequisite concepts from course learning objectives
Uses DSPy for optimized prompt-based extraction
"""

import dspy
from typing import List, Dict
from config import initialize_dspy


class PrerequisiteExtractor(dspy.Signature):
    """
    Extract prerequisite knowledge/skills from course learning objectives
    
    Identifies concepts students need to know BEFORE taking the course
    """
    course_title = dspy.InputField(desc="Course title")
    learning_objectives = dspy.InputField(desc="List of learning objectives")
    prerequisites = dspy.OutputField(desc="List of prerequisite concepts (3-7 items)")


class ConceptExtractor(dspy.Module):
    """
    DSPy module for extracting prerequisites with examples
    """
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(PrerequisiteExtractor)
    
    def forward(self, course_title: str, learning_objectives: List[str]) -> List[str]:
        """
        Extract prerequisite concepts
        
        Args:
            course_title: Course name
            learning_objectives: List of objective strings
            
        Returns:
            List of prerequisite concept strings
        """
        # Join objectives into text
        objectives_text = "\n".join(f"- {obj}" for obj in learning_objectives)
        
        # Call DSPy
        result = self.extract(
            course_title=course_title,
            learning_objectives=objectives_text
        )
        
        # Parse result (DSPy might return string or list)
        prerequisites = result.prerequisites
        
        if isinstance(prerequisites, str):
            # If string, split by newlines or commas
            if '\n' in prerequisites:
                prerequisites = [p.strip('- ').strip() for p in prerequisites.split('\n') if p.strip()]
            else:
                prerequisites = [p.strip() for p in prerequisites.split(',') if p.strip()]
        
        # Clean up
        prerequisites = [p for p in prerequisites if p and len(p) > 3]
        
        return prerequisites[:7]  # Max 7 concepts


def extract_prerequisites(course: Dict, extractor: ConceptExtractor = None) -> List[str]:
    """
    Extract prerequisites from a course dictionary
    
    Args:
        course: Course dict with 'title' and 'learning_objectives'
        extractor: Optional pre-initialized extractor
        
    Returns:
        List of prerequisite concept strings
    """
    if extractor is None:
        extractor = ConceptExtractor()
    
    title = course.get('title', '')
    objectives = course.get('learning_objectives', [])
    
    if not objectives:
        return []
    
    prerequisites = extractor.forward(title, objectives)
    return prerequisites


def extract_prerequisites_batch(courses: List[Dict]) -> Dict[str, List[str]]:
    """
    Extract prerequisites for multiple courses efficiently
    
    Args:
        courses: List of course dictionaries
        
    Returns:
        Dict mapping course_code -> list of prerequisites
    """
    extractor = ConceptExtractor()  # Reuse same extractor
    results = {}
    
    for i, course in enumerate(courses, 1):
        course_code = course.get('course_code', 'unknown')
        print(f"Extracting prerequisites for {course_code} ({i}/{len(courses)})...")
        
        prerequisites = extract_prerequisites(course, extractor)
        results[course_code] = prerequisites
        
        if prerequisites:
            print(f"  ✓ Found: {', '.join(prerequisites[:3])}" + 
                  (f" (+{len(prerequisites)-3} more)" if len(prerequisites) > 3 else ""))
        else:
            print(f"  ⚠️  No prerequisites extracted")
    
    return results


if __name__ == "__main__":
    # Initialize DSPy
    initialize_dspy()
    
    print("Testing prerequisite extraction...\n")
    
    # Test with example courses
    test_courses = [
        {
            "course_code": "02460",
            "title": "Advanced Machine Learning",
            "learning_objectives": [
                "Apply advanced optimization techniques for machine learning",
                "Implement deep neural networks and convolutional architectures",
                "Understand and apply probabilistic graphical models",
                "Evaluate model performance using cross-validation"
            ]
        },
        {
            "course_code": "02450",
            "title": "Introduction to Machine Learning and Data Mining",
            "learning_objectives": [
                "Understand basic machine learning concepts",
                "Apply supervised learning algorithms",
                "Perform data preprocessing and feature engineering",
                "Evaluate and compare different models"
            ]
        }
    ]
    
    # Extract prerequisites
    extractor = ConceptExtractor()
    
    for course in test_courses:
        print(f"\n{'='*60}")
        print(f"Course: {course['course_code']} - {course['title']}")
        print(f"{'='*60}")
        
        print("\nLearning Objectives:")
        for obj in course['learning_objectives']:
            print(f"  - {obj}")
        
        prerequisites = extract_prerequisites(course, extractor)
        
        print(f"\n✨ Extracted Prerequisites ({len(prerequisites)}):")
        for prereq in prerequisites:
            print(f"  → {prereq}")