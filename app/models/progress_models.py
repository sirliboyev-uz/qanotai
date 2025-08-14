"""
Models for Epic 4: Progress Tracking
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


class BadgeType(str, Enum):
    """Types of achievement badges"""
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30" 
    STREAK_100 = "streak_100"
    SCORE_IMPROVEMENT = "score_improvement"
    TESTS_10 = "tests_10"
    TESTS_50 = "tests_50"
    TESTS_100 = "tests_100"
    BAND_6 = "band_6"
    BAND_7 = "band_7"
    BAND_8 = "band_8"
    PERFECT_PART = "perfect_part"
    FIRST_TEST = "first_test"
    CONSISTENT_USER = "consistent_user"


class TestAttemptHistory(BaseModel):
    """US-4.1: Test History - Individual test attempt record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    attempt_id: str  # Links to test attempt
    
    # Test Details
    test_date: datetime
    test_mode: str  # "full", "part1", "part2", "part3"
    target_band_score: Optional[float] = None
    
    # Results
    overall_band: float = 0.0
    fluency_coherence: float = 0.0
    lexical_resource: float = 0.0
    grammatical_range_accuracy: float = 0.0
    pronunciation: float = 0.0
    
    # Part-wise scores
    part1_score: Optional[float] = None
    part2_score: Optional[float] = None
    part3_score: Optional[float] = None
    
    # Performance metrics
    total_questions: int = 0
    completion_percentage: float = 100.0
    test_duration_minutes: int = 0
    
    # Analysis data
    word_count_total: int = 0
    unique_words_used: int = 0
    filler_words_count: int = 0
    hesitations_count: int = 0
    speaking_rate_wpm: float = 0.0
    
    # Status
    is_completed: bool = True
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProgressMetrics(BaseModel):
    """US-4.2: Progress Dashboard metrics"""
    user_id: str
    
    # Current status
    current_band: float = 0.0
    target_band: float = 7.0
    gap_to_target: float = 0.0
    
    # Streak data
    current_streak: int = 0
    longest_streak: int = 0
    last_practice_date: Optional[date] = None
    
    # Test statistics
    total_tests: int = 0
    tests_this_week: int = 0
    tests_this_month: int = 0
    
    # Score trends (last 10 tests)
    score_trend: List[float] = []
    score_dates: List[date] = []
    
    # Average scores by criteria
    avg_fluency: float = 0.0
    avg_lexical: float = 0.0
    avg_grammar: float = 0.0
    avg_pronunciation: float = 0.0
    
    # Improvement indicators
    score_improvement_7_days: float = 0.0
    score_improvement_30_days: float = 0.0
    
    # Practice consistency
    practice_days_this_month: int = 0
    average_practice_per_week: float = 0.0
    
    # Target achievement
    target_test_date: Optional[date] = None
    days_until_target: Optional[int] = None
    estimated_days_to_target: Optional[int] = None
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PerformanceAnalytics(BaseModel):
    """US-4.3: Performance Analytics"""
    user_id: str
    analysis_period_days: int = 30  # Analysis period
    
    # Score breakdown by parts
    part1_performance: Dict[str, float] = {}  # {"average": 6.5, "improvement": 0.3}
    part2_performance: Dict[str, float] = {}
    part3_performance: Dict[str, float] = {}
    
    # Common mistake patterns
    grammar_error_patterns: List[Dict[str, Any]] = []  # [{"error": "article", "frequency": 15}]
    vocabulary_gaps: List[str] = []  # Topics or word types lacking
    pronunciation_issues: List[str] = []  # Specific sounds or patterns
    
    # Fluency analysis
    hesitation_patterns: Dict[str, Any] = {}  # {"avg_per_minute": 2.5, "trend": "improving"}
    filler_word_usage: Dict[str, int] = {}  # {"um": 12, "like": 8, "you know": 5}
    speaking_pace_analysis: Dict[str, float] = {}  # {"avg_wpm": 140, "consistency": 0.8}
    
    # Time management
    response_time_analysis: Dict[str, float] = {}  # {"part1_avg": 25, "part2_prep": 58}
    completion_rate_by_part: Dict[str, float] = {}  # {"part1": 100, "part2": 95}
    
    # Question type performance
    question_type_scores: Dict[str, float] = {}  # {"personal_info": 7.0, "abstract": 6.0}
    difficult_topics: List[str] = []  # Topics with consistently lower scores
    strong_topics: List[str] = []  # Topics with consistently higher scores
    
    # Recommendations
    focus_areas: List[str] = []  # Areas needing most improvement
    practice_suggestions: List[str] = []  # Specific practice activities
    
    # Trends
    improvement_velocity: float = 0.0  # Rate of improvement (points per week)
    consistency_score: float = 0.0  # How consistent performance is (0-1)
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AchievementBadge(BaseModel):
    """US-4.4: Achievement Badges"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_type: BadgeType
    
    # Badge details
    title: str
    description: str
    icon: str  # Icon identifier
    color: str  # Hex color code
    
    # Achievement data
    earned_date: datetime
    milestone_value: Optional[int] = None  # e.g., 7 for streak_7, 100 for tests_100
    
    # Display properties
    is_featured: bool = False  # Show prominently
    rarity: str = "common"  # "common", "rare", "legendary"
    
    # Related data
    trigger_test_id: Optional[str] = None  # Test that triggered this badge
    progress_snapshot: Optional[Dict[str, Any]] = None  # User stats when earned
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserGoal(BaseModel):
    """Goal setting and tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Goal details
    target_band_score: float
    target_date: date
    current_band_score: float
    
    # Milestone tracking
    milestones: List[Dict[str, Any]] = []  # [{"score": 6.5, "date": "2024-01-15", "achieved": true}]
    
    # Progress tracking
    is_active: bool = True
    is_achieved: bool = False
    achieved_date: Optional[datetime] = None
    
    # Motivation
    reason: Optional[str] = None  # Why they set this goal
    reward: Optional[str] = None  # What they'll do when achieved
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DailyPracticeLog(BaseModel):
    """Daily practice tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    practice_date: date
    
    # Practice details
    tests_completed: int = 0
    total_practice_minutes: int = 0
    
    # Performance summary
    best_score_today: Optional[float] = None
    average_score_today: Optional[float] = None
    
    # Streaks
    is_streak_day: bool = True
    streak_count: int = 1
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models for API endpoints

class ProgressDashboardResponse(BaseModel):
    """Response for US-4.2: Progress Dashboard"""
    metrics: ProgressMetrics
    recent_tests: List[TestAttemptHistory]
    badges: List[AchievementBadge]
    current_goal: Optional[UserGoal]


class PerformanceAnalyticsResponse(BaseModel):
    """Response for US-4.3: Performance Analytics"""
    analytics: PerformanceAnalytics
    recommendations: List[str]
    improvement_plan: List[Dict[str, Any]]


class TestHistoryResponse(BaseModel):
    """Response for US-4.1: Test History"""
    tests: List[TestAttemptHistory]
    total_count: int
    page: int
    per_page: int
    has_more: bool


class SetGoalRequest(BaseModel):
    """Request to set a new goal"""
    target_band_score: float = Field(ge=0.0, le=9.0)
    target_date: date
    reason: Optional[str] = None
    reward: Optional[str] = None


class BadgeEarnedNotification(BaseModel):
    """Notification when a badge is earned"""
    badge: AchievementBadge
    message: str
    is_new_achievement: bool
    celebration_level: str  # "small", "medium", "large"