"""
Pydantic schemas for User model
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from app.models.user import UserRole


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    target_band_score: Optional[int] = Field(None, ge=1, le=9)
    locale: str = "en"
    timezone: str = "UTC"
    
    @validator("phone_number")
    def validate_phone(cls, v):
        if v and not v.startswith("+"):
            raise ValueError("Phone number must include country code (e.g., +998901234567)")
        return v


class UserCreate(UserBase):
    firebase_uid: str


class UserUpdate(UserBase):
    target_band_score: Optional[int] = Field(None, ge=1, le=9)
    target_test_date: Optional[datetime] = None
    profile_photo_url: Optional[str] = None


class UserInDB(UserBase):
    id: UUID
    firebase_uid: str
    role: UserRole
    subscription_expires_at: Optional[datetime]
    free_tests_remaining: int
    total_tests_taken: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    free_tests_remaining: int
    total_tests_taken: int
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    subscription_expires_at: Optional[datetime]
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class FirebaseAuthRequest(BaseModel):
    firebase_token: str


class PhoneAuthRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number with country code")
    verification_code: str = Field(..., min_length=6, max_length=6)