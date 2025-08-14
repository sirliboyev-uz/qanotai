"""
Score model for IELTS band score predictions and feedback
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Score(Base):
    __tablename__ = "scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("attempts.id"), unique=True, nullable=False)
    
    # Overall band scores
    overall_band = Column(Float, nullable=False)  # 0-9 with 0.5 increments
    
    # Individual criteria scores (0-9)
    fluency_coherence = Column(Float, nullable=False)
    lexical_resource = Column(Float, nullable=False)
    grammatical_range_accuracy = Column(Float, nullable=False)
    pronunciation = Column(Float, nullable=False)
    
    # Detailed scoring breakdown
    part1_score = Column(Float, nullable=True)
    part2_score = Column(Float, nullable=True)
    part3_score = Column(Float, nullable=True)
    
    # Feedback
    summary_feedback = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)  # List of strength points
    improvements = Column(JSON, nullable=True)  # List of improvement areas
    
    # Detailed feedback per criterion
    fluency_feedback = Column(Text, nullable=True)
    lexical_feedback = Column(Text, nullable=True)
    grammar_feedback = Column(Text, nullable=True)
    pronunciation_feedback = Column(Text, nullable=True)
    
    # Specific issues identified
    common_errors = Column(JSON, nullable=True)
    vocabulary_suggestions = Column(JSON, nullable=True)
    grammar_corrections = Column(JSON, nullable=True)
    
    # Uzbek-specific feedback (localized)
    uzbek_learner_tips = Column(JSON, nullable=True)
    
    # Recommendations
    recommended_topics = Column(JSON, nullable=True)
    practice_exercises = Column(JSON, nullable=True)
    estimated_improvement_time = Column(String, nullable=True)  # "2-3 weeks"
    
    # AI Provider metadata
    ai_provider = Column(String, nullable=True)  # openai, anthropic
    ai_model = Column(String, nullable=True)  # gpt-4, claude-3
    scoring_version = Column(String, nullable=True)  # rubric version
    ai_confidence = Column(Float, nullable=True)  # 0-1 confidence score
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    attempt = relationship("Attempt", back_populates="score")