# Person to Wikidata API

REST API for querying Wikidata information about people: birthdays, doctoral students, political parties, and advisors.

## Overview

This service performs entity linking to find people on Wikidata and retrieves structured data about them using SPARQL queries.

## Requirements

- Python 3.11
- Docker (optional)
- Internet connection (queries Wikidata)
- Conda environment (see `llm-operations.yml` in parent directory)

## Installation

### Local Development
```bash
# Activate conda environment
conda activate llm-operations

# Run the API
uvicorn main:app --reload
```

### Docker
```bash
# Build image
docker build -t person-to-wikidata:latest .

# Run container
docker run --rm -p 8000:8000 person-to-wikidata:latest
```

## API Usage

### Endpoints

1. **POST /v1/birthday** - Get person's date of birth
2. **POST /v1/students** - Get person's doctoral students
3. **POST /v1/all** - Get birthday and students (parallel)
4. **POST /v1/political-party** - Get person's political party
5. **POST /v1/supervisor** - Get person's doctoral advisor

### Request Format
```json
{
  "person": "Niels Bohr",
  "context": "When was Niels Bohr born?"
}
```

- **person** (required): Person's name
- **context** (optional): Natural language context (for future extensions)

## Examples

### Birthday
```bash
curl -X POST http://localhost:8000/v1/birthday \
  -H 'Content-Type: application/json' \
  -d '{"person":"Niels Bohr"}'
```

**Response:**
```json
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "birthday": "1885-10-07"
}
```

### Students
```bash
curl -X POST http://localhost:8000/v1/students \
  -H 'Content-Type: application/json' \
  -d '{"person":"Niels Bohr"}'
```

**Response:**
```json
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "students": [
    {"label": "Aage Bohr", "qid": "Q103854"},
    {"label": "Oskar Klein", "qid": "Q251524"}
  ]
}
```

### All Data
```bash
curl -X POST http://localhost:8000/v1/all \
  -H 'Content-Type: application/json' \
  -d '{"person":"Niels Bohr"}'
```

**Response:**
```json
{
  "person": "Niels Bohr",
  "qid": "Q7085",
  "birthday": "1885-10-07",
  "students": [
    {"label": "Aage Bohr", "qid": "Q103854"},
    {"label": "Oskar Klein", "qid": "Q251524"}
  ]
}
```

### Political Party
```bash
curl -X POST http://localhost:8000/v1/political-party \
  -H 'Content-Type: application/json' \
  -d '{"person":"Mette Frederiksen"}'
```

**Response:**
```json
{
  "person": "Mette Frederiksen",
  "qid": "Q5015",
  "political_party": {
    "label": "Social Democrats",
    "qid": "Q287044"
  }
}
```

## Testing
```bash
# Run tests
python test_main.py

# Or with pytest
pytest test_main.py -v
```

## Documentation

Interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
person-to-wikidata/
├── main.py                  # FastAPI application
├── wikidata_client.py       # Generic SPARQL executor
├── entity_linker.py         # Name → QID resolution
├── property_queries.py      # Property-specific queries
├── test_main.py            # Test suite
├── Dockerfile              # Container configuration
└── README.md               # This file
```

## Architecture

### Two-Step Approach

1. **Entity Linking:** Person name → Wikidata QID
2. **Property Query:** QID → Specific data

### Entity Linking

Uses Wikidata Search API (`wbsearchentities`) for:
- Fuzzy matching ("Niels Bohr" = "Bohr" = "N. Bohr")
- Ranked results
- Description-based filtering (prefers people over places)

### Property Queries

Uses SPARQL for structured queries:
- **P569**: Date of birth
- **P185**: Doctoral student
- **P102**: Political party
- **P184**: Doctoral advisor

### Async/Parallel Execution

The `/v1/all` endpoint uses `asyncio.gather` to query birthday and students simultaneously for faster response times.

## Design Decisions

### Why Search API for Entity Linking?

- Handles typos and variations
- Returns ranked results
- More user-friendly than exact SPARQL matching

### Why SPARQL for Properties?

- Precise control over queries
- Efficient for structured data
- Can filter and aggregate

### Why Async?

- Wikidata queries can take 200-500ms
- Parallel execution saves time
- `/v1/all` is ~2x faster than sequential

## Error Handling

**404 Not Found:**
- Person not found in Wikidata
- No matching entity

**Example:**
```bash
curl -X POST http://localhost:8000/v1/birthday \
  -H 'Content-Type: application/json' \
  -d '{"person":"Completely Fake Person XYZ"}'

# Response: 404 {"detail": "Person 'Completely Fake Person XYZ' not found"}
```

**Missing Data:**
- Returns `null` if property not found
- Empty list `[]` for students if none exist

## Wikidata Properties Used

| Property | ID | Description |
|----------|-----|-------------|
| Date of birth | P569 | Person's birthday |
| Doctoral student | P185 | Students advised |
| Political party | P102 | Party membership |
| Doctoral advisor | P184 | PhD supervisor |

## Limitations

- Requires internet connection
- Depends on Wikidata data quality
- Entity linking may return wrong person for ambiguous names
- Some properties may be missing for certain people

## Submission

Create submission archive:
```bash
git archive -o latest.zip HEAD
```

## Notes

- First request may be slower (cold start)
- Wikidata rate limits apply
- User-Agent header required (included in code)
- SPARQL queries are cached by Wikidata