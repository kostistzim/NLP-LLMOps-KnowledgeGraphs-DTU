Person to Wikidata
==================

Purpose
-------
Build a dockerized FastAPI microservice that, given a person's name,
resolves the entity on Wikidata and answers simple knowledge questions
via Wikidata APIs and/or SPARQL. Emphasis: entity linking, property
lookup and relationship queries.

Task
----
Construct a Docker/Podman container that exposes a REST web service on
port 8000 with endpoints:
* POST /v1/birthday
* POST /v1/students
* POST /v1/all
Optional:
* POST /v1/political-party
* POST /v1/supervisor

*Input*
``` 
{
  "person": "Mette Frederiksen",
  "context": "When was Mette Frederiksen born?"
}
```
* `person`: (string, required) - The person's name to look up in Wikidata.
*  context: (string, optional) - A question, to provide natural
context (not strictly used, but useful for RAG demos or
prompt-engineering extensions).

*Output examples*
* `POST /v1/birthday`
```
{
  "person": "Mette Frederiksen",
  "qid": "Q5015",
  "birthday": "1977-11-19",
}
```

* `POST /v1/students`
```
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "students": [
    {"label": "Aage Bohr", "qid": "Q103854"},
    {"label": "Oskar Klein", "qid": "Q251524"},
    ...
  ]
}
```

* `POST /v1/all`
```
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "birthday": "1885-10-07",
  "students": [
    {"label": "Aage Bohr", "qid": "Q103854"},
    {"label": "Oskar Klein", "qid": "Q251524"},
    ...
  ]
}
``` 

Testing
-------
When the Web app is running on the base system or in the container you
should be able to do manual testing in http://127.0.0.1:8000/docs with
"Try it out" under each endpoint.

You can also test it with, e.g., 
```
$ curl -s -X POST http://localhost:8000/v1/birthday \
  -H 'Content-Type: application/json' \
  -d '{"person":"Niels Bohr"}' | jq
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "birthday": "1885-10-07"
}
```

Questions
---------
Consider the issues:
- Should we break down the task to first find the item (the Wikidata
QID for the person) and then the data for the person?
- How should we get the item from the the person name? With the
Wikidata API wbsearchentites or SPARQL?
- How should we get the data when the QID of the item is identified?
- What is the Wikidata property for birthday
- What is/are the Wikidata property/ies for student?
- What are there of problem for date of birth?
- What kind of query synchronous/asynchrous should be made?


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
- Wikidata
  - "Knowledge graphs - chapter 3
- SPARQL
  - "Knowledge graphs" - chapter 4
- Entity linking
  - "Knowledge graphs" - chapter 8