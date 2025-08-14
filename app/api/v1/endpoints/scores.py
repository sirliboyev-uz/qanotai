"""
Score endpoints for viewing test results
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user_firebase
from app.models.score import Score
from app.models.attempt import Attempt
from app.models.user import User
from app.schemas.score import ScoreResponse, ScoreSummary
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/attempt/{attempt_id}", response_model=ScoreResponse)
async def get_attempt_score(
    attempt_id: UUID,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get score for a specific attempt
    """
    # Verify user owns the attempt
    attempt_result = await db.execute(
        select(Attempt).where(
            and_(
                Attempt.id == attempt_id,
                Attempt.user_id == current_user["uid"] if not current_user.get("firebase_user") else None
            )
        )
    )
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    # Get score
    score_result = await db.execute(
        select(Score).where(Score.attempt_id == attempt_id)
    )
    score = score_result.scalar_one_or_none()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not yet available. Please check back later."
        )
    
    return ScoreResponse.from_orm(score)


@router.get("/history", response_model=List[ScoreSummary])
async def get_score_history(
    limit: int = 10,
    days: Optional[int] = None,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's score history with improvement tracking
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
    
    # Build query
    query = select(Score, Attempt).join(
        Attempt, Score.attempt_id == Attempt.id
    ).where(Attempt.user_id == user_id)
    
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(Score.created_at >= cutoff_date)
    
    query = query.order_by(Score.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    scores_with_attempts = result.all()
    
    # Calculate improvements
    summaries = []
    previous_score = None
    
    for score, attempt in reversed(scores_with_attempts):
        improvement = None
        if previous_score:
            improvement = score.overall_band - previous_score
        
        summaries.append(ScoreSummary(
            attempt_id=attempt.id,
            date=score.created_at,
            overall_band=score.overall_band,
            test_mode=attempt.test_mode,
            improvement=improvement
        ))
        
        previous_score = score.overall_band
    
    return list(reversed(summaries))


@router.get("/average")
async def get_average_scores(
    days: int = 30,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's average scores by criteria over a time period
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
    
    # Calculate averages
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        func.avg(Score.overall_band).label("avg_overall"),
        func.avg(Score.fluency_coherence).label("avg_fluency"),
        func.avg(Score.lexical_resource).label("avg_lexical"),
        func.avg(Score.grammatical_range_accuracy).label("avg_grammar"),
        func.avg(Score.pronunciation).label("avg_pronunciation"),
        func.count(Score.id).label("total_tests")
    ).join(
        Attempt, Score.attempt_id == Attempt.id
    ).where(
        and_(
            Attempt.user_id == user_id,
            Score.created_at >= cutoff_date
        )
    )
    
    result = await db.execute(query)
    averages = result.one()
    
    return {
        "period_days": days,
        "total_tests": averages.total_tests or 0,
        "average_overall_band": round(averages.avg_overall or 0, 1),
        "average_fluency": round(averages.avg_fluency or 0, 1),
        "average_lexical": round(averages.avg_lexical or 0, 1),
        "average_grammar": round(averages.avg_grammar or 0, 1),
        "average_pronunciation": round(averages.avg_pronunciation or 0, 1)
    }


@router.get("/progress")
async def get_progress_analysis(
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed progress analysis and recommendations
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
    
    # Get last 10 scores
    query = select(Score).join(
        Attempt, Score.attempt_id == Attempt.id
    ).where(
        Attempt.user_id == user_id
    ).order_by(Score.created_at.desc()).limit(10)
    
    result = await db.execute(query)
    recent_scores = result.scalars().all()
    
    if not recent_scores:
        return {
            "message": "No test data available yet",
            "recommendation": "Take your first practice test to get started!"
        }
    
    # Calculate trends
    latest = recent_scores[0]
    oldest = recent_scores[-1] if len(recent_scores) > 1 else latest
    
    improvement = latest.overall_band - oldest.overall_band
    
    # Identify weakest area
    criteria_scores = {
        "fluency": latest.fluency_coherence,
        "lexical": latest.lexical_resource,
        "grammar": latest.grammatical_range_accuracy,
        "pronunciation": latest.pronunciation
    }
    weakest_area = min(criteria_scores, key=criteria_scores.get)
    
    return {
        "current_band": latest.overall_band,
        "improvement": round(improvement, 1),
        "tests_taken": len(recent_scores),
        "weakest_area": weakest_area,
        "weakest_score": criteria_scores[weakest_area],
        "strengths": latest.strengths or [],
        "focus_areas": latest.improvements or [],
        "recommended_topics": latest.recommended_topics or [],
        "estimated_improvement_time": latest.estimated_improvement_time
    }