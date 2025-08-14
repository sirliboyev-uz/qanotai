"""
Pydantic schemas for Attempt model
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from app.models.attempt import AttemptStatus
from app.schemas.score import ScoreResponse


class AttemptCreate(BaseModel):
    test_mode: str = Field("full", description="full, part1, part2, part3, quick")
    target_band: Optional[int] = Field(None, ge=1, le=9)
    part1_question_ids: Optional[List[UUID]] = None
    part2_question_id: Optional[UUID] = None
    part3_question_ids: Optional[List[UUID]] = None
    client_info: Optional[Dict[str, Any]] = None


class AttemptComplete(BaseModel):
    part1_audio_keys: Optional[List[str]] = None
    part2_audio_key: Optional[str] = None
    part3_audio_keys: Optional[List[str]] = None


class AttemptResponse(BaseModel):
    id: UUID
    status: AttemptStatus
    test_mode: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None
    upload_urls: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AttemptWithScore(AttemptResponse):
    score: Optional[ScoreResponse] = None
    celery_task_id: Optional[str] = None
    
    class Config:
        from_attributes = True