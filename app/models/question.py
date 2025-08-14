"""
Question model for IELTS Speaking test questions
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Question details
    part = Column(Integer, nullable=False)  # 1, 2, or 3
    text = Column(Text, nullable=False)
    topic = Column(String, nullable=True)
    sub_topic = Column(String, nullable=True)
    
    # For Part 2 cue cards
    bullet_points = Column(JSON, nullable=True)  # List of bullet points
    preparation_time_seconds = Column(Integer, default=60)
    speaking_time_seconds = Column(Integer, default=120)
    
    # For Part 1 and 3
    expected_duration_seconds = Column(Integer, default=30)
    follow_up_questions = Column(JSON, nullable=True)  # Related questions
    
    # Metadata
    difficulty_level = Column(Integer, default=5)  # 1-9 scale
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer, nullable=True)  # Average band score
    
    # Tags and categorization
    tags = Column(JSON, nullable=True)  # ["travel", "education", etc.]
    is_trending = Column(Boolean, default=False)
    is_recent_exam = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Source tracking
    source = Column(String, nullable=True)  # "official", "user_submitted", etc.
    submitted_by = Column(UUID(as_uuid=True), nullable=True)