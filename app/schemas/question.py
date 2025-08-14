"""
Pydantic schemas for Question model
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class QuestionBase(BaseModel):
    part: int = Field(..., ge=1, le=3)
    text: str
    topic: Optional[str] = None
    sub_topic: Optional[str] = None
    difficulty_level: int = Field(5, ge=1, le=9)


class QuestionResponse(QuestionBase):
    id: UUID
    bullet_points: Optional[List[str]] = None
    preparation_time_seconds: Optional[int] = None
    speaking_time_seconds: Optional[int] = None
    expected_duration_seconds: Optional[int] = None
    follow_up_questions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_trending: bool = False
    is_recent_exam: bool = False
    
    class Config:
        from_attributes = True


class QuestionSet(BaseModel):
    """Set of questions for a test attempt"""
    part1: Optional[List[QuestionResponse]] = None
    part2: Optional[QuestionResponse] = None
    part3: Optional[List[QuestionResponse]] = None
    test_mode: str = "full"
    
    class Config:
        from_attributes = True