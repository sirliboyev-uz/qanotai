"""
Simplified FastAPI app - minimal dependencies for quick start
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

# Create app
app = FastAPI(
    title="QanotAI API",
    version="1.0.0",
    description="IELTS Speaking Test Preparation Platform"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
questions_db = {
    "part1": [
        {"id": str(uuid.uuid4()), "text": "Do you work or are you a student?", "part": 1},
        {"id": str(uuid.uuid4()), "text": "What do you like about your job/studies?", "part": 1},
        {"id": str(uuid.uuid4()), "text": "Where is your hometown?", "part": 1},
    ],
    "part2": [
        {"id": str(uuid.uuid4()), "text": "Describe a person who has influenced you", "part": 2,
         "bullet_points": ["Who this person is", "How you know them", "What influence they had"]},
        {"id": str(uuid.uuid4()), "text": "Describe a memorable journey", "part": 2,
         "bullet_points": ["Where you went", "How you traveled", "Why it was memorable"]},
    ],
    "part3": [
        {"id": str(uuid.uuid4()), "text": "What qualities make someone a good role model?", "part": 3},
        {"id": str(uuid.uuid4()), "text": "How has technology changed education?", "part": 3},
    ]
}

attempts_db = []

# Models
class Question(BaseModel):
    id: str
    text: str
    part: int
    bullet_points: Optional[List[str]] = None

class QuestionSet(BaseModel):
    part1: List[Question]
    part2: Question
    part3: List[Question]

class AttemptCreate(BaseModel):
    test_mode: str = "full"

class Attempt(BaseModel):
    id: str
    test_mode: str
    started_at: datetime
    status: str = "in_progress"

# Endpoints
@app.get("/")
async def root():
    return {
        "name": "QanotAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "http://localhost:8000/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/questions/next", response_model=QuestionSet)
async def get_questions():
    """Get question set for a test"""
    import random
    return QuestionSet(
        part1=random.sample(questions_db["part1"], 2),
        part2=random.choice(questions_db["part2"]),
        part3=random.sample(questions_db["part3"], 2)
    )

@app.post("/api/v1/attempts", response_model=Attempt)
async def create_attempt(attempt: AttemptCreate):
    """Create a new test attempt"""
    new_attempt = Attempt(
        id=str(uuid.uuid4()),
        test_mode=attempt.test_mode,
        started_at=datetime.now(),
        status="in_progress"
    )
    attempts_db.append(new_attempt)
    return new_attempt

@app.get("/api/v1/attempts")
async def list_attempts():
    """List all attempts"""
    return attempts_db

@app.get("/api/v1/questions/topics")
async def get_topics():
    """Get available topics"""
    return ["Work/Study", "Hometown", "Technology", "People", "Travel", "Culture"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)