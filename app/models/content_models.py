"""
Models for Epic 6: Content & Question Bank
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


class TestPart(str, Enum):
    """IELTS Speaking test parts"""
    PART_1 = "part_1"
    PART_2 = "part_2" 
    PART_3 = "part_3"


class QuestionDifficulty(str, Enum):
    """Question difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TopicCategory(str, Enum):
    """IELTS topic categories"""
    PERSONAL_INFO = "personal_info"
    FAMILY = "family"
    WORK_STUDY = "work_study"
    HOBBIES = "hobbies"
    TRAVEL = "travel"
    FOOD = "food"
    TECHNOLOGY = "technology"
    ENVIRONMENT = "environment"
    EDUCATION = "education"
    HEALTH = "health"
    CULTURE = "culture"
    MEDIA = "media"
    SPORTS = "sports"
    SHOPPING = "shopping"
    TRANSPORTATION = "transportation"
    FUTURE_PLANS = "future_plans"
    RELATIONSHIPS = "relationships"
    ENTERTAINMENT = "entertainment"
    SOCIETY = "society"
    ABSTRACT_CONCEPTS = "abstract_concepts"


class QuestionTopic(BaseModel):
    """US-6.1: Browse Question Topics - Topic organization"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Topic details
    name: str
    category: TopicCategory
    description: str
    
    # Metadata
    difficulty_level: QuestionDifficulty = QuestionDifficulty.INTERMEDIATE
    estimated_time_minutes: int = 15
    
    # Popularity and trending
    popularity_score: float = 0.0  # Based on user engagement
    is_trending: bool = False
    trend_score: float = 0.0
    
    # Organization
    tags: List[str] = []
    keywords: List[str] = []
    
    # Usage statistics
    total_attempts: int = 0
    average_score: float = 0.0
    last_used: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Question(BaseModel):
    """Individual IELTS speaking question"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Question content
    text: str
    follow_up_questions: List[str] = []
    
    # Classification
    part: TestPart
    topic_id: str
    category: TopicCategory
    difficulty: QuestionDifficulty = QuestionDifficulty.INTERMEDIATE
    
    # For Part 2 cue cards
    cue_card_title: Optional[str] = None
    cue_card_points: List[str] = []
    preparation_time_seconds: int = 60  # Part 2 prep time
    speaking_time_minutes: int = 2  # Part 2 speaking time
    
    # Metadata
    tags: List[str] = []
    keywords: List[str] = []
    
    # Analytics
    usage_count: int = 0
    average_score: float = 0.0
    average_response_time_seconds: int = 0
    
    # Regional variations
    region_specific: Optional[str] = None  # e.g., "UK", "Australia"
    cultural_context: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_verified: bool = True
    verification_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DailyChallenge(BaseModel):
    """US-6.2: Daily Challenge system"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Challenge details
    challenge_date: date
    title: str
    description: str
    
    # Questions for the challenge
    part_1_questions: List[str] = []  # Question IDs
    part_2_question: Optional[str] = None  # Question ID
    part_3_questions: List[str] = []  # Question IDs
    
    # Challenge configuration
    estimated_duration_minutes: int = 5
    difficulty_level: QuestionDifficulty = QuestionDifficulty.INTERMEDIATE
    
    # Theme and focus
    theme: str  # e.g., "Travel Adventures", "Technology in Daily Life"
    focus_skills: List[str] = []  # e.g., ["fluency", "vocabulary", "grammar"]
    
    # Participation tracking
    total_participants: int = 0
    completion_rate: float = 0.0
    average_score: float = 0.0
    
    # Notifications
    notification_sent: bool = False
    notification_time: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserChallenge(BaseModel):
    """User's participation in daily challenges"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    challenge_id: str
    
    # Participation details
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Performance
    is_completed: bool = False
    overall_score: float = 0.0
    completion_time_minutes: int = 0
    
    # Individual responses
    responses: List[Dict[str, Any]] = []  # Question responses with scores
    
    # Streak tracking
    is_streak_day: bool = False
    current_streak: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TrendingTopic(BaseModel):
    """US-6.3: Trending Topics tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    
    # Trending metrics
    trend_period: str = "weekly"  # "daily", "weekly", "monthly"
    trend_score: float = 0.0
    position_change: int = 0  # +/- from previous period
    
    # Regional data
    region: Optional[str] = None
    country: Optional[str] = None
    
    # Sources
    data_sources: List[str] = []  # e.g., ["user_reports", "official_ielts", "forums"]
    confidence_score: float = 0.8
    
    # Temporal data
    trend_start_date: date
    last_reported: datetime = Field(default_factory=datetime.utcnow)
    
    # User submission tracking
    user_submitted: bool = False
    submission_count: int = 0
    verification_status: str = "pending"  # "pending", "verified", "rejected"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserTopicPreference(BaseModel):
    """US-6.1: Favorite topics feature"""
    user_id: str
    topic_id: str
    
    # Preference details
    is_favorite: bool = False
    interest_level: int = Field(default=3, ge=1, le=5)  # 1-5 scale
    
    # Usage tracking
    practice_count: int = 0
    last_practiced: Optional[datetime] = None
    average_score: float = 0.0
    
    # Learning progress
    mastery_level: float = 0.0  # 0-1 scale
    improvement_rate: float = 0.0
    
    # Personalization
    custom_notes: Optional[str] = None
    difficulty_preference: Optional[QuestionDifficulty] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionSubmission(BaseModel):
    """User-submitted questions for trending topics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Submission details
    question_text: str
    suggested_part: TestPart
    suggested_category: TopicCategory
    suggested_topic: Optional[str] = None
    
    # Context
    test_location: Optional[str] = None
    test_date: Optional[date] = None
    examiner_accent: Optional[str] = None
    
    # Verification
    status: str = "pending"  # "pending", "approved", "rejected", "needs_review"
    moderator_notes: Optional[str] = None
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # Community feedback
    upvotes: int = 0
    downvotes: int = 0
    helpful_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models for API endpoints

