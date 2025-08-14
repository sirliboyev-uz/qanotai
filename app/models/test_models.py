"""
Models for Epic 2: IELTS Speaking Test Simulation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class TestPart(str, Enum):
    PART1 = "part1"
    PART2 = "part2"
    PART3 = "part3"


class TestMode(str, Enum):
    FULL = "full"
    PART1_ONLY = "part1"
    PART2_ONLY = "part2"
    PART3_ONLY = "part3"
    QUICK = "quick"  # Shorter version for practice


class Question(BaseModel):
    """IELTS Speaking question model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    part: TestPart
    text: str
    topic: str
    sub_topic: Optional[str] = None
    
    # Part 2 specific fields
    bullet_points: Optional[List[str]] = None
    preparation_time_seconds: int = 60
    speaking_time_seconds: int = 120
    
    # Part 1 and 3 specific
    expected_duration_seconds: int = 30
    follow_up_questions: Optional[List[str]] = None
    
    # Metadata
    difficulty_level: int = Field(5, ge=1, le=9)
    tags: List[str] = []
    is_trending: bool = False


class QuestionSet(BaseModel):
    """Set of questions for a complete test"""
    part1_questions: List[Question] = []
    part2_question: Optional[Question] = None
    part3_questions: List[Question] = []
    test_mode: TestMode = TestMode.FULL


class TestAttempt(BaseModel):
    """Test attempt tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    test_mode: TestMode
    question_set: QuestionSet
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Status
    current_part: Optional[TestPart] = None
    current_question_index: int = 0
    is_recording: bool = False
    
    # Audio recordings (simulated for now)
    recordings: Dict[str, Any] = {}
    
    # Scores (will be added in Epic 3)
    score: Optional[Dict[str, Any]] = None


class RecordingSession(BaseModel):
    """Voice recording session for US-2.5"""
    attempt_id: str
    part: TestPart
    question_index: int
    
    # Recording metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: Optional[int] = None
    audio_url: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_completed: bool = False


class TimerState(BaseModel):
    """Timer state for test parts"""
    part: TestPart
    total_seconds: int
    remaining_seconds: int
    is_running: bool = False
    started_at: Optional[datetime] = None
    
    # Part-specific timers
    preparation_time: Optional[int] = None  # For Part 2
    speaking_time: Optional[int] = None     # For Part 2