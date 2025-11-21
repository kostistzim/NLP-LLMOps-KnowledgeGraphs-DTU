Information retrieval
=====================
Build and evaluate a small information retrieval (IR) system over DTU course data (titles + learning objectives) with
sparse (TF-IDF) and/or dense (Sentence-Transformers) retrieval, expose it as a FastAPI web service in a Docker container.

Dataset
-------
```
{
  "02402": {
    "title": "02402 Statistics (Polytechnical Foundation)",
    "learning-objectives": [
      "Estimate and interpret simple summary statistics...",
      "Apply simple graphical techniques...",
      "Identify and describe probability distributions..."
    ]
  },
  "02403": { "...": "..." }
}
```

System overview
---------------
Indexing unit (one or more)
- Course-level documents: doc_text = title + "\n" + "\n".join(learning_objectives)
- learning objective-level documents 

Retrievers (one or more, choose one as default)
- Sparse, e.g., TfidfVectorizer or Gensim. Consider lowercase, ngram_range=(1,2), cosine similarity
- Dense: e.g., sentence-transformers/distiluse-base-multilingual-cased-v2
- Hybrid: `score = alpha * dense + (1− alpha) * sparse`

Serving:
- FastAPI app with endpoints below
- In-memory indices (optionally a vector database)

Endpoints
---------
Choose one or more of the endpoints.

- Similar courses given a course ID

`GET /v1/courses/{course_id}/similar?top_k=10&mode=dense|sparse|hybrid&alpha=0.5`

```
{
  "query_course_id": "02451",
  "results": [
    {"course_id": "02452", "title": "02452 ...", "score": 0.873},
    {"course_id": "02460", "title": "02460 ...", "score": 0.741}
  ],
  "mode": "dense",
  "top_k": 10
}
```

- Search courses by free text query

`GET /v1/search?query=machine%20learning&top_k=10&mode=dense|sparse|hybrid&alpha=0.5`

```
{
  "query": "machine learning",
  "results": [
    {"course_id": "02460", "title": "02460 Advanced Machine Learning", "score": 0.912},
    {"course_id": "02451", "title": "02451 Introduction to Machine Learning", "score": 0.881}
  ],
  "mode": "hybrid"
}
```

- Search learning objectives (return objective + course)

`GET /v1/objectives/search?query=dimensionality%20reduction&top_k=10&mode=dense|sparse|hybrid&alpha=0.5`

```
{
  "query": "dimensionality reduction",
  "results": [
    {"course_id": "02451", "title": "02451 Introduction to Machine Learning", "objective": "Match practical problems to standard ...", "score": 0.834},
    {"course_id": "02460", "title": "02460 Advanced Machine Learning", "objective": "Operationalize and implement graph ...", "score": 0.802}
  ]
}
```

- Health check (optional)

`GET /v1/health`

{"status": "ok", "index_sizes": {"courses": 55, "objectives": 600}}


Testing
-------
Similar courses

`curl -s "http://localhost:8000/v1/courses/02451/similar" | jq

Keyword search

`curl -s "http://localhost:8000/v1/search?query=machine%20learning" | jq`

Objective search

`curl -s "http://localhost:8000/v1/objectives/search?query=principal%20component" | jq `


Handin
------
- Zipped repository with Dockerfile in the root: `git archive -o latest.zip HEAD`