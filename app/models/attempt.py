"""
Test attempt model for tracking user IELTS speaking tests
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class AttemptStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PROCESSING = "processing"
    SCORED = "scored"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Test configuration
    test_mode = Column(String, default="full")  # full, part1, part2, part3, quick
    target_band = Column(Integer, nullable=True)
    
    # Questions used
    part1_questions = Column(JSON, nullable=True)  # List of question IDs
    part2_question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=True)
    part3_questions = Column(JSON, nullable=True)  # List of question IDs
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_duration_seconds = Column(Integer, nullable=True)
    
    # Status
    status = Column(Enum(AttemptStatus), default=AttemptStatus.PENDING)
    
    # Audio files
    part1_audio_keys = Column(JSON, nullable=True)  # S3/Spaces keys
    part2_audio_key = Column(String, nullable=True)
    part3_audio_keys = Column(JSON, nullable=True)
    
    # Processing
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    celery_task_id = Column(String, nullable=True)
    
    # Metadata
    client_info = Column(JSON, nullable=True)  # app version, device, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="attempts")
    score = relationship("Score", back_populates="attempt", uselist=False)
    transcripts = relationship("Transcript", back_populates="attempt")


class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("attempts.id"), nullable=False)
    
    # Part identification
    part = Column(Integer, nullable=False)  # 1, 2, or 3
    question_index = Column(Integer, default=0)  # For multiple questions in part
    
    # Transcription
    text = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Analysis
    word_count = Column(Integer, nullable=True)
    words_per_minute = Column(Float, nullable=True)
    filler_words = Column(JSON, nullable=True)  # ["um", "uh", counts]
    pause_count = Column(Integer, nullable=True)
    hesitation_count = Column(Integer, nullable=True)
    
    # Language analysis
    vocabulary_level = Column(String, nullable=True)  # A1-C2
    unique_words = Column(Integer, nullable=True)
    complex_sentences = Column(Integer, nullable=True)
    grammar_errors = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    attempt = relationship("Attempt", back_populates="transcripts")