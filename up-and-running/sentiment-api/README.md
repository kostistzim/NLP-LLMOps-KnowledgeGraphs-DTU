# Course Evaluation Sentiment Analysis API

A REST API for analyzing sentiment in Danish and English course evaluations, built with FastAPI and Docker.

##  Features

- **Bilingual Support**: Automatic detection of Danish and English
- **Advanced Sentiment Analysis**:
  - Negation handling ("not good", "ikke god")
  - Intensifier support ("very", "meget", "rigtig")
  - Multi-word sentiment scoring
- **Score Range**: -5 (very negative) to 5 (very positive)
- **REST API**: Simple JSON interface
- **Auto-Documentation**: Swagger UI at `/docs`
- **Small Container**: < 200 MB Docker image

## Test Results

- **Assignment Tests**: 2/3 passing perfectly, 1 within ±1
- **Overall Accuracy**: 95.8% on 24 test cases (±1 tolerance)
- **Languages**: 12 Danish + 12 English test cases

##  Quick Start

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload

# Or run directly
python main.py
```

Visit http://localhost:8000/docs for Swagger UI

### Run Tests

```bash
python test_main.py
```

### Run with Docker

```bash
# Build the image
docker build -t sentiment-api .

# Run the container
docker run -p 8000:8000 sentiment-api

# Check image size
docker images sentiment-api
```

##  API Usage

### Basic Sentiment Analysis

```bash
curl -X POST "http://localhost:8000/v1/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text":"Det var en god lærer."}'
```

Response:
```json
{"score": 3}
```

### Detailed Analysis

```bash
curl -X POST "http://localhost:8000/v1/sentiment/detailed" \
     -H "Content-Type: application/json" \
     -d '{"text":"It was a bad course"}'
```

Response:
```json
{
  "score": -3,
  "language": "en",
  "text": "It was a bad course"
}
```

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/sentiment",
    json={"text": "Fantastisk kursus!"}
)
print(response.json())  # {"score": 5}
```

## 🎓 Implementation Approach

### Dictionary-Based Sentiment Analysis

**Pros:**
-  Very small size (< 1 MB of code)
-  Fast inference (< 1ms)
-  Interpretable and debuggable
-  No training data required
-  Easy to customize for course evaluations

**Cons:**
-  Limited by predefined vocabulary
-  May miss nuanced expressions
-  Requires manual curation of word lists

### Advanced Features

1. **Language Detection**
   - Character-based (æ, ø, å)
   - Word-based (common words)
   - Defaults to English if unclear

2. **Negation Handling**
   - Detects negations within 2 words
   - Flips sentiment and reduces magnitude
   - Examples: "not good" → negative

3. **Intensifiers**
   - Multiplies base sentiment score
   - "very" (1.5x), "extremely" (1.7x)
   - "meget" (1.5x), "rigtig" (1.4x)

4. **Multi-word Scoring**
   - Averages all sentiment words in text
   - Handles complex evaluations
   - Clamps final score to [-5, 5]

##  Project Structure

```
.
├── main.py                 # FastAPI application
├── sentiment_analyzer.py   # Core sentiment logic
├── language_detector.py    # Language detection
├── test_data.py           # Test cases (24 examples)
├── test_main.py           # Test suite
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md             # This file
```

## 🧪 Test Cases

### Assignment Tests (Required)

1.  "Det var en god lærer." → 3
2.  "It was a bad course" → -3
3.   "It was a very dry course and I did not learn much." → -4 (expected -3)

### Additional Test Coverage

- Very positive (5): "Fantastisk kursus!", "Amazing course!"
- Positive (3-4): "Good teacher", "Rigtig godt"
- Neutral (0-1): "Okay course", "Standard kursus"
- Negative (-3): "Bad course", "Kedelig underviser"
- Very negative (-5): "Terrible!", "Forfærdelig!"
- Negations: "Not good", "Ikke god"
- Intensifiers: "Very good", "Meget dårlig"

##  Customization

### Add More Sentiment Words

Edit `sentiment_analyzer.py`:

```python
self.danish_sentiment = {
    'new_positive_word': 3,
    'new_negative_word': -3,
    # ...
}
```

### Adjust Intensifier Strength

```python
self.english_intensifiers = {
    'very': 1.5,  # Adjust multiplier
    'extremely': 1.7,
}
```

##  Container Size Analysis

| Component | Size |
|-----------|------|
| Base image (python:3.11-alpine) | ~50 MB |
| Python packages (FastAPI, uvicorn) | ~20 MB |
| Application code | < 1 MB |
| **Total** | **~71 MB** |

Well under the 200 MB requirement! 

##  Assignment Questions Answered

### Q: What are pros/cons of dictionary, ML, and LLMs?

**Dictionary (Current Implementation):**
- Pros: Tiny, fast, interpretable
- Cons: Limited vocabulary, misses context

**Machine Learning (scikit-learn):**
- Pros: Learns patterns, better accuracy
- Cons: Needs training data, larger size (~50-100 MB)

**Pre-trained LLMs:**
- Pros: Best accuracy, understands context
- Cons: HUGE (200MB+ for tiny models), slower, overkill for this task

### Q: How to handle two languages?

**Chosen approach**: Language detection + separate dictionaries
- Automatic detection based on characters and words
- Language-specific sentiment dictionaries
- Shared scoring logic

**Alternatives considered:**
- Multilingual model (would exceed 200 MB)
- Translation to English (adds latency)
- Separate endpoints (less elegant UX)

### Q: What's possible within 200 MB?

-  Dictionary-based (< 100 MB)
-  Small ML models like Logistic Regression (~100 MB)
-  BERT-tiny (~120 MB model alone, ~180 MB total)
-  BERT-base (400+ MB)
-  Larger transformers (GB+)

### Q: More annotated data?

**Found resources:**
- DaNLP library (Danish sentiment datasets)
- European language resources
- Trustpilot reviews (Danish)

**Could create:**
- Manual annotation of real DTU evaluations
- Crowdsourcing from classmates
- Synthetic data generation

##  Dependencies

```
fastapi==0.115.5
uvicorn[standard]==0.32.1
pydantic==2.10.3
```

##  Known Issues

- Third assignment test case scores -4 instead of -3 (within tolerance)
- Empty text returns score of 0 (could return error instead)
- Very long texts not optimized (though still fast)

##  Author

DTU Student - Natural Language Processing Course  
Technical University of Denmark

##  License

MIT License - Free for educational use

---

**Questions?** Check the Swagger docs at `/docs` or run `python test_main.py` to see all examples.
