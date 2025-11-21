Text to persons
===============

Purpose
-------
Get an LLM API to do named entity recognition.


Task
----
Construct a Docker/Podman container that exposes a REST-based Web service
with a Python program running from port 8000 that extract person names
from a given text.
The endpoint should be `/v1/extract-persons` and with POST with field `text`.
The system can use the API from the CampusAI at
https//campusai.compute.dtu.dk with an appropriate prompt.

The Web service should return the response as JSON with a dictionary
with the field ``persons'' that is a list of strings. Where each
string is a name from the text.

If you use the LLM API you need a CAMPUSAI_API_KEY from the
CampusAI. You API keyy must NOT be included in the hand-in. Instead
put it in a `~/.env` file. and build and run the container with

```
docker build -t text-to-persons:latest .
docker run --rm -p 8000:8000 --env-file ~/.env text-to-persons:latest
```
This way your API key stay on your computer (in the `.env` file) and
if others (e.g., me) should use your container/Webservice they need to
provide their own API key.


Testing
-------
When you have the Web server running you should be able access the
Swagger UI with you API documentation at

http://127.0.0.1:8000/docs

There you can also test it.

With the Web service running you should also be able to do
```
curl -s -X POST http://localhost:8000/v1/extract-persons \
  -H 'Content-Type: application/json' \
  -d '{"text":"Einstein and von Neumann meet each other."}' | jq
```

If you construct a function called `campusai_extract_persons` then you
can test it with

```python

examples = [
   "Ms Mette Frederiksen is in New York today.",
   "Einstein and von Neumann meet each other."
]
expected = [
  ["Mette Frederiksen"],
  ["Einstein", "von Neumann"],
]

import os
from app import extract_persons

def test_examples_from_prompt():
    examples = [
        "Ms Mette Frederiksen is in New York today.",
        "Einstein and von Neumann meet each other.",
    ]
    expected = [
        ["Mette Frederiksen"],
        ["Einstein", "von Neumann"],
    ]
    for text, exp in zip(examples, expected):
        assert campusai_extract_persons(text) == exp
```
If the test is in a `test_` prefixed file you can run with `pytest`.


Questions
---------
Consider some issues
- Should the CampusAI LLM API be used or is, e.g., spaCy better?
- What models are there on CampusAI?
- Should the LLM be called via a library or "directly" to the Web API.
- What format should the prompt have?
- Are chain-of-thought, few-short prompting, etc. necessary?


Requirements & Resources
------------------------
- Python
- Command-line interface
- Git
  - [DTU MLOps – Organisation and Version Control](https://skaftenicki.github.io/dtu_mlops/s2_organisation_and_version_control/git/)
- Web serving with FastAPI
  - "Natural language processing" - chapter "Web serving" section 8.1
- Docker and docker compose
  - "Natural language processing" - chapter "Containerization" section 8.2
- Prompting engineering
  - "Natural langauage processing" - Chapter 7
- LLM API and CampusAI
  - "Natural langauge processing" - particularly section 8.3.3.
- Entity recognition
  - "Knowledge graphs" - chapter 8, particularly section 8.2 


Handin
------
- Zipped archieved repository with a `Dockerfile` in the root: `git archive -o latest.zip HEAD`
