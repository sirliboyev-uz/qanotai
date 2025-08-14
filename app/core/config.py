"""
Core configuration for QanotAI backend using Pydantic Settings
"""
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "QanotAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = Field(..., min_length=32)
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Firebase
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_ENABLED: bool = False
    
    # Storage (DigitalOcean Spaces / S3)
    SPACES_ENDPOINT: str
    SPACES_KEY: str
    SPACES_SECRET: str
    SPACES_BUCKET: str
    SPACES_REGION: str = "nyc3"
    UPLOAD_URL_EXPIRY: int = 3600  # 1 hour
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "openai"  # openai or anthropic
    
    # Whisper STT
    WHISPER_MODEL: str = "whisper-1"
    STT_PROVIDER: str = "openai"  # openai or google
    STT_TIMEOUT: int = 30  # seconds
    
    # Scoring Configuration
    MAX_AUDIO_DURATION_MS: int = 120000  # 2 minutes
    MIN_AUDIO_DURATION_MS: int = 5000   # 5 seconds
    SCORING_TIMEOUT: int = 60  # seconds
    
    # Payment (Payme for Uzbekistan)
    PAYME_MERCHANT_ID: Optional[str] = None
    PAYME_SECRET_KEY: Optional[str] = None
    PAYME_TEST_MODE: bool = True
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # Analytics
    POSTHOG_API_KEY: Optional[str] = None
    POSTHOG_HOST: str = "https://app.posthog.com"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8100"]
    
    # Rate Limiting
    RATE_LIMIT_FREE_TESTS_PER_MONTH: int = 3
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")
    
    # IELTS Scoring Rubric
    BAND_DESCRIPTORS: dict = {
        "fluency": {
            9: "Speaks fluently with only rare repetition or self-correction",
            8: "Speaks fluently with only occasional repetition or self-correction",
            7: "Speaks at length without noticeable effort or loss of coherence",
            6: "Is willing to speak at length, though may lose coherence at times",
            5: "Usually maintains flow of speech but uses repetition and self-correction",
            4: "Cannot respond without noticeable pauses and may speak slowly",
            3: "Speaks with long pauses, limited ability to link simple sentences",
            2: "Pauses lengthily before most words, little communication possible",
            1: "No communication possible"
        },
        "lexical_resource": {
            9: "Uses vocabulary with full flexibility and precise meaning",
            8: "Uses a wide vocabulary resource readily and flexibly",
            7: "Uses vocabulary resource flexibly to discuss variety of topics",
            6: "Has a wide enough vocabulary to discuss topics at length",
            5: "Manages to talk about familiar and unfamiliar topics",
            4: "Is able to talk about familiar topics but vocabulary limited",
            3: "Uses simple vocabulary to convey personal information",
            2: "Only produces isolated words or memorized utterances",
            1: "No communication possible"
        },
        "grammatical_range": {
            9: "Uses a full range of structures naturally and appropriately",
            8: "Uses a wide range of structures flexibly",
            7: "Uses a range of complex structures with some flexibility",
            6: "Uses a mix of simple and complex structures",
            5: "Produces basic sentence forms with reasonable accuracy",
            4: "Produces basic sentence forms and some correct simple sentences",
            3: "Attempts basic sentence forms but with limited success",
            2: "Cannot produce basic sentence forms",
            1: "No communication possible"
        },
        "pronunciation": {
            9: "Uses a full range of pronunciation features with precision",
            8: "Is easy to understand throughout with flexible use of features",
            7: "Shows all positive features but with occasional lapses",
            6: "Uses a range of pronunciation features with mixed control",
            5: "Shows all positive features but control limited",
            4: "Uses limited range of pronunciation features",
            3: "Shows some positive features but control limited",
            2: "Speech often unintelligible",
            1: "No communication possible"
        }
    }
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @validator("CELERY_BROKER_URL", pre=True)
    def set_celery_broker(cls, v, values):
        if not v and "REDIS_URL" in values:
            return values["REDIS_URL"].replace("/0", "/1")
        return v
    
    @validator("CELERY_RESULT_BACKEND", pre=True)
    def set_celery_backend(cls, v, values):
        if not v and "REDIS_URL" in values:
            return values["REDIS_URL"].replace("/0", "/2")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()