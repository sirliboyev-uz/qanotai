"""
Test attempt endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user_firebase
from app.models.attempt import Attempt, AttemptStatus
from app.models.user import User
from app.schemas.attempt import (
    AttemptCreate,
    AttemptResponse,
    AttemptComplete,
    AttemptWithScore
)
from app.services.storage import StorageService
from app.workers.tasks import process_attempt_scoring
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
storage_service = StorageService()


@router.post("/", response_model=AttemptResponse)
async def create_attempt(
    attempt_data: AttemptCreate,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new test attempt and return presigned upload URLs
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
    
    # Check user quota
    if user.role == "free" and user.free_tests_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No free tests remaining. Please upgrade to continue."
        )
    
    # Create attempt
    attempt = Attempt(
        user_id=user.id,
        test_mode=attempt_data.test_mode,
        target_band=attempt_data.target_band,
        part1_questions=attempt_data.part1_question_ids,
        part2_question_id=attempt_data.part2_question_id,
        part3_questions=attempt_data.part3_question_ids,
        started_at=datetime.utcnow(),
        status=AttemptStatus.IN_PROGRESS,
        client_info=attempt_data.client_info
    )
    
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    
    # Generate presigned upload URLs
    upload_urls = {}
    
    if attempt_data.test_mode in ["full", "part1"]:
        upload_urls["part1"] = []
        for i in range(len(attempt_data.part1_question_ids or [])):
            url = await storage_service.generate_upload_url(
                f"attempts/{attempt.id}/part1_{i}.webm"
            )
            upload_urls["part1"].append(url)
    
    if attempt_data.test_mode in ["full", "part2"]:
        upload_urls["part2"] = await storage_service.generate_upload_url(
            f"attempts/{attempt.id}/part2.webm"
        )
    
    if attempt_data.test_mode in ["full", "part3"]:
        upload_urls["part3"] = []
        for i in range(len(attempt_data.part3_question_ids or [])):
            url = await storage_service.generate_upload_url(
                f"attempts/{attempt.id}/part3_{i}.webm"
            )
            upload_urls["part3"].append(url)
    
    logger.info(f"Created attempt {attempt.id} for user {user.id}")
    
    return AttemptResponse(
        id=attempt.id,
        status=attempt.status,
        test_mode=attempt.test_mode,
        started_at=attempt.started_at,
        upload_urls=upload_urls
    )


@router.put("/{attempt_id}/complete", response_model=Dict[str, str])
async def complete_attempt(
    attempt_id: UUID,
    complete_data: AttemptComplete,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark attempt as complete and trigger scoring
    """
    # Get attempt
    result = await db.execute(
        select(Attempt).where(
            and_(
                Attempt.id == attempt_id,
                Attempt.user_id == current_user["uid"] if not current_user.get("firebase_user") else None
            )
        )
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempt is not in progress"
        )
    
    # Update attempt
    attempt.completed_at = datetime.utcnow()
    attempt.status = AttemptStatus.PROCESSING
    attempt.total_duration_seconds = (
        attempt.completed_at - attempt.started_at
    ).total_seconds()
    
    # Store audio keys
    attempt.part1_audio_keys = complete_data.part1_audio_keys
    attempt.part2_audio_key = complete_data.part2_audio_key
    attempt.part3_audio_keys = complete_data.part3_audio_keys
    
    await db.commit()
    
    # Update user quota
    user = await db.get(User, attempt.user_id)
    if user.role == "free":
        user.free_tests_remaining -= 1
    user.total_tests_taken += 1
    await db.commit()
    
    # Trigger async scoring
    task = process_attempt_scoring.delay(str(attempt.id))
    
    # Update attempt with task ID
    attempt.celery_task_id = task.id
    await db.commit()
    
    logger.info(f"Completed attempt {attempt.id}, scoring task: {task.id}")
    
    return {
        "message": "Attempt completed successfully",
        "task_id": task.id,
        "status": "processing"
    }


@router.get("/{attempt_id}", response_model=AttemptWithScore)
async def get_attempt(
    attempt_id: UUID,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get attempt details with score if available
    """
    # Get attempt with score
    result = await db.execute(
        select(Attempt).where(
            and_(
                Attempt.id == attempt_id,
                Attempt.user_id == current_user["uid"] if not current_user.get("firebase_user") else None
            )
        )
    )
    attempt = result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    return AttemptWithScore.from_orm(attempt)


@router.get("/", response_model=List[AttemptResponse])
async def list_attempts(
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's test attempts
    """
    # Get user
    if current_user.get("firebase_user"):
        user_result = await db.execute(
            select(User).where(User.firebase_uid == current_user["uid"])
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user.id
    else:
        user_id = current_user["uid"]
    
    # Get attempts
    result = await db.execute(
        select(Attempt)
        .where(Attempt.user_id == user_id)
        .order_by(Attempt.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    attempts = result.scalars().all()
    
    return [AttemptResponse.from_orm(a) for a in attempts]