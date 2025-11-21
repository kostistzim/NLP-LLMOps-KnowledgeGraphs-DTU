PDF to sentences
================

Purpose
-------
Get a small text processing pipeline implemented with conversion from PDF to text and extraction of sentences.

Task
----
Construct Docker/Podman container or a set of docker containers with docker compose that expose
a REST-based Web service with a Python program running from port 8000 that extract sentences from the body text of a PDF file. 
The endpoint should be `/v1/extract-sentences` and with POST with field `pdf_file`.
The system must not use external Web services, only the services set up on the docker compose.

The Web service should return the response as JSON with a dictionary with the field ``sentences'' that is a list of strings.


Testing
-------

With the Web service running a test file called `2303.15133.pdf` you should be able to do
```
curl -s -F pdf_file=@2303.15133.pdf http://localhost:8000/v1/extract-sentences | jq
```

Before you put the Web service in a container you can also test it

To test the setup with a file called `2303.15133.pdf` and with no container.
```python
import os
os.environ.setdefault("GROBID_URL", "http://localhost:8070")
# The above is necessary if we have a GROBID container running to do the conversion

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_extract_sentences():
    # Adjust the path to your PDF file
    pdf_path = "2303.15133.pdf"

    with open(pdf_path, "rb") as f:
        files = {"pdf_file": ("2303.15133.pdf", f, "application/pdf")}
        response = client.post("/v1/extract-sentences", files=files)

    # --- basic checks
    assert response.status_code == 200, response.text
    data = response.json()
    assert "sentences" in data
    assert isinstance(data["sentences"], list)

    sentence = "How language should best be handled is not clear."
    assert sentence in data["sentences"]
```
And then run with `pytest`.

Questions
---------
Consider some issues
- What kind of tool should convert the PDF to text?
- What tool should be used to convert the text to sentences
- What are difficult conversions?


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
- PDF
  - "Natural language processing" - chapter "Text", particularly about XML, PDF, GROBID, MarkItDown and Docling


Handin
------
- Zipped archieved repository with a `compose.yaml`: `git archive -o latest.zip HEAD`
  
