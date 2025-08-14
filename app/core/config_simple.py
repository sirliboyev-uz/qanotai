"""
Simplified configuration for deployment - Pydantic v1 compatible
"""
import os
from typing import List, Optional

class Settings:
    # Application
    APP_NAME: str = "QanotAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./qanotai.db")
    
    # Supabase
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Payme
    PAYME_MERCHANT_ID: Optional[str] = os.getenv("PAYME_MERCHANT_ID")
    PAYME_SECRET_KEY: Optional[str] = os.getenv("PAYME_SECRET_KEY")
    PAYME_TEST_MODE: bool = os.getenv("PAYME_TEST_MODE", "true").lower() == "true"
    
    # Storage
    SPACES_ENDPOINT: str = os.getenv("SPACES_ENDPOINT", "https://nyc3.digitaloceanspaces.com")
    SPACES_KEY: str = os.getenv("SPACES_KEY", "dev-key")
    SPACES_SECRET: str = os.getenv("SPACES_SECRET", "dev-secret")
    SPACES_BUCKET: str = os.getenv("SPACES_BUCKET", "qanotai-dev")
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_FREE_TESTS_PER_MONTH: int = 3
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

settings = Settings()