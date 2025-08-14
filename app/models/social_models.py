"""
Models for Epic 7: Social & Community Features
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


class SharePlatform(str, Enum):
    """Social media platforms for sharing"""
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    LINKEDIN = "linkedin"


class PrivacyLevel(str, Enum):
    """Privacy levels for sharing"""
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class LeaderboardPeriod(str, Enum):
    """Leaderboard time periods"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


class StudyGroupRole(str, Enum):
    """Study group member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class GroupMessageType(str, Enum):
    """Group message types"""
    TEXT = "text"
    SCORE_SHARE = "score_share"
    CHALLENGE = "challenge"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"


class ScoreCard(BaseModel):
    """US-7.1: Share Results - Score card for social sharing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Test details
    test_attempt_id: str
    overall_band: float
    test_date: datetime
    test_type: str = "full_test"  # "full_test", "daily_challenge", "practice"
    
    # Detailed scores
    fluency_coherence: float = 0.0
    lexical_resource: float = 0.0
    grammatical_range_accuracy: float = 0.0
    pronunciation: float = 0.0
    
    # Achievement context
    achievement_title: Optional[str] = None  # e.g., "Personal Best!", "First 7.0!"
    improvement_note: Optional[str] = None  # e.g., "+0.5 from last month"
    
    # Visual customization
    card_template: str = "default"  # "default", "achievement", "milestone"
    background_color: str = "#6366f1"
    accent_color: str = "#8b5cf6"
    
    # Privacy settings
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC
    show_detailed_scores: bool = True
    show_improvement: bool = True
    
    # App branding
    include_branding: bool = True
    branding_text: str = "Powered by QanotAI"
    
    # Sharing metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None  # Generated image URL
    share_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SocialShare(BaseModel):
    """Social sharing activity tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    score_card_id: str
    
    # Sharing details
    platform: SharePlatform
    shared_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Privacy and audience
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC
    audience_count: Optional[int] = None  # Estimated reach
    
    # Engagement tracking (if available from platform)
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    
    # Success tracking
    share_successful: bool = True
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LeaderboardEntry(BaseModel):
    """US-7.2: Leaderboards - Individual leaderboard entry"""
    user_id: str
    
    # Display information
    display_name: str  # Can be anonymous
    is_anonymous: bool = False
    avatar_url: Optional[str] = None
    
    # Ranking details
    rank: int
    score: float
    score_type: str = "average_band"  # "average_band", "best_score", "total_tests"
    
    # Performance metrics
    total_tests: int = 0
    tests_this_period: int = 0
    improvement_trend: float = 0.0  # +/- change
    
    # Regional information
    country: Optional[str] = None
    region: Optional[str] = None
    
    # Achievement indicators
    badges_count: int = 0
    streak_days: int = 0
    
    # Participation consent
    opted_in: bool = True
    last_active: datetime = Field(default_factory=datetime.utcnow)


class Leaderboard(BaseModel):
    """Leaderboard container"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Leaderboard configuration
    period: LeaderboardPeriod
    region: Optional[str] = None
    country: Optional[str] = None
    
    # Time range
    start_date: date
    end_date: date
    
    # Entries
    entries: List[LeaderboardEntry] = []
    total_participants: int = 0
    
    # Statistics
    average_score: float = 0.0
    highest_score: float = 0.0
    most_active_user: Optional[str] = None
    
    # Update tracking
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    next_update: datetime
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StudyGroup(BaseModel):
    """US-7.3: Study Groups - Study group management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Group details
    name: str
    description: str
    group_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    
    # Settings
    max_members: int = 20
    is_public: bool = True
    requires_approval: bool = False
    
    # Group goals
    target_band_score: Optional[float] = None
    target_test_date: Optional[date] = None
    focus_areas: List[str] = []  # e.g., ["pronunciation", "vocabulary"]
    
    # Activity settings
    weekly_challenge: bool = True
    score_sharing: bool = True
    group_chat: bool = True
    
    # Statistics
    member_count: int = 0
    total_tests_completed: int = 0
    average_group_score: float = 0.0
    
    # Group performance
    group_streak_days: int = 0
    achievements_earned: List[str] = []
    
    # Status
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StudyGroupMember(BaseModel):
    """Study group membership"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    
    # Membership details
    role: StudyGroupRole = StudyGroupRole.MEMBER
    display_name: str
    
    # Join information
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None
    
    # Participation
    is_active: bool = True
    last_active: Optional[datetime] = None
    
    # Member stats
    tests_completed_in_group: int = 0
    average_score_in_group: float = 0.0
    contributions_count: int = 0  # Messages, tips, etc.
    
    # Preferences
    receive_notifications: bool = True
    share_scores_auto: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GroupChallenge(BaseModel):
    """Group challenges and goals"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    created_by: str
    
    # Challenge details
    title: str
    description: str
    challenge_type: str = "weekly_goal"  # "weekly_goal", "practice_streak", "score_target"
    
    # Challenge parameters
    target_value: float  # Score target, test count, etc.
    target_metric: str  # "average_score", "test_count", "streak_days"
    
    # Timeline
    start_date: date
    end_date: date
    
    # Participation
    participants: List[str] = []  # User IDs
    completed_by: List[str] = []  # User IDs who completed
    
    # Progress tracking
    current_progress: float = 0.0
    is_completed: bool = False
    completion_rate: float = 0.0
    
    # Rewards
    reward_description: Optional[str] = None
    badge_earned: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GroupMessage(BaseModel):
    """US-7.3: Group chat messages"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    
    # Message content
    message_type: GroupMessageType = GroupMessageType.TEXT
    content: str
    
    # Attachments/references
    score_card_id: Optional[str] = None  # For score shares
    challenge_id: Optional[str] = None  # For challenge messages
    
    # Message metadata
    sender_name: str
    is_system_message: bool = False
    
    # Engagement
    likes_count: int = 0
    liked_by: List[str] = []  # User IDs
    
    # Moderation
    is_flagged: bool = False
    is_deleted: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None


class UserSocialSettings(BaseModel):
    """User social and privacy preferences"""
    user_id: str
    
    # Leaderboard preferences
    participate_in_leaderboards: bool = True
    show_in_country_leaderboard: bool = True
    show_in_global_leaderboard: bool = True
    leaderboard_display_name: Optional[str] = None
    show_anonymous: bool = False
    
    # Sharing preferences
    auto_share_achievements: bool = False
    auto_share_personal_bests: bool = True
    default_privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC
    
    # Study group preferences
    allow_group_invites: bool = True
    auto_share_scores_in_groups: bool = False
    receive_group_notifications: bool = True
    
    # Social discovery
    allow_friend_requests: bool = True
    show_profile_publicly: bool = True
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models for API endpoints

class CreateScoreCardRequest(BaseModel):
    """Request to create a score card"""
    test_attempt_id: str
    achievement_title: Optional[str] = None
    card_template: str = "default"
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC
    show_detailed_scores: bool = True


class ShareScoreRequest(BaseModel):
    """Request to share a score card"""
    score_card_id: str
    platforms: List[SharePlatform]
    privacy_level: Optional[PrivacyLevel] = None
    custom_message: Optional[str] = None


class LeaderboardRequest(BaseModel):
    """Request for leaderboard data"""
    period: LeaderboardPeriod = LeaderboardPeriod.WEEKLY
    region: Optional[str] = None
    country: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=100)


class CreateStudyGroupRequest(BaseModel):
    """Request to create a study group"""
    name: str
    description: str
    is_public: bool = True
    requires_approval: bool = False
    target_band_score: Optional[float] = None
    target_test_date: Optional[date] = None
    focus_areas: List[str] = []


class JoinStudyGroupRequest(BaseModel):
    """Request to join a study group"""
    group_code: Optional[str] = None
    group_id: Optional[str] = None
    message: Optional[str] = None  # For approval-required groups


class GroupMessageRequest(BaseModel):
    """Request to send group message"""
    content: str
    message_type: GroupMessageType = GroupMessageType.TEXT
    score_card_id: Optional[str] = None


class UpdateSocialSettingsRequest(BaseModel):
    """Request to update social settings"""
    participate_in_leaderboards: Optional[bool] = None
    show_anonymous: Optional[bool] = None
    auto_share_achievements: Optional[bool] = None
    default_privacy_level: Optional[PrivacyLevel] = None


# Response models

class ScoreCardResponse(BaseModel):
    """Response for score card creation"""
    score_card: ScoreCard
    image_url: str
    share_urls: Dict[str, str]  # Platform-specific share URLs


class LeaderboardResponse(BaseModel):
    """Response for leaderboard data"""
    leaderboard: Leaderboard
    user_rank: Optional[int] = None
    user_entry: Optional[LeaderboardEntry] = None
    rank_change: Optional[int] = None  # +/- from previous period


class StudyGroupResponse(BaseModel):
    """Response for study group details"""
    group: StudyGroup
    members: List[StudyGroupMember]
    recent_messages: List[GroupMessage] = []
    active_challenges: List[GroupChallenge] = []
    user_role: Optional[StudyGroupRole] = None


class SocialStatsResponse(BaseModel):
    """Response for user's social statistics"""
    total_shares: int
    leaderboard_rank: Optional[int]
    study_groups_count: int
    achievements_shared: int
    social_score: float  # Overall social engagement score