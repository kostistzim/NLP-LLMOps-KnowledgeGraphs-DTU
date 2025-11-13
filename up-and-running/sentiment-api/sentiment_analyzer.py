"""
Advanced sentiment analyzer with support for:
- Negation handling (not good, ikke god)
- Intensifiers (very, really, meget, rigtig)
- Multiple sentiment words
- Language-specific dictionaries
"""

from typing import Dict, List, Tuple
from language_detector import LanguageDetector


class SentimentAnalyzer:
    """Advanced sentiment analyzer for course evaluations"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        
        # Danish sentiment words
        self.danish_sentiment = {
            # Very positive (5)
            'fantastisk': 5, 'fremragende': 5, 'utrolig': 5, 'exceptionel': 5,
            'perfekt': 5, 'brilliant': 5, 'outstanding': 5,
            
            # Positive (3-4)
            'god': 3, 'godt': 3, 'gode': 3, 'gods': 3,
            'interessant': 3, 'engagerende': 3, 'inspirerende': 4,
            'lærerig': 4, 'lærerigt': 4, 'informativ': 3,
            'spændende': 3, 'velorganiseret': 3, 'struktureret': 3,
            'nyttig': 3, 'relevant': 3, 'klar': 3,
            
            # Slightly positive (1-2)
            'okay': 1, 'fin': 2, 'fint': 2, 'nogenlunde': 1,
            'rimelig': 2, 'acceptabel': 1,
            
            # Negative (-3 to -2)
            'dårlig': -3, 'dårligt': -3, 'dårlige': -3,
            'kedelig': -3, 'kedeligt': -3, 'kedelige': -3,
            'forvirrende': -3, 'ustruktureret': -3, 'kaotisk': -3,
            'irrelevant': -3, 'uengagerende': -3, 'svær': -2,
            'svært': -2, 'svære': -2, 'uklar': -2,
            
            # Very negative (-5 to -4)
            'forfærdelig': -5, 'forfærdeligt': -5, 'forfærdelige': -5,
            'terrible': -5, 'spild': -4, 'værdiløs': -5,
            'meningsløs': -4, 'ubrugelig': -4,
        }
        
        # English sentiment words
        self.english_sentiment = {
            # Very positive (5)
            'amazing': 5, 'fantastic': 5, 'excellent': 5, 'outstanding': 5,
            'brilliant': 5, 'exceptional': 5, 'perfect': 5, 'wonderful': 5,
            
            # Positive (3-4)
            'good': 3, 'great': 4, 'interesting': 3, 'engaging': 3,
            'inspiring': 4, 'informative': 3, 'useful': 3, 'helpful': 3,
            'clear': 3, 'organized': 3, 'structured': 3, 'relevant': 3,
            'effective': 3, 'enjoyable': 4,
            
            # Slightly positive (1-2)
            'okay': 1, 'fine': 2, 'decent': 2, 'acceptable': 1,
            'adequate': 1, 'fair': 2, 'reasonable': 2,
            
            # Negative (-3 to -2)
            'bad': -3, 'poor': -3, 'boring': -3, 'dull': -3,
            'confusing': -3, 'unclear': -2, 'difficult': -2,
            'unorganized': -3, 'disorganized': -3, 'irrelevant': -3,
            'useless': -4, 'unhelpful': -3, 'dry': -3,
            
            # Very negative (-5 to -4)
            'terrible': -5, 'awful': -5, 'horrible': -5, 'waste': -4,
            'worst': -5, 'pathetic': -5, 'disappointing': -4,
        }
        
        # Danish intensifiers
        self.danish_intensifiers = {
            'meget': 1.5, 'rigtig': 1.4, 'super': 1.6, 'ekstremt': 1.7,
            'utrolig': 1.6, 'virkelig': 1.4, 'helt': 1.3, 'særlig': 1.2,
        }
        
        # English intensifiers
        self.english_intensifiers = {
            'very': 1.5, 'really': 1.4, 'extremely': 1.7, 'incredibly': 1.6,
            'absolutely': 1.6, 'truly': 1.4, 'quite': 1.2, 'pretty': 1.2,
        }
        
        # Danish negations
        self.danish_negations = {'ikke', 'aldrig', 'ingen', 'intet'}
        
        # English negations
        self.english_negations = {'not', 'no', 'never', 'neither', "n't", 'dont', "don't"}
        
    def analyze(self, text: str) -> int:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text
            
        Returns:
            Sentiment score from -5 to 5
        """
        # Detect language
        language = self.language_detector.detect(text)
        
        # Get language-specific resources
        if language == 'da':
            sentiment_dict = self.danish_sentiment
            intensifiers = self.danish_intensifiers
            negations = self.danish_negations
        else:
            sentiment_dict = self.english_sentiment
            intensifiers = self.english_intensifiers
            negations = self.english_negations
        
        # Tokenize and lowercase
        words = text.lower().split()
        
        # Analyze sentiment
        scores = []
        i = 0
        
        while i < len(words):
            word = words[i].strip('.,!?;:')
            
            # Check if current word is a sentiment word
            if word in sentiment_dict:
                base_score = sentiment_dict[word]
                
                # Check for intensifier before this word
                intensifier = 1.0
                if i > 0:
                    prev_word = words[i-1].strip('.,!?;:')
                    if prev_word in intensifiers:
                        intensifier = intensifiers[prev_word]
                
                # Check for negation before this word (within 2 words)
                is_negated = False
                for j in range(max(0, i-2), i):
                    check_word = words[j].strip('.,!?;:')
                    if check_word in negations:
                        is_negated = True
                        break
                
                # Apply intensifier
                final_score = base_score * intensifier
                
                # Apply negation (flip sign and reduce magnitude)
                if is_negated:
                    final_score = -final_score * 0.8
                
                scores.append(final_score)
            
            i += 1
        
        # Calculate final score
        if not scores:
            return 0
        
        # Average the scores and round
        avg_score = sum(scores) / len(scores)
        
        # Clamp to -5 to 5 range
        final_score = max(-5, min(5, round(avg_score)))
        
        return final_score
    
    def analyze_detailed(self, text: str) -> Dict:
        """
        Analyze sentiment with detailed breakdown
        
        Returns:
            Dictionary with score, language, and analysis details
        """
        language = self.language_detector.detect(text)
        score = self.analyze(text)
        
        return {
            'score': score,
            'language': language,
            'text': text,
        }


if __name__ == "__main__":
    # Test the analyzer
    analyzer = SentimentAnalyzer()
    
    test_cases = [
        "Det var en god lærer.",
        "It was a bad course",
        "It was a very dry course and I did not learn much.",
        "Fantastisk kursus! Jeg lærte meget.",
        "Det var ikke et godt kursus.",
        "Really excellent teacher and engaging material.",
        "Rigtig dårligt kursus med kedelig underviser.",
    ]
    
    print("Testing sentiment analyzer:\n")
    for text in test_cases:
        result = analyzer.analyze_detailed(text)
        print(f"Text: {text}")
        print(f"Score: {result['score']} | Language: {result['language']}")
        print("-" * 60)
