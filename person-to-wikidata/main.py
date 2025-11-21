"""
FastAPI application for Wikidata person queries
"""

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from entity_linker import find_person_qid
from property_queries import get_birthday, get_students, get_political_party, get_doctoral_advisor


app = FastAPI(
    title="Person to Wikidata API",
    description="Query Wikidata for person information: birthday, students, political party, advisor",
    version="1.0.0"
)


class PersonInput(BaseModel):
    """Input model for person queries"""
    person: str
    context: Optional[str] = None


class BirthdayResponse(BaseModel):
    """Response for birthday endpoint"""
    person: str
    qid: str
    birthday: Optional[str]


class Student(BaseModel):
    """Student information"""
    label: str
    qid: str


class StudentsResponse(BaseModel):
    """Response for students endpoint"""
    person: str
    qid: str
    students: List[Student]


class AllResponse(BaseModel):
    """Response for all data endpoint"""
    person: str
    qid: str
    birthday: Optional[str]
    students: List[Student]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Person to Wikidata API",
        "version": "1.0.0",
        "endpoints": [
            "/v1/birthday",
            "/v1/students",
            "/v1/all",
            "/v1/political-party",
            "/v1/supervisor"
        ]
    }


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/v1/birthday", response_model=BirthdayResponse)
async def birthday_endpoint(input_data: PersonInput):
    """Get person's birthday"""
    qid = await find_person_qid(input_data.person)
    
    if not qid:
        raise HTTPException(status_code=404, detail=f"Person '{input_data.person}' not found")
    
    birthday = await get_birthday(qid)
    
    return {
        "person": input_data.person,
        "qid": qid,
        "birthday": birthday
    }


@app.post("/v1/students", response_model=StudentsResponse)
async def students_endpoint(input_data: PersonInput):
    """Get person's doctoral students"""
    qid = await find_person_qid(input_data.person)
    
    if not qid:
        raise HTTPException(status_code=404, detail=f"Person '{input_data.person}' not found")
    
    students = await get_students(qid)
    
    return {
        "person": input_data.person,
        "qid": qid,
        "students": students
    }


@app.post("/v1/all", response_model=AllResponse)
async def all_endpoint(input_data: PersonInput):
    """Get birthday and students (parallel queries)"""
    qid = await find_person_qid(input_data.person)
    
    if not qid:
        raise HTTPException(status_code=404, detail=f"Person '{input_data.person}' not found")
    
    # Fetch both in parallel
    birthday, students = await asyncio.gather(
        get_birthday(qid),
        get_students(qid)
    )
    
    return {
        "person": input_data.person,
        "qid": qid,
        "birthday": birthday,
        "students": students
    }


@app.post("/v1/political-party")
async def political_party_endpoint(input_data: PersonInput):
    """Get person's political party (optional endpoint)"""
    qid = await find_person_qid(input_data.person)
    
    if not qid:
        raise HTTPException(status_code=404, detail=f"Person '{input_data.person}' not found")
    
    party = await get_political_party(qid)
    
    return {
        "person": input_data.person,
        "qid": qid,
        "political_party": party
    }


@app.post("/v1/supervisor")
async def supervisor_endpoint(input_data: PersonInput):
    """Get person's doctoral advisor (optional endpoint)"""
    qid = await find_person_qid(input_data.person)
    
    if not qid:
        raise HTTPException(status_code=404, detail=f"Person '{input_data.person}' not found")
    
    advisor = await get_doctoral_advisor(qid)
    
    return {
        "person": input_data.person,
        "qid": qid,
        "supervisor": advisor
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)