"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user_firebase
from app.models.user import User
from app.schemas.user import UserUpdate, UserProfile, UserResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile
    """
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
    
    return UserProfile.from_orm(user)


@router.patch("/profile", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile
    """
    # Get user
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
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return UserProfile.from_orm(user)


@router.get("/stats")
async def get_user_stats(
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's test statistics and progress
    """
    # Get user
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
    
    # TODO: Get actual stats from attempts and scores
    return {
        "total_tests": user.total_tests_taken,
        "free_tests_remaining": user.free_tests_remaining,
        "subscription_status": "premium" if user.role == "premium" else "free",
        "subscription_expires_at": user.subscription_expires_at,
        "average_score": None,  # TODO: Calculate from scores
        "last_test_date": None,  # TODO: Get from attempts
        "improvement_rate": None,  # TODO: Calculate trend
        "practice_streak": 0,  # TODO: Calculate from attempts
    }


@router.delete("/account")
async def delete_user_account(
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account (GDPR compliance)
    """
    # Get user
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
    
    # Soft delete (mark as inactive)
    user.is_active = False
    await db.commit()
    
    # TODO: Also delete from Firebase
    # TODO: Schedule hard delete after retention period
    
    return {"message": "Account deactivated successfully"}