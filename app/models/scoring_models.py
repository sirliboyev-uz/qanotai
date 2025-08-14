"""
Models for Epic 3: AI-Powered Assessment
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class TranscriptSegment(BaseModel):
    """Speech transcription segment"""
    text: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    start_time: float
    end_time: float
    words: List[Dict[str, Any]] = []


class Transcript(BaseModel):
    """US-3.1: Speech Transcription"""
    model_config = {"protected_namespaces": ()}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    attempt_id: str
    part: str  # part1, part2, part3
    question_index: int
    
    # Transcription
    text: str
    segments: List[TranscriptSegment] = []
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    # Analysis
    word_count: int = 0
    words_per_minute: float = 0.0
    unique_words: int = 0
    
    # Language features
    filler_words: List[str] = []  # um, uh, you know
    hesitations: int = 0
    pauses: List[float] = []  # pause durations
    
    # Metadata
    transcription_service: str = "whisper"  # or "google"
    model_version: str = "whisper-1"
    processing_time_seconds: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BandScore(BaseModel):
    """US-3.2: Band Score Prediction"""
    model_config = {"protected_namespaces": ()}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    attempt_id: str
    
    # Overall band scores (0-9 with 0.5 increments)
    overall_band: float = Field(0.0, ge=0.0, le=9.0)
    
    # Individual criteria scores
    fluency_coherence: float = Field(0.0, ge=0.0, le=9.0)
    lexical_resource: float = Field(0.0, ge=0.0, le=9.0)
    grammatical_range_accuracy: float = Field(0.0, ge=0.0, le=9.0)
    pronunciation: float = Field(0.0, ge=0.0, le=9.0)
    
    # Part-wise scores
    part1_score: Optional[float] = None
    part2_score: Optional[float] = None
    part3_score: Optional[float] = None
    
    # Comparison
    target_band: Optional[float] = None
    gap_to_target: Optional[float] = None
    
    # AI metadata
    scoring_model: str = "gpt-4"  # or "claude-3"
    scoring_version: str = "v1.0"
    confidence_level: float = Field(0.0, ge=0.0, le=1.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackReport(BaseModel):
    """US-3.3: Detailed Feedback Report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    attempt_id: str
    score_id: str
    
    # Summary
    summary: str
    overall_impression: str
    
    # Strengths (highlighted in green)
    strengths: List[str] = []
    strength_examples: List[Dict[str, str]] = []  # {"criterion": "fluency", "example": "..."}
    
    # Areas for improvement (amber/red)
    improvements: List[str] = []
    improvement_examples: List[Dict[str, str]] = []
    
    # Specific feedback per criterion
    fluency_feedback: str = ""
    lexical_feedback: str = ""
    grammar_feedback: str = ""
    pronunciation_feedback: str = ""
    
    # Actionable suggestions
    action_items: List[str] = []
    recommended_practice: List[str] = []
    estimated_improvement_time: str = ""  # e.g., "2-3 weeks"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LanguageAnalysis(BaseModel):
    """US-3.4: Grammar & Vocabulary Analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    attempt_id: str
    transcript_id: str
    
    # Grammar analysis
    grammar_errors: List[Dict[str, Any]] = []  # {"error": "...", "correction": "...", "type": "..."}
    grammar_accuracy_percentage: float = 0.0
    complex_structures_used: List[str] = []
    sentence_variety_score: float = 0.0
    
    # Vocabulary analysis
    vocabulary_range: str = ""  # "limited", "adequate", "good", "excellent"
    advanced_words_used: List[str] = []
    repetitive_words: List[Dict[str, int]] = []  # {"word": count}
    collocations_used: List[str] = []
    idiomatic_expressions: List[str] = []
    
    # Word choice
    word_choice_errors: List[Dict[str, str]] = []  # {"incorrect": "...", "suggested": "..."}
    register_appropriateness: str = ""  # "appropriate", "too formal", "too casual"
    
    # Uzbek learner specific
    common_l1_interference: List[str] = []  # Common mistakes for Uzbek speakers
    recommended_focus_areas: List[str] = []
    
    # Statistics
    average_sentence_length: float = 0.0
    lexical_diversity: float = 0.0  # unique words / total words
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScoringRequest(BaseModel):
    """Request to score a test attempt"""
    attempt_id: str
    audio_urls: Dict[str, str]  # {"part1_0": "url", "part2": "url", ...}
    target_band: Optional[float] = None
    urgent: bool = False  # Priority processing


class ScoringResponse(BaseModel):
    """Response from scoring service"""
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    estimated_time_seconds: int
    result_url: Optional[str] = None