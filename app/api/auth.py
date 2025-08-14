"""
Authentication endpoints for Epic 1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from app.core.auth import (
    create_access_token,
    verify_firebase_token,
    hash_password,
    verify_password,
    get_current_user,
    require_auth
)
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# In-memory user storage for demo (replace with database)
users_db = {}


class PhoneAuthRequest(BaseModel):
    """US-1.1: Phone Number Registration"""
    phone_number: str = Field(..., description="Phone with country code +998...")
    verification_code: Optional[str] = Field(None, description="OTP code")


class SocialAuthRequest(BaseModel):
    """US-1.2: Social Login"""
    provider: str = Field(..., description="google or apple")
    id_token: str = Field(..., description="OAuth ID token")


class UserProfile(BaseModel):
    """US-1.3: Profile Management"""
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    target_band_score: Optional[int] = Field(None, ge=1, le=9)
    target_test_date: Optional[datetime] = None
    locale: str = "en"
    timezone: str = "UTC"
    profile_photo_url: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


@router.post("/phone/send-otp")
async def send_phone_otp(request: PhoneAuthRequest):
    """
    US-1.1: Send OTP to phone number
    Acceptance Criteria:
    - User can enter phone number in international format
    - OTP verification is sent via SMS
    """
    if not request.phone_number.startswith("+"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must include country code (e.g., +998901234567)"
        )
    
    # For demo, generate fake OTP (in production, use SMS service)
    otp_code = "123456"
    
    return {
        "message": "OTP sent successfully",
        "phone_number": request.phone_number,
        "otp_hint": otp_code if settings.DEBUG else None  # Only show in debug mode
    }


@router.post("/phone/verify", response_model=AuthResponse)
async def verify_phone_otp(request: PhoneAuthRequest):
    """
    US-1.1: Verify OTP and create account
    Acceptance Criteria:
    - Account is created after successful verification
    - User profile is initialized with default settings
    """
    if not request.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is required"
        )
    
    # For demo, accept "123456" as valid OTP
    if request.verification_code != "123456":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Create or get user
    user_id = str(uuid.uuid4())
    if request.phone_number not in users_db:
        users_db[request.phone_number] = {
            "id": user_id,
            "phone_number": request.phone_number,
            "created_at": datetime.utcnow().isoformat(),
            "is_verified": True,
            "role": "free",
            "free_tests_remaining": 3
        }
    else:
        user_id = users_db[request.phone_number]["id"]
    
    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": user_id,
            "phone_number": request.phone_number,
            "type": "access"
        }
    )
    
    return AuthResponse(
        access_token=access_token,
        user=users_db[request.phone_number]
    )


@router.post("/social", response_model=AuthResponse)
async def social_login(request: SocialAuthRequest):
    """
    US-1.2: Social Login with Google/Apple
    Acceptance Criteria:
    - Google OAuth integration works on both iOS/Android
    - Apple Sign In works on iOS devices
    - User profile automatically populated from social account
    - Email is retrieved from social provider
    """
    if request.provider not in ["google", "apple"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider must be 'google' or 'apple'"
        )
    
    # Verify with Firebase if enabled
    user_data = {}
    if settings.FIREBASE_ENABLED:
        try:
            firebase_user = await verify_firebase_token(request.id_token)
            user_data = {
                "id": firebase_user.get("uid"),
                "email": firebase_user.get("email"),
                "name": firebase_user.get("name"),
                "provider": request.provider,
                "firebase_user": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid {request.provider} token"
            )
    else:
        # Demo mode - accept any token
        user_data = {
            "id": str(uuid.uuid4()),
            "email": f"demo@{request.provider}.com",
            "name": "Demo User",
            "provider": request.provider
        }
    
    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": user_data["id"],
            "email": user_data.get("email"),
            "provider": request.provider,
            "type": "access"
        }
    )
    
    return AuthResponse(
        access_token=access_token,
        user=user_data
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    US-1.3: Get user profile
    Acceptance Criteria:
    - Returns current user profile information
    """
    # Get user from database (demo uses in-memory)
    user_id = current_user.get("user_id")
    
    # Return profile
    return UserProfile(
        full_name=current_user.get("name", "Demo User"),
        email=current_user.get("email"),
        phone_number=current_user.get("phone_number"),
        locale="en",
        timezone="UTC"
    )


@router.patch("/profile", response_model=UserProfile)
async def update_profile(
    profile: UserProfile,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """
    US-1.3: Update user profile
    Acceptance Criteria:
    - Can edit name, target band score, test date
    - Can set language preference (English/Uzbek)
    - Can upload profile photo
    - Changes are saved immediately
    """
    user_id = current_user.get("user_id")
    
    # Update profile in database (demo returns updated data)
    updated_profile = profile.dict(exclude_unset=True)
    updated_profile["updated_at"] = datetime.utcnow().isoformat()
    
    return profile


@router.post("/refresh")
async def refresh_token(current_user: Dict[str, Any] = Depends(require_auth)):
    """Refresh access token"""
    new_token = create_access_token(
        data={
            "sub": current_user.get("user_id"),
            "email": current_user.get("email"),
            "phone_number": current_user.get("phone_number"),
            "type": "access"
        }
    )
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }