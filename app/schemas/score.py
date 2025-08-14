"""
Pydantic schemas for Score model
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ScoreBase(BaseModel):
    overall_band: float = Field(..., ge=0, le=9)
    fluency_coherence: float = Field(..., ge=0, le=9)
    lexical_resource: float = Field(..., ge=0, le=9)
    grammatical_range_accuracy: float = Field(..., ge=0, le=9)
    pronunciation: float = Field(..., ge=0, le=9)


class ScoreCreate(ScoreBase):
    attempt_id: UUID
    summary_feedback: str
    strengths: List[str]
    improvements: List[str]
    ai_provider: str
    ai_model: str
    scoring_version: str


class ScoreResponse(ScoreBase):
    id: UUID
    attempt_id: UUID
    part1_score: Optional[float] = None
    part2_score: Optional[float] = None
    part3_score: Optional[float] = None
    summary_feedback: Optional[str] = None
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    fluency_feedback: Optional[str] = None
    lexical_feedback: Optional[str] = None
    grammar_feedback: Optional[str] = None
    pronunciation_feedback: Optional[str] = None
    common_errors: Optional[List[Dict[str, str]]] = None
    vocabulary_suggestions: Optional[List[str]] = None
    grammar_corrections: Optional[List[Dict[str, str]]] = None
    uzbek_learner_tips: Optional[List[str]] = None
    recommended_topics: Optional[List[str]] = None
    practice_exercises: Optional[List[str]] = None
    estimated_improvement_time: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreSummary(BaseModel):
    """Summary for progress tracking"""
    attempt_id: UUID
    date: datetime
    overall_band: float
    test_mode: str
    improvement: Optional[float] = None  # Change from previous test