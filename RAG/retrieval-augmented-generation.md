Retrieval-Augmented Generation
==============================
Build a Retrieval-Augmented Generation (RAG) system over DTU course
data that can answer natural-language questions about courses,
teachers, and topics with implementation in a dockerize Web service.

Your system should:

1. Retrieve relevant course documents (dense or sparse retrieval)
2. Aggregate the retrieved information
3. Generate a natural-language answer using a local LLM

Dataset
-------

You will receive two files:

- `dtu_courses.warc.gz` — archived HTML source of course pages

- `dtu_courses.jsonl` — structured JSON lines extracted from the pages

Each JSON line corresponds to one course, for example:

```
{
  "course_code": "02195",
  "title": "Quantum Algorithms and Machine Learning",
  "academic_year": "2025/2026",
  "fields": {
    "Responsible": "Sven Karlsson",
    "Point( ECTS )": 5,
    "Language of instruction": "English",
    "Department": "01 Department of Applied Mathematics and Computer Science"
  },
  "learning_objectives": [
    "Explain common quantum algorithms",
    "Use quantum computing frameworks",
    "Develop quantum algorithms"
  ],
  "content": "Use of key quantum concepts in algorithms: Quantum states; Qubits; Entanglement ..."
}
```

System Overview
---------------

Your system should implement a retrieval component and a generation
component exposed as a FastAPI web service. 

1. Retrieval Component

Implement one or more of the following:

- Sparse, scikit-learn (TfidfVectorizer) or gensi
- Dense, e.g. sentence-transformers	
- Hybrid, Weighted combination	score = α * dense + (1−α) * sparse

2. Generation Component

Use a local LLM (e.g., via dspy) to generate final answers.

Example setup:

```
import os
from dotenv import load_dotenv
import dspy

load_dotenv(os.path.expanduser("~/.env"))

api_key = os.getenv("CAMPUSAI_API_KEY")
model = "openai/" + os.getenv("CAMPUSAI_MODEL")
api_url = os.getenv("CAMPUSAI_API_URL")

dspy.configure(lm=dspy.LM(api_key=api_key, api_base=api_url, model=model))

Given a user query:

- Retrieve top-k relevant courses
- Aggregate them into a text prompt (e.g., title, teachers, objectives)
- Call the LLM to generate an answer
- Return the answer and the retrieved courses

Endpoints
---------
1. Search endpoint

`GET /v1/search?query=<text>&top_k=5&mode=sparse|dense|hybrid`

Response:

```
{
  "query": "MRI",
  "mode": "sparse",
  "results": [
    {"course_code": "22507", "title": "22507 Advanced Magnetic Resonance Imaging", "score": 0.912},
    {"course_code": "22506", "title": "22506 Medical Magnetic Resonance Imaging", "score": 0.884}
  ]
}
```

2. Question answering endpoint (RAG)

`GET /v1/ask?query=<natural-language-question>&top_k=5&mode=sparse|dense`

Response:

```
{
  "query": "How many ECTS points is Tue Herlau's course?",
  "answer": "Tue Herlau is responsible for 02465 Introduction to reinforcement learning and control, which gives 5 ECTS points.",
  "retrieved_courses": [
    {"course_code": "02445", "title": "02465 Introduction to reinforcement learning and control"}
  ]
}
```

Examples / Test Queries
-----------------------
"How many ECTS points is Tue Herlau's course?"	5 ECTS

"Are there any courses about MRI?"	22507, 22506

"Does Ivana Konvalenka teach a course together with another teacher?"
02464 Artificial Intelligence and Human Cognition

"Which course is Hiba Nassar involved in?"	02461 Signal and Data


Implementation suggestions
--------------------------

Input processing

- Combine relevant fields: "title", "learning_objectives", "fields",
  "content". This could be by simple `json.dumps`
- Lowercase and strip accents for sparse retrieval.
- Optional: limit to 2 KB text per course for dense models.

Retrieval

- Normalize vectors for cosine similarity.
- Return both scores and course metadata.
- Optionally support hybrid scoring.

Prompt construction

- Include the question and the top-k retrieved course snippets.
- Example template:

```
You are a helpful assistant for DTU courses.
Use the context below to answer the user's question.
If the answer is not present, say you don't know.

Question: {query}

Context:
{course_1}
{course_2}
...

Answer:
``` 

Generation

- Use dspy with your local LLM endpoint (OpenAI-compatible API).
- Limit total prompt size (e.g., 2 000–4 000 characters).

Output

- Return JSON with the generated answer and list of retrieved courses.

Serving
-------
Dockerfile:

```
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

Testing
-------

Example queries

```
# Search courses about MRI
curl -s "http://localhost:8000/v1/search?query=MRI&mode=sparse" | jq

# Ask question via RAG
curl -s "http://localhost:8000/v1/ask?query=Which%20course%20is%20Hiba%20Nassar%20involved%20in?" | jq
```

Deliverables
------------
A zipped repository with Dockerfile in root (git archive -o latest.zip HEAD)