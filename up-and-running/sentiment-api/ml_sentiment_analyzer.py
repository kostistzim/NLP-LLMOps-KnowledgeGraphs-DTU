"""
ML-based sentiment analyzer using scikit-learn
This is an alternative to the dictionary-based approach
"""

from typing import List, Tuple
import pickle
from pathlib import Path


class MLSentimentAnalyzer:
    """
    Machine Learning-based sentiment analyzer
    Uses TfidfVectorizer + LogisticRegression
    """
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def train(self, texts: List[str], labels: List[int]):
        """
        Train the ML model
        
        Args:
            texts: List of training texts
            labels: List of sentiment scores (-5 to 5)
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        
        # Vectorize texts
        self.vectorizer = TfidfVectorizer(
            max_features=1000,  # Limit features to keep model small
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,
            strip_accents='unicode',  # Handle Danish characters
        )
        
        X = self.vectorizer.fit_transform(texts)
        
        # Train classifier
        # Map scores to classes: [-5,-4,-3] -> negative, [-2,-1,0,1,2] -> neutral, [3,4,5] -> positive
        # Then we'll map back to scores
        self.model = LogisticRegression(
            max_iter=500,
            multi_class='multinomial',
            random_state=42
        )
        
        self.model.fit(X, labels)
        self.is_trained = True
        
        print(f"✓ Model trained on {len(texts)} examples")
        print(f"  Vocabulary size: {len(self.vectorizer.vocabulary_)}")
    
    def analyze(self, text: str) -> int:
        """
        Analyze sentiment using trained model
        
        Args:
            text: Input text
            
        Returns:
            Sentiment score from -5 to 5
        """
        if not self.is_trained:
            raise ValueError("Model not trained! Train the model first or load a pre-trained one.")
        
        # Vectorize input
        X = self.vectorizer.transform([text])
        
        # Predict
        score = self.model.predict(X)[0]
        
        # Ensure score is in valid range
        return max(-5, min(5, int(score)))
    
    def save_model(self, path: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model from disk"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.is_trained = True
        
        print(f"✓ Model loaded from {path}")
    
    def get_model_size(self, path: str = None) -> int:
        """Get size of saved model in bytes"""
        if path and Path(path).exists():
            return Path(path).stat().st_size
        return 0


def train_ml_model(save_path: str = "models/ml_sentiment.pkl"):
    """
    Train and save ML model using test data
    
    This creates a baseline ML model for comparison with dictionary approach
    """
    from test_data import ALL_TESTS
    
    # Prepare training data
    texts = [t[0] for t in ALL_TESTS]
    labels = [t[1] for t in ALL_TESTS]
    
    print("Training ML sentiment model...")
    print(f"Training samples: {len(texts)}")
    
    # Initialize and train
    analyzer = MLSentimentAnalyzer()
    analyzer.train(texts, labels)
    
    # Save model
    Path("models").mkdir(exist_ok=True)
    analyzer.save_model(save_path)
    
    # Report size
    size_mb = analyzer.get_model_size(save_path) / (1024 * 1024)
    print(f"✓ Model size: {size_mb:.2f} MB")
    
    return analyzer


if __name__ == "__main__":
    # Train and save model
    analyzer = train_ml_model()
    
    # Test it
    print("\nTesting ML model:")
    test_texts = [
        "Det var en god lærer.",
        "It was a bad course",
        "Fantastisk kursus!",
    ]
    
    for text in test_texts:
        score = analyzer.analyze(text)
        print(f"  '{text}' → {score}")
