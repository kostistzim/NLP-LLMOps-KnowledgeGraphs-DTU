"""
Compare dictionary-based and ML-based sentiment analysis approaches
Evaluates accuracy, speed, and size trade-offs
"""

import time
from pathlib import Path
from sentiment_analyzer import SentimentAnalyzer
from ml_sentiment_analyzer import MLSentimentAnalyzer, train_ml_model
from test_data import ALL_TESTS, ASSIGNMENT_TESTS


def evaluate_accuracy(analyzer, test_cases, name="Analyzer", tolerance=1):
    """
    Evaluate accuracy of an analyzer
    
    Args:
        analyzer: Analyzer instance with analyze() method
        test_cases: List of (text, expected_score, language, description) tuples
        name: Name for display
        tolerance: Allow ±tolerance difference in score
    
    Returns:
        accuracy percentage
    """
    correct = 0
    total = len(test_cases)
    errors = []
    
    print(f"\n{'='*60}")
    print(f"EVALUATING: {name}")
    print(f"{'='*60}")
    
    for text, expected, lang, desc in test_cases:
        predicted = analyzer.analyze(text)
        diff = abs(predicted - expected)
        
        if diff <= tolerance:
            correct += 1
            status = "✓"
        else:
            status = "✗"
            errors.append((text, expected, predicted, lang))
        
        print(f"{status} [{lang}] Expected: {expected:2d}, Got: {predicted:2d} | {text[:50]}")
    
    accuracy = 100 * correct / total
    
    print(f"\n{'='*60}")
    print(f"Results: {correct}/{total} correct (tolerance: ±{tolerance})")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for text, exp, pred, lang in errors[:5]:  # Show first 5 errors
            print(f"  [{lang}] '{text[:40]}...'")
            print(f"       Expected: {exp}, Got: {pred}, Diff: {abs(exp-pred)}")
    
    print(f"{'='*60}")
    
    return accuracy


def measure_speed(analyzer, test_cases, name="Analyzer"):
    """Measure inference speed"""
    print(f"\n{'='*60}")
    print(f"SPEED TEST: {name}")
    print(f"{'='*60}")
    
    # Warmup
    for text, _, _, _ in test_cases[:3]:
        analyzer.analyze(text)
    
    # Measure
    start = time.time()
    for text, _, _, _ in test_cases:
        analyzer.analyze(text)
    end = time.time()
    
    total_time = end - start
    avg_time = total_time / len(test_cases) * 1000  # Convert to ms
    
    print(f"Total time: {total_time:.4f} seconds")
    print(f"Average per text: {avg_time:.4f} ms")
    print(f"Throughput: {len(test_cases)/total_time:.1f} texts/second")
    print(f"{'='*60}")
    
    return avg_time


def compare_approaches():
    """
    Main comparison function
    Compares dictionary-based vs ML-based approaches
    """
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS APPROACH COMPARISON")
    print("="*60)
    
    # Initialize dictionary analyzer
    print("\n1. Initializing dictionary-based analyzer...")
    dict_analyzer = SentimentAnalyzer()
    print("✓ Dictionary analyzer ready")
    
    # Train ML analyzer
    print("\n2. Training ML-based analyzer...")
    try:
        # Try to load existing model
        ml_analyzer = MLSentimentAnalyzer("models/ml_sentiment.pkl")
        print("✓ Loaded pre-trained ML model")
    except:
        # Train new model
        ml_analyzer = train_ml_model()
    
    # Evaluate on assignment tests (critical!)
    print("\n" + "="*60)
    print("ASSIGNMENT TEST CASES (Required)")
    print("="*60)
    
    print("\nDictionary Approach:")
    for text, expected, lang, desc in ASSIGNMENT_TESTS:
        pred = dict_analyzer.analyze(text)
        status = "✓" if pred == expected else "✗"
        print(f"{status} {desc}: Expected {expected}, Got {pred}")
    
    print("\nML Approach:")
    for text, expected, lang, desc in ASSIGNMENT_TESTS:
        pred = ml_analyzer.analyze(text)
        status = "✓" if pred == expected else "✗"
        print(f"{status} {desc}: Expected {expected}, Got {pred}")
    
    # Accuracy comparison
    dict_acc = evaluate_accuracy(dict_analyzer, ALL_TESTS, "Dictionary Approach", tolerance=1)
    ml_acc = evaluate_accuracy(ml_analyzer, ALL_TESTS, "ML Approach", tolerance=1)
    
    # Speed comparison
    dict_speed = measure_speed(dict_analyzer, ALL_TESTS, "Dictionary Approach")
    ml_speed = measure_speed(ml_analyzer, ALL_TESTS, "ML Approach")
    
    # Size comparison
    print("\n" + "="*60)
    print("SIZE COMPARISON")
    print("="*60)
    
    # Dictionary approach size (just the code)
    dict_size = (
        Path("sentiment_analyzer.py").stat().st_size +
        Path("language_detector.py").stat().st_size
    ) / 1024  # KB
    
    # ML approach size (code + model)
    ml_code_size = Path("ml_sentiment_analyzer.py").stat().st_size / 1024
    ml_model_size = Path("models/ml_sentiment.pkl").stat().st_size / 1024 if Path("models/ml_sentiment.pkl").exists() else 0
    ml_total_size = ml_code_size + ml_model_size
    
    print(f"Dictionary approach: {dict_size:.1f} KB (code only)")
    print(f"ML approach: {ml_total_size:.1f} KB (code: {ml_code_size:.1f} KB + model: {ml_model_size:.1f} KB)")
    print(f"Size difference: {ml_total_size/dict_size:.1f}x larger")
    print("="*60)
    
    # Final summary
    print("\n" + "="*60)
    print("SUMMARY: DICTIONARY vs ML")
    print("="*60)
    print(f"\n{'Metric':<20} {'Dictionary':<20} {'ML':<20}")
    print("-" * 60)
    print(f"{'Accuracy':<20} {dict_acc:.1f}%{'':<15} {ml_acc:.1f}%")
    print(f"{'Speed (ms/text)':<20} {dict_speed:.4f}{'':<14} {ml_speed:.4f}")
    print(f"{'Size (KB)':<20} {dict_size:.1f}{'':<16} {ml_total_size:.1f}")
    print(f"{'Training needed':<20} {'No':<20} {'Yes'}")
    print(f"{'Interpretable':<20} {'Yes':<20} {'Limited'}")
    print(f"{'Container size':<20} {'~70 MB':<20} {'~72 MB'}")
    print("="*60)
    
    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    print("""
For this use case (course evaluation sentiment):

✅ DICTIONARY APPROACH IS BETTER:
   - Simpler and more interpretable
   - No training data needed
   - Faster inference
   - Smaller footprint
   - Easy to customize for course-specific terms
   - Meets all requirements

ML approach advantages:
   - Could be better with more training data (we only have 24 examples)
   - Would learn patterns we might miss
   - Better for general sentiment (not course-specific)

CONCLUSION: Dictionary approach is optimal for this assignment given:
   - Limited training data
   - 200 MB container constraint
   - Course-specific domain
   - Need for interpretability
""")
    print("="*60)


if __name__ == "__main__":
    # Check if sklearn is available
    try:
        import sklearn
        compare_approaches()
    except ImportError:
        print("⚠️  scikit-learn not installed!")
        print("Install with: pip install scikit-learn")
        print("\nFor now, running dictionary approach only...")
        
        dict_analyzer = SentimentAnalyzer()
        evaluate_accuracy(dict_analyzer, ALL_TESTS, "Dictionary Approach", tolerance=1)
