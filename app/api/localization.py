"""
Epic 8: Accessibility & Localization API Endpoints
US-8.1: Bilingual Interface
US-8.2: Offline Mode
US-8.3: Accessibility Features
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json
import random
from ..models.localization_models import (
    Language,
    AccessibilityLevel,
    TextSize,
    ContrastMode,
    OfflineContentType,
    TranslationEntry,
    UserLanguagePreference,
    AccessibilitySettings,
    OfflineContent,
    UserOfflineContent,
    LocalizationStats,
    UpdateLanguagePreferenceRequest,
    UpdateAccessibilityRequest,
    DownloadOfflineContentRequest,
    TranslateTextRequest,
    LocalizationResponse,
    AccessibilityInfoResponse,
    OfflineContentResponse,
    TranslationResponse
)
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/localization", tags=["Accessibility & Localization"])

# Mock data stores (replace with actual database in production)
translations_db: List[TranslationEntry] = []
user_language_preferences_db: Dict[str, UserLanguagePreference] = {}
accessibility_settings_db: Dict[str, AccessibilitySettings] = {}
offline_content_db: List[OfflineContent] = []
user_offline_content_db: List[UserOfflineContent] = []

@router.get("/languages")
async def get_supported_languages():
    """
    US-8.1: Bilingual Interface
    Get list of supported languages
    """
    return {
        "supported_languages": [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "flag": "🇺🇸",
                "is_primary": True
            },
            {
                "code": "uz",
                "name": "Uzbek",
                "native_name": "O'zbekcha",
                "flag": "🇺🇿",
                "is_primary": True
            },
            {
                "code": "ru",
                "name": "Russian",
                "native_name": "Русский",
                "flag": "🇷🇺",
                "is_primary": False
            },
            {
                "code": "kz",
                "name": "Kazakh",
                "native_name": "Қазақша",
                "flag": "🇰🇿",
                "is_primary": False
            },
            {
                "code": "tr",
                "name": "Turkish",
                "native_name": "Türkçe",
                "flag": "🇹🇷",
                "is_primary": False
            }
        ],
        "default_language": "en",
        "auto_detect_available": True
    }

@router.get("/preferences", response_model=UserLanguagePreference)
async def get_language_preferences(current_user: Dict = Depends(get_current_user)):
    """
    US-8.1: Bilingual Interface
    Get user's language preferences
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create preferences
    if user_id not in user_language_preferences_db:
        user_language_preferences_db[user_id] = UserLanguagePreference(user_id=user_id)
    
    return user_language_preferences_db[user_id]

@router.put("/preferences")
async def update_language_preferences(
    request: UpdateLanguagePreferenceRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.1: Bilingual Interface
    Update user's language preferences
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create preferences
    if user_id not in user_language_preferences_db:
        user_language_preferences_db[user_id] = UserLanguagePreference(user_id=user_id)
    
    preferences = user_language_preferences_db[user_id]
    
    # Update fields if provided
    if request.interface_language is not None:
        preferences.interface_language = request.interface_language
    
    if request.feedback_language is not None:
        preferences.feedback_language = request.feedback_language
    
    if request.region is not None:
        preferences.region = request.region
    
    if request.timezone is not None:
        preferences.timezone = request.timezone
    
    if request.auto_translate_feedback is not None:
        preferences.auto_translate_feedback = request.auto_translate_feedback
    
    preferences.updated_at = datetime.utcnow()
    
    return {
        "message": "Language preferences updated successfully",
        "preferences": preferences
    }

@router.get("/translations", response_model=LocalizationResponse)
async def get_translations(
    language: Language = Query(Language.ENGLISH),
    namespace: Optional[str] = Query("app"),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.1: Bilingual Interface
    Get translations for specified language and namespace
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get user's preferred language if not specified
    if user_id in user_language_preferences_db:
        user_preferences = user_language_preferences_db[user_id]
        if language == Language.ENGLISH:  # Use user's preference
            language = user_preferences.interface_language
    
    # Mock translations data
    mock_translations = _get_mock_translations(language, namespace)
    
    return LocalizationResponse(
        translations=mock_translations,
        language=language,
        fallback_used=language != Language.ENGLISH and len(mock_translations) < 50,
        missing_keys=[]
    )

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslateTextRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.1: Bilingual Interface
    Translate text between supported languages
    """
    # Mock translation service (in production, use actual translation API)
    translated_text = _mock_translate(request.text, request.from_language, request.to_language)
    
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated_text,
        from_language=request.from_language,
        to_language=request.to_language,
        confidence=0.95,
        alternatives=[]
    )

@router.get("/accessibility", response_model=AccessibilityInfoResponse)
async def get_accessibility_settings(current_user: Dict = Depends(get_current_user)):
    """
    US-8.3: Accessibility Features
    Get user's accessibility settings and available features
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create settings
    if user_id not in accessibility_settings_db:
        accessibility_settings_db[user_id] = AccessibilitySettings(user_id=user_id)
    
    settings = accessibility_settings_db[user_id]
    
    available_features = [
        "text_size_adjustment",
        "high_contrast_mode",
        "screen_reader_support",
        "extended_timeouts",
        "audio_descriptions",
        "extended_test_time",
        "simplified_interface",
        "focus_indicators",
        "reduced_animations"
    ]
    
    # Generate recommended settings based on current settings
    recommended_settings = _generate_accessibility_recommendations(settings)
    
    return AccessibilityInfoResponse(
        settings=settings,
        available_features=available_features,
        recommended_settings=recommended_settings
    )

@router.put("/accessibility")
async def update_accessibility_settings(
    request: UpdateAccessibilityRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.3: Accessibility Features
    Update user's accessibility preferences
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create settings
    if user_id not in accessibility_settings_db:
        accessibility_settings_db[user_id] = AccessibilitySettings(user_id=user_id)
    
    settings = accessibility_settings_db[user_id]
    
    # Update fields if provided
    if request.text_size is not None:
        settings.text_size = request.text_size
    
    if request.contrast_mode is not None:
        settings.contrast_mode = request.contrast_mode
        settings.use_high_contrast = (request.contrast_mode == ContrastMode.HIGH)
    
    if request.enable_screen_reader is not None:
        settings.enable_screen_reader = request.enable_screen_reader
    
    if request.extended_timeouts is not None:
        settings.extended_timeouts = request.extended_timeouts
    
    if request.timeout_extension_seconds is not None:
        settings.timeout_extension_seconds = request.timeout_extension_seconds
    
    if request.allow_extended_test_time is not None:
        settings.allow_extended_test_time = request.allow_extended_test_time
    
    if request.test_time_multiplier is not None:
        settings.test_time_multiplier = max(1.0, min(2.0, request.test_time_multiplier))
    
    settings.updated_at = datetime.utcnow()
    
    return {
        "message": "Accessibility settings updated successfully",
        "settings": settings
    }

@router.get("/offline-content", response_model=OfflineContentResponse)
async def get_offline_content(
    content_type: Optional[OfflineContentType] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.2: Offline Mode
    Get available offline content and user's downloaded content
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Filter available content
    available_content = offline_content_db.copy()
    if content_type:
        available_content = [c for c in available_content if c.content_type == content_type]
    
    # Get user's downloaded content
    user_downloads = [uc for uc in user_offline_content_db if uc.user_id == user_id]
    
    # Calculate storage usage
    storage_used = sum(uc.local_size_mb or 0 for uc in user_downloads)
    storage_available = 1024 - storage_used  # Mock 1GB limit
    
    # Check if sync is pending
    sync_pending = any(uc.needs_update for uc in user_downloads)
    
    return OfflineContentResponse(
        available_content=available_content,
        downloaded_content=user_downloads,
        storage_used_mb=storage_used,
        storage_available_mb=max(0, storage_available),
        sync_pending=sync_pending
    )

@router.post("/offline-content/download")
async def download_offline_content(
    request: DownloadOfflineContentRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.2: Offline Mode
    Start downloading offline content
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find the content
    content = None
    for c in offline_content_db:
        if c.id == request.content_id:
            content = c
            break
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already downloaded or downloading
    existing_download = None
    for uc in user_offline_content_db:
        if uc.user_id == user_id and uc.content_id == request.content_id:
            existing_download = uc
            break
    
    if existing_download and existing_download.download_status == "completed":
        return {
            "message": "Content already downloaded",
            "download_id": existing_download.id,
            "status": "completed"
        }
    
    # Create or update download record
    if not existing_download:
        user_content = UserOfflineContent(
            user_id=user_id,
            content_id=request.content_id,
            download_status="downloading"
        )
        user_offline_content_db.append(user_content)
    else:
        existing_download.download_status = "downloading"
        existing_download.download_progress = 0.0
        user_content = existing_download
    
    # Start background download simulation
    background_tasks.add_task(_simulate_download, user_content, content)
    
    return {
        "message": "Download started",
        "download_id": user_content.id,
        "estimated_time_minutes": content.size_mb / 10,  # Mock: 10MB/min
        "status": "downloading"
    }

@router.delete("/offline-content/{content_id}")
async def delete_offline_content(
    content_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.2: Offline Mode
    Delete downloaded offline content
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find and remove the user's download
    removed_content = None
    for i, uc in enumerate(user_offline_content_db):
        if uc.user_id == user_id and uc.content_id == content_id:
            removed_content = user_offline_content_db.pop(i)
            break
    
    if not removed_content:
        raise HTTPException(status_code=404, detail="Downloaded content not found")
    
    # Mock cleanup of local files
    storage_freed = removed_content.local_size_mb or 0
    
    return {
        "message": "Offline content deleted successfully",
        "storage_freed_mb": storage_freed
    }

@router.post("/offline-content/sync")
async def sync_offline_content(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-8.2: Offline Mode
    Sync all offline content with latest versions
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find content that needs updates
    user_downloads = [uc for uc in user_offline_content_db if uc.user_id == user_id]
    updates_needed = [uc for uc in user_downloads if uc.needs_update]
    
    if not updates_needed:
        return {
            "message": "All content is up to date",
            "updates_count": 0
        }
    
    # Start background sync
    background_tasks.add_task(_simulate_sync, updates_needed)
    
    return {
        "message": "Content sync started",
        "updates_count": len(updates_needed),
        "estimated_time_minutes": len(updates_needed) * 2
    }

@router.get("/stats")
async def get_localization_stats(current_user: Dict = Depends(get_current_user)):
    """
    Get localization and accessibility usage statistics
    """
    # Mock statistics
    stats = LocalizationStats(
        language_usage={
            "en": 1250,
            "uz": 800,
            "ru": 200,
            "kz": 150,
            "tr": 100
        },
        region_distribution={
            "UZ": 900,
            "KZ": 180,
            "TR": 120,
            "RU": 150,
            "OTHER": 150
        },
        screen_reader_users=45,
        high_contrast_users=120,
        large_text_users=200,
        extended_timeout_users=80,
        translation_completeness={
            "uz": 85.5,
            "ru": 75.2,
            "kz": 60.8,
            "tr": 55.3
        },
        offline_downloads_total=1580,
        most_popular_offline_content=[
            "IELTS Speaking Part 1 Questions",
            "Common Vocabulary Pack",
            "Pronunciation Practice Audio"
        ]
    )
    
    return stats

# Helper functions

def _get_mock_translations(language: Language, namespace: str) -> Dict[str, str]:
    """Generate mock translations for given language and namespace"""
    base_translations = {
        "app.welcome": "Welcome to QanotAI",
        "app.start_test": "Start Test",
        "app.view_results": "View Results",
        "app.settings": "Settings",
        "test.part1_instructions": "Part 1: Answer questions about familiar topics",
        "test.part2_instructions": "Part 2: Give a 2-minute talk on the given topic",
        "test.part3_instructions": "Part 3: Discuss abstract ideas related to the topic",
        "feedback.overall_score": "Overall Band Score",
        "feedback.fluency": "Fluency and Coherence",
        "feedback.vocabulary": "Lexical Resource",
        "feedback.grammar": "Grammatical Range and Accuracy",
        "feedback.pronunciation": "Pronunciation"
    }
    
    if language == Language.UZBEK:
        uzbek_translations = {
            "app.welcome": "QanotAI ga xush kelibsiz",
            "app.start_test": "Testni boshlash",
            "app.view_results": "Natijalarni ko'rish",
            "app.settings": "Sozlamalar",
            "test.part1_instructions": "1-qism: Tanish mavzular haqida savollar",
            "test.part2_instructions": "2-qism: Berilgan mavzu bo'yicha 2 daqiqalik nutq",
            "test.part3_instructions": "3-qism: Mavzu bilan bog'liq mavhum g'oyalarni muhokama qilish",
            "feedback.overall_score": "Umumiy Ball",
            "feedback.fluency": "Ravonlik va Izchillik",
            "feedback.vocabulary": "Lug'at boyligi",
            "feedback.grammar": "Grammatik to'g'rilik",
            "feedback.pronunciation": "Talaffuz"
        }
        return uzbek_translations
    
    elif language == Language.RUSSIAN:
        russian_translations = {
            "app.welcome": "Добро пожаловать в QanotAI",
            "app.start_test": "Начать тест",
            "app.view_results": "Просмотр результатов",
            "app.settings": "Настройки",
            "test.part1_instructions": "Часть 1: Ответы на вопросы о знакомых темах",
            "test.part2_instructions": "Часть 2: 2-минутный рассказ на заданную тему",
            "test.part3_instructions": "Часть 3: Обсуждение абстрактных идей по теме",
            "feedback.overall_score": "Общий балл",
            "feedback.fluency": "Беглость и связность",
            "feedback.vocabulary": "Словарный запас",
            "feedback.grammar": "Грамматическая точность",
            "feedback.pronunciation": "Произношение"
        }
        return russian_translations
    
    return base_translations

def _mock_translate(text: str, from_lang: Language, to_lang: Language) -> str:
    """Mock translation function"""
    if from_lang == to_lang:
        return text
    
    # Simple mock translations for common phrases
    mock_translations = {
        ("Hello", Language.ENGLISH, Language.UZBEK): "Salom",
        ("Hello", Language.ENGLISH, Language.RUSSIAN): "Привет",
        ("Good luck", Language.ENGLISH, Language.UZBEK): "Omad tilayman",
        ("Good luck", Language.ENGLISH, Language.RUSSIAN): "Удачи",
        ("Start Test", Language.ENGLISH, Language.UZBEK): "Testni boshlash",
        ("Start Test", Language.ENGLISH, Language.RUSSIAN): "Начать тест"
    }
    
    key = (text, from_lang, to_lang)
    if key in mock_translations:
        return mock_translations[key]
    
    # Default fallback
    return f"[{to_lang.value}] {text}"

def _generate_accessibility_recommendations(settings: AccessibilitySettings) -> Dict[str, Any]:
    """Generate accessibility recommendations based on current settings"""
    recommendations = {}
    
    if settings.text_size == TextSize.SMALL:
        recommendations["text_size"] = "Consider using larger text for better readability"
    
    if not settings.enable_screen_reader and settings.use_high_contrast:
        recommendations["screen_reader"] = "Screen reader support may be helpful with high contrast mode"
    
    if settings.extended_timeouts and not settings.allow_extended_test_time:
        recommendations["test_time"] = "Consider enabling extended test time as well"
    
    return recommendations

async def _simulate_download(user_content: UserOfflineContent, content: OfflineContent):
    """Simulate content download progress"""
    import asyncio
    
    total_steps = 10
    for step in range(total_steps + 1):
        await asyncio.sleep(1)  # Simulate download time
        progress = step / total_steps
        user_content.download_progress = progress
        
        if step == total_steps:
            user_content.download_status = "completed"
            user_content.downloaded_at = datetime.utcnow()
            user_content.local_size_mb = content.size_mb
            user_content.local_path = f"/offline/{content.id}"

async def _simulate_sync(updates_needed: List[UserOfflineContent]):
    """Simulate content sync process"""
    import asyncio
    
    for user_content in updates_needed:
        await asyncio.sleep(2)  # Simulate sync time
        user_content.needs_update = False
        user_content.local_version = "latest"

# Initialize sample offline content
def _initialize_sample_offline_content():
    """Initialize sample offline content"""
    global offline_content_db
    
    if not offline_content_db:
        sample_content = [
            {
                "name": "IELTS Speaking Part 1 Questions",
                "description": "Comprehensive collection of Part 1 questions organized by topic",
                "content_type": OfflineContentType.QUESTION_PACK,
                "size_mb": 25.5,
                "question_count": 500,
                "estimated_practice_time_minutes": 300
            },
            {
                "name": "Common Vocabulary Pack",
                "description": "Essential IELTS vocabulary with pronunciation guides",
                "content_type": OfflineContentType.VOCABULARY,
                "size_mb": 45.2,
                "estimated_practice_time_minutes": 180
            },
            {
                "name": "Pronunciation Practice Audio",
                "description": "Audio samples for pronunciation practice",
                "content_type": OfflineContentType.AUDIO_SAMPLES,
                "size_mb": 120.8,
                "audio_duration_minutes": 90
            },
            {
                "name": "Grammar Rules Reference",
                "description": "Complete grammar reference for IELTS speaking",
                "content_type": OfflineContentType.GRAMMAR_RULES,
                "size_mb": 15.3,
                "estimated_practice_time_minutes": 120
            },
            {
                "name": "Mock Test Pack 1",
                "description": "5 complete IELTS speaking mock tests",
                "content_type": OfflineContentType.PRACTICE_TESTS,
                "size_mb": 85.7,
                "question_count": 75,
                "estimated_practice_time_minutes": 450
            }
        ]
        
        for content_data in sample_content:
            content = OfflineContent(
                **content_data,
                download_url=f"https://qanotai.com/downloads/{uuid.uuid4()}",
                checksum=f"sha256:{uuid.uuid4()}",
                is_free=random.choice([True, False]),
                requires_subscription=not content_data.get("is_free", True)
            )
            offline_content_db.append(content)

# Initialize sample data
_initialize_sample_offline_content()