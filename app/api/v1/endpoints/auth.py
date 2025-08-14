"""
Authentication endpoints for QanotAI
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    verify_firebase_token,
    create_user_tokens,
    get_current_user_firebase
)
from app.models.user import User
from app.schemas.user import (
    FirebaseAuthRequest,
    TokenResponse,
    UserCreate,
    UserResponse
)
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/firebase", response_model=TokenResponse)
async def authenticate_firebase(
    request: FirebaseAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with Firebase token and create/update user in database
    """
    try:
        # Verify Firebase token
        firebase_user = await verify_firebase_token(request.firebase_token)
        
        # Check if user exists
        result = await db.execute(
            select(User).where(User.firebase_uid == firebase_user["uid"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                firebase_uid=firebase_user["uid"],
                email=firebase_user.get("email"),
                phone_number=firebase_user.get("phone_number"),
                full_name=firebase_user.get("name"),
                display_name=firebase_user.get("name", "").split()[0] if firebase_user.get("name") else None,
                is_verified=firebase_user.get("email_verified", False),
                last_login_at=datetime.utcnow()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New user created: {user.id}")
        else:
            # Update last login
            user.last_login_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
        
        # Create JWT tokens
        tokens = create_user_tokens(
            user_id=str(user.id),
            email=user.email,
            phone_number=user.phone_number
        )
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        logger.error(f"Firebase authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == current_user["uid"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new tokens
    tokens = create_user_tokens(
        user_id=str(user.id),
        email=user.email,
        phone_number=user.phone_number
    )
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user
    """
    # Get user from database
    if current_user.get("firebase_user"):
        result = await db.execute(
            select(User).where(User.firebase_uid == current_user["uid"])
        )
    else:
        result = await db.execute(
            select(User).where(User.id == current_user["uid"])
        )
    
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)