"""
User model for QanotAI
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"
    TEACHER = "teacher"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    full_name = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    
    # Profile
    target_band_score = Column(Integer, nullable=True)
    target_test_date = Column(DateTime(timezone=True), nullable=True)
    locale = Column(String, default="en")
    timezone = Column(String, default="UTC")
    profile_photo_url = Column(String, nullable=True)
    
    # Subscription
    role = Column(Enum(UserRole), default=UserRole.FREE)
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    free_tests_remaining = Column(Integer, default=3)
    total_tests_taken = Column(Integer, default=0)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())