"""
Enhanced authentication endpoints for mobile app integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
import uuid
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# In-memory user storage (replace with database in production)
users_db = {}

class PhoneVerifyRequest(BaseModel):
    phoneNumber: str
    isOTPValid: bool

class GoogleAuthRequest(BaseModel):
    idToken: str
    email: str
    displayName: Optional[str] = None
    photoURL: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    remainingTrials: int = 3
    isSubscribed: bool = False
    subscriptionExpiresAt: Optional[datetime] = None

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    isNewUser: bool

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_or_create_user(identifier: str, **kwargs) -> tuple[dict, bool]:
    """Get existing user or create new one"""
    # Check if user exists
    for user_id, user in users_db.items():
        if user.get("phoneNumber") == identifier or user.get("email") == identifier:
            # Update user info
            user["updatedAt"] = datetime.utcnow()
            for key, value in kwargs.items():
                if value is not None:
                    user[key] = value
            return user, False
    
    # Create new user
    user = {
        "id": str(uuid.uuid4()),
        "phoneNumber": kwargs.get("phoneNumber"),
        "email": kwargs.get("email"),
        "displayName": kwargs.get("displayName"),
        "photoURL": kwargs.get("photoURL"),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "remainingTrials": 3,
        "isSubscribed": False,
        "subscriptionExpiresAt": None,
    }
    users_db[user["id"]] = user
    return user, True

@router.post("/phone-verify", response_model=AuthResponse)
async def verify_phone_otp(request: PhoneVerifyRequest):
    """
    Verify phone number with OTP and create/login user
    """
    if not request.isOTPValid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Get or create user
    user, is_new = get_or_create_user(
        request.phoneNumber,
        phoneNumber=request.phoneNumber
    )
    
    # Create JWT token
    token = create_access_token({"sub": user["id"], "phone": request.phoneNumber})
    
    return AuthResponse(
        user=UserResponse(**user),
        token=token,
        isNewUser=is_new
    )

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google and create/login user
    """
    # In production, verify the idToken with Google
    # For now, we trust the token
    
    # Get or create user
    user, is_new = get_or_create_user(
        request.email,
        email=request.email,
        displayName=request.displayName,
        photoURL=request.photoURL
    )
    
    # Create JWT token
    token = create_access_token({"sub": user["id"], "email": request.email})
    
    return AuthResponse(
        user=UserResponse(**user),
        token=token,
        isNewUser=is_new
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: str = None):
    """
    Get current user from JWT token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/refresh")
async def refresh_token(authorization: str = None):
    """
    Refresh JWT token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new token
        new_token = create_access_token({"sub": user_id})
        
        return {"token": new_token}
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )