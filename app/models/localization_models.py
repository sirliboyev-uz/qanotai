"""
Models for Epic 8: Accessibility & Localization
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    UZBEK = "uz"
    RUSSIAN = "ru"
    KAZAKH = "kz"
    TURKISH = "tr"


class AccessibilityLevel(str, Enum):
    """Accessibility assistance levels"""
    NONE = "none"
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL = "full"


class TextSize(str, Enum):
    """Text size options"""
    SMALL = "small"
    NORMAL = "normal"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


class ContrastMode(str, Enum):
    """Display contrast modes"""
    NORMAL = "normal"
    HIGH = "high"
    DARK = "dark"
    CUSTOM = "custom"


class OfflineContentType(str, Enum):
    """Types of offline content"""
    QUESTION_PACK = "question_pack"
    AUDIO_SAMPLES = "audio_samples"
    VOCABULARY = "vocabulary"
    GRAMMAR_RULES = "grammar_rules"
    PRACTICE_TESTS = "practice_tests"


class TranslationEntry(BaseModel):
    """Individual translation entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Translation keys
    key: str  # e.g., "button.start_test", "message.welcome"
    namespace: str = "app"  # "app", "test", "feedback", etc.
    
    # Translations
    english_text: str
    uzbek_text: Optional[str] = None
    russian_text: Optional[str] = None
    kazakh_text: Optional[str] = None
    turkish_text: Optional[str] = None
    
    # Context and metadata
    description: Optional[str] = None
    context: Optional[str] = None  # UI context where used
    max_length: Optional[int] = None
    
    # Version control
    version: int = 1
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
    
    # Status
    is_active: bool = True
    requires_review: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserLanguagePreference(BaseModel):
    """User language preferences"""
    user_id: str
    
    # Primary language settings
    interface_language: Language = Language.ENGLISH
    feedback_language: Language = Language.ENGLISH
    
    # Regional preferences
    region: Optional[str] = None  # "UZ", "KZ", "TR", etc.
    timezone: str = "Asia/Tashkent"
    date_format: str = "DD/MM/YYYY"
    time_format: str = "24"  # "12" or "24"
    
    # Language learning context
    native_language: Optional[Language] = None
    target_ielts_band: Optional[float] = None
    
    # Auto-translation preferences
    auto_translate_feedback: bool = True
    auto_translate_questions: bool = False  # Questions stay in English
    show_original_with_translation: bool = True
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AccessibilitySettings(BaseModel):
    """User accessibility preferences"""
    user_id: str
    
    # Visual accessibility
    text_size: TextSize = TextSize.NORMAL
    contrast_mode: ContrastMode = ContrastMode.NORMAL
    use_high_contrast: bool = False
    reduce_animations: bool = False
    
    # Screen reader support
    enable_screen_reader: bool = False
    screen_reader_voice_speed: int = 1  # 0.5x to 2x
    announce_ui_changes: bool = True
    
    # Audio accessibility
    enable_audio_descriptions: bool = False
    audio_cue_volume: float = 0.7
    enable_sound_feedback: bool = True
    
    # Motor accessibility
    extended_touch_targets: bool = False
    extended_timeouts: bool = False
    timeout_extension_seconds: int = 30
    
    # Cognitive accessibility
    simplified_interface: bool = False
    show_progress_indicators: bool = True
    enable_focus_indicators: bool = True
    
    # Test-specific accessibility
    allow_extended_test_time: bool = False
    test_time_multiplier: float = 1.0  # 1.0 to 2.0
    enable_pause_breaks: bool = False
    break_interval_minutes: int = 15
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OfflineContent(BaseModel):
    """Offline content package"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Content details
    name: str
    description: str
    content_type: OfflineContentType
    
    # Content metadata
    language: Language = Language.ENGLISH
    difficulty_level: Optional[str] = None  # "beginner", "intermediate", "advanced"
    topic_areas: List[str] = []
    
    # Package information
    version: str = "1.0"
    size_mb: float
    download_url: str
    checksum: str
    
    # Content structure
    question_count: Optional[int] = None
    audio_duration_minutes: Optional[int] = None
    estimated_practice_time_minutes: Optional[int] = None
    
    # Availability
    is_free: bool = True
    requires_subscription: bool = False
    
    # Sync information
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    sync_required: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserOfflineContent(BaseModel):
    """User's downloaded offline content"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_id: str
    
    # Download status
    download_status: str = "pending"  # "pending", "downloading", "completed", "failed"
    download_progress: float = 0.0  # 0.0 to 1.0
    downloaded_at: Optional[datetime] = None
    
    # Local storage
    local_path: Optional[str] = None
    local_size_mb: Optional[float] = None
    
    # Usage tracking
    times_used: int = 0
    last_used: Optional[datetime] = None
    
    # Sync status
    needs_update: bool = False
    local_version: str = "1.0"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LocalizationStats(BaseModel):
    """Localization usage statistics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Usage by language
    language_usage: Dict[str, int] = {}  # Language code -> user count
    
    # Regional distribution
    region_distribution: Dict[str, int] = {}  # Region -> user count
    
    # Feature usage
    screen_reader_users: int = 0
    high_contrast_users: int = 0
    large_text_users: int = 0
    extended_timeout_users: int = 0
    
    # Translation completeness
    translation_completeness: Dict[str, float] = {}  # Language -> percentage
    
    # Offline content usage
    offline_downloads_total: int = 0
    most_popular_offline_content: List[str] = []
    
    # Update tracking
    last_calculated: datetime = Field(default_factory=datetime.utcnow)
    calculation_period_days: int = 30


# Request/Response models for API endpoints

class UpdateLanguagePreferenceRequest(BaseModel):
    """Request to update language preferences"""
    interface_language: Optional[Language] = None
    feedback_language: Optional[Language] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    auto_translate_feedback: Optional[bool] = None


class UpdateAccessibilityRequest(BaseModel):
    """Request to update accessibility settings"""
    text_size: Optional[TextSize] = None
    contrast_mode: Optional[ContrastMode] = None
    enable_screen_reader: Optional[bool] = None
    extended_timeouts: Optional[bool] = None
    timeout_extension_seconds: Optional[int] = None
    allow_extended_test_time: Optional[bool] = None
    test_time_multiplier: Optional[float] = None


class DownloadOfflineContentRequest(BaseModel):
    """Request to download offline content"""
    content_id: str
    priority: str = "normal"  # "low", "normal", "high"


class TranslateTextRequest(BaseModel):
    """Request to translate text"""
    text: str
    from_language: Language = Language.ENGLISH
    to_language: Language
    context: Optional[str] = None


class LocalizationResponse(BaseModel):
    """Response with localized content"""
    translations: Dict[str, str]  # Key -> translated text
    language: Language
    fallback_used: bool = False
    missing_keys: List[str] = []


class AccessibilityInfoResponse(BaseModel):
    """Response with accessibility information"""
    settings: AccessibilitySettings
    available_features: List[str]
    recommended_settings: Dict[str, Any]


class OfflineContentResponse(BaseModel):
    """Response with offline content information"""
    available_content: List[OfflineContent]
    downloaded_content: List[UserOfflineContent]
    storage_used_mb: float
    storage_available_mb: float
    sync_pending: bool


class TranslationResponse(BaseModel):
    """Response for text translation"""
    original_text: str
    translated_text: str
    from_language: Language
    to_language: Language
    confidence: float = 1.0
    alternatives: List[str] = []