class TopicBrowseRequest(BaseModel):
    """Request for browsing topics"""
    category: Optional[TopicCategory] = None
    part: Optional[TestPart] = None
    difficulty: Optional[QuestionDifficulty] = None
    search_query: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="popularity")  # "popularity", "name", "difficulty", "trending"
    include_favorites: bool = False


class TopicBrowseResponse(BaseModel):
    """Response for topic browsing"""
    topics: List[QuestionTopic]
    total_count: int
    page: int
    per_page: int
    has_more: bool
    categories: List[str]  # Available categories
    trending_topics: List[str]  # Trending topic IDs


class QuestionResponse(BaseModel):
    """Response for individual question"""
    question: Question
    topic: QuestionTopic
    related_questions: List[Question] = []
    user_stats: Optional[Dict[str, Any]] = None


class DailyChallengeResponse(BaseModel):
    """Response for daily challenge"""
    challenge: DailyChallenge
    questions: List[Question]
    user_participation: Optional[UserChallenge] = None
    leaderboard: List[Dict[str, Any]] = []


class TrendingTopicsResponse(BaseModel):
    """Response for trending topics"""
    trending: List[TrendingTopic]
    topics: List[QuestionTopic]
    regions: List[str]
    last_updated: datetime


class StartChallengeRequest(BaseModel):
    """Request to start daily challenge"""
    challenge_id: str
    difficulty_preference: Optional[QuestionDifficulty] = None


class SubmitChallengeResponse(BaseModel):
    """Request to submit challenge completion"""
    challenge_id: str
    responses: List[Dict[str, Any]]
    completion_time_minutes: int


class FavoriteTopicRequest(BaseModel):
    """Request to add/remove favorite topic"""
    topic_id: str
    is_favorite: bool
    interest_level: Optional[int] = Field(default=3, ge=1, le=5)


class SubmitQuestionRequest(BaseModel):
    """Request to submit new question"""
    question_text: str
    part: TestPart
    category: TopicCategory
    test_context: Optional[Dict[str, Any]] = None


# Mock data for initial content

SAMPLE_TOPICS = [
    {
        "name": "Family and Relationships",
        "category": TopicCategory.FAMILY,
        "description": "Questions about family members, relationships, and family traditions",
        "difficulty_level": QuestionDifficulty.BEGINNER,
        "tags": ["family", "relationships", "traditions", "personal"],
        "keywords": ["parents", "siblings", "relatives", "marriage", "children"],
        "popularity_score": 0.95,
        "is_trending": True
    },
    {
        "name": "Work and Career",
        "category": TopicCategory.WORK_STUDY,
        "description": "Professional life, career goals, and workplace experiences",
        "difficulty_level": QuestionDifficulty.INTERMEDIATE,
        "tags": ["career", "job", "workplace", "professional"],
        "keywords": ["occupation", "colleagues", "salary", "promotion", "skills"],
        "popularity_score": 0.88
    },
    {
        "name": "Technology in Daily Life",
        "category": TopicCategory.TECHNOLOGY,
        "description": "Impact of technology on modern life and communication",
        "difficulty_level": QuestionDifficulty.ADVANCED,
        "tags": ["technology", "digital", "communication", "modern"],
        "keywords": ["smartphone", "internet", "social media", "artificial intelligence"],
        "popularity_score": 0.82,
        "is_trending": True
    },
    {
        "name": "Travel and Tourism",
        "category": TopicCategory.TRAVEL,
        "description": "Travel experiences, destinations, and cultural exploration",
        "difficulty_level": QuestionDifficulty.INTERMEDIATE,
        "tags": ["travel", "tourism", "culture", "exploration"],
        "keywords": ["vacation", "destination", "culture", "adventure", "transportation"],
        "popularity_score": 0.90
    },
    {
        "name": "Environmental Issues",
        "category": TopicCategory.ENVIRONMENT,
        "description": "Climate change, conservation, and environmental responsibility",
        "difficulty_level": QuestionDifficulty.ADVANCED,
        "tags": ["environment", "climate", "conservation", "sustainability"],
        "keywords": ["pollution", "recycling", "renewable energy", "global warming"],
        "popularity_score": 0.75,
        "is_trending": True
    }
]

SAMPLE_QUESTIONS = [
    # Part 1 Questions
    {
        "text": "Can you tell me about your family?",
        "part": TestPart.PART_1,
        "category": TopicCategory.FAMILY,
        "difficulty": QuestionDifficulty.BEGINNER,
        "tags": ["family", "personal", "introduction"],
        "follow_up_questions": [
            "How many people are in your family?",
            "Who are you closest to in your family?",
            "Do you live with your family?"
        ]
    },
    {
        "text": "What do you do for work or study?",
        "part": TestPart.PART_1,
        "category": TopicCategory.WORK_STUDY,
        "difficulty": QuestionDifficulty.BEGINNER,
        "tags": ["work", "study", "personal"],
        "follow_up_questions": [
            "Do you enjoy your work/studies?",
            "What are your future career plans?",
            "What skills are important in your field?"
        ]
    },
    # Part 2 Questions
    {
        "text": "Describe a piece of technology that you find useful",
        "part": TestPart.PART_2,
        "category": TopicCategory.TECHNOLOGY,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "cue_card_title": "A useful piece of technology",
        "cue_card_points": [
            "What it is",
            "How you use it",
            "When you started using it",
            "And explain why you find it useful"
        ],
        "tags": ["technology", "personal experience", "description"]
    },
    {
        "text": "Describe a memorable trip you have taken",
        "part": TestPart.PART_2,
        "category": TopicCategory.TRAVEL,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "cue_card_title": "A memorable trip",
        "cue_card_points": [
            "Where you went",
            "Who you went with",
            "What you did there",
            "And explain why it was memorable"
        ],
        "tags": ["travel", "personal experience", "narrative"]
    },
    # Part 3 Questions
    {
        "text": "How has technology changed the way families communicate?",
        "part": TestPart.PART_3,
        "category": TopicCategory.TECHNOLOGY,
        "difficulty": QuestionDifficulty.ADVANCED,
        "tags": ["technology", "family", "communication", "social change"],
        "follow_up_questions": [
            "Do you think this is a positive or negative change?",
            "How might family communication change in the future?",
            "What are the advantages and disadvantages of digital communication?"
        ]
    },
    {
        "text": "What are the benefits of traveling for young people?",
        "part": TestPart.PART_3,
        "category": TopicCategory.TRAVEL,
        "difficulty": QuestionDifficulty.ADVANCED,
        "tags": ["travel", "youth", "benefits", "education"],
        "follow_up_questions": [
            "Should schools organize more educational trips?",
            "How does travel contribute to personal development?",
            "What challenges do young travelers face?"
        ]
    }
]