"""
Question bank endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user_firebase
from app.models.question import Question
from app.schemas.question import QuestionResponse, QuestionSet
import random
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/next", response_model=QuestionSet)
async def get_next_question_set(
    test_mode: str = Query("full", description="Test mode: full, part1, part2, part3, quick"),
    difficulty: Optional[int] = Query(None, ge=1, le=9),
    topic: Optional[str] = None,
    current_user: dict = Depends(get_current_user_firebase),
    db: AsyncSession = Depends(get_db)
):
    """
    Get next set of questions for a test attempt
    Returns questions for all 3 parts based on test mode
    """
    questions = {}
    
    # Build base query
    base_conditions = [Question.is_active == True]
    if difficulty:
        base_conditions.append(Question.difficulty_level == difficulty)
    if topic:
        base_conditions.append(Question.topic == topic)
    
    try:
        if test_mode in ["full", "part1"]:
            # Get 4-5 Part 1 questions
            part1_query = select(Question).where(
                and_(Question.part == 1, *base_conditions)
            ).order_by(func.random()).limit(5)
            result = await db.execute(part1_query)
            questions["part1"] = [QuestionResponse.from_orm(q) for q in result.scalars()]
        
        if test_mode in ["full", "part2"]:
            # Get 1 Part 2 cue card
            part2_query = select(Question).where(
                and_(Question.part == 2, *base_conditions)
            ).order_by(func.random()).limit(1)
            result = await db.execute(part2_query)
            part2_questions = result.scalars().all()
            if part2_questions:
                questions["part2"] = QuestionResponse.from_orm(part2_questions[0])
        
        if test_mode in ["full", "part3"]:
            # Get 4-5 Part 3 questions
            # If we have a Part 2 question, try to get related Part 3 questions
            part3_conditions = base_conditions.copy()
            if "part2" in questions and questions["part2"]:
                part3_conditions.append(Question.topic == questions["part2"].topic)
            
            part3_query = select(Question).where(
                and_(Question.part == 3, *part3_conditions)
            ).order_by(func.random()).limit(5)
            result = await db.execute(part3_query)
            questions["part3"] = [QuestionResponse.from_orm(q) for q in result.scalars()]
        
        if test_mode == "quick":
            # Quick test: 2 Part 1, 1 Part 2, 2 Part 3
            for part, limit in [(1, 2), (2, 1), (3, 2)]:
                query = select(Question).where(
                    and_(Question.part == part, *base_conditions)
                ).order_by(func.random()).limit(limit)
                result = await db.execute(query)
                part_questions = [QuestionResponse.from_orm(q) for q in result.scalars()]
                
                if part == 2 and part_questions:
                    questions[f"part{part}"] = part_questions[0]
                else:
                    questions[f"part{part}"] = part_questions
        
        # Update usage count for selected questions
        all_question_ids = []
        for key, value in questions.items():
            if isinstance(value, list):
                all_question_ids.extend([q.id for q in value])
            elif value:
                all_question_ids.append(value.id)
        
        if all_question_ids:
            await db.execute(
                update(Question)
                .where(Question.id.in_(all_question_ids))
                .values(usage_count=Question.usage_count + 1)
            )
            await db.commit()
        
        return QuestionSet(**questions, test_mode=test_mode)
        
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve questions"
        )


@router.get("/topics", response_model=List[str])
async def get_available_topics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of available question topics
    """
    query = select(Question.topic).where(
        and_(Question.is_active == True, Question.topic != None)
    ).distinct()
    result = await db.execute(query)
    topics = [row[0] for row in result.all()]
    return sorted(topics)


@router.get("/trending", response_model=List[QuestionResponse])
async def get_trending_questions(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending/recent exam questions
    """
    query = select(Question).where(
        and_(
            Question.is_active == True,
            Question.is_trending == True
        )
    ).order_by(Question.updated_at.desc()).limit(limit)
    
    result = await db.execute(query)
    questions = result.scalars().all()
    
    return [QuestionResponse.from_orm(q) for q in questions]


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific question by ID
    """
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return QuestionResponse.from_orm(question)