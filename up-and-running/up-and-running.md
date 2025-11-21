Up and running
==============

Purpose
-------
Get git and docker with a web service running with a simple sentiment analysis implemented with FastAPI.

Task
----
Construct a Docker/Podman container less than 200 MB with a REST-based Web service with a Python program running from port 8000 that scores Danish or English course evaluations for sentiment.
The system must not use external Web services.
The API should be with the interface `/v1/sentiment` as HTTP POST.
The input is a JSON dictionary with the field `text`.
The Web service should return the response as JSON with a dictionary with the field ``score'' that is a float or integer value between
$-5$ and 5 where $-3$ is a common bad score, $-5$ really bad, 0 neutral, 3 good, 5 very good.
The Web service should have Swagger documentation. 
Examples of three course evaluation texts are
```
Det var en god lærer.
It was a bad course
It was a very dry course and I did not learn much.
```

When the lines are submitted individually to the web service, the values of the score field in the responses should be $3, -3, -3$, respectively.

Example
-------
For a baseline system, a Python file `main.py` may look like

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/v1/sentiment")
def analyze_sentiment(text: TextInput):
    lowered_text = text.text.lower()

    if 'god' in lowered_text or 'good' in lowered_text:
        return {"score": 3}
    elif 'dårlig' in lowered_text or 'bad' in lowered_text:
        return {"score": -3}
    else:
        return {"score": 0}
```
Here we need a `requirements.txt` file with

```
fastapi
uvicorn[standard]
```

To see if it works (without podman) we can make a `test_main.py` file
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_positive_sentiment():
    response = client.post("/v1/sentiment", json={"text": "Det var en god lærer."})
    assert response.status_code == 200
    assert response.json() == {"score": 3}

def test_negative_sentiment():
    response = client.post("/v1/sentiment", json={"text": "It was a bad course"})
    assert response.status_code == 200
    assert response.json() == {"score": -3}


if __name__ == "__main__":
    test_positive_sentiment()
    test_negative_sentiment()
    print("All tests passed!")
```
And then run `python test_main.py`.

A `Dockerfile` for podman using the small Alpine Linux (a "small and very resource efficient") is  
```dockerfile
FROM python:3.11-alpine

WORKDIR /app

COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  
```
This can be build and run with
```sh
$ podman build -t sentiment-api .
$ podman run -p 8000:8000 sentiment-api
```
After issue of the commands you should see the Swagger documentation for
the Web service automagically set up at
http://127.0.0.1:8000/docs. Here you can test the Web service.
If everything looks ok, then you can also test the Web service from the
command-line with the `curl` program
```bash
curl -X POST "http://localhost:8000/v1/sentiment" \
     -H "Content-Type: application/json" \
     -d '{"input":"It was a good course."}'
```
Alternatively, you can also call and test it with a Python program.

Questions
---------
Consider some issues
- What are the pros and cons with using dictionary, machine learning and pretrained LLMs for the task?
- ... and how should the two languages be handled?
- What is possible to do within 200 MB container?
- Is it possible to come up or find more text that have been annotated for sentiment and that resembles course evaluations?
- Other issues?

Requirements & Resources
------------------------
- Python
- Command-line interface
- Git
  - [DTU MLOps – Organisation and Version Control](https://skaftenicki.github.io/dtu_mlops/s2_organisation_and_version_control/git/)
- Web serving with FastAPI
  - "Natural language processing" - chapter "Web serving" section 8.1
- Docker
- Sentiment analysis
  - "Natural language processing" - chapter "Sentiment analysis"
