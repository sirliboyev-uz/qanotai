"""
Epic 6: Content & Question Bank API Endpoints
US-6.1: Browse Question Topics
US-6.2: Daily Challenge
US-6.3: Trending Topics
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import random
from ..models.content_models import (
    QuestionTopic,
    Question,
    DailyChallenge,
    UserChallenge,
    TrendingTopic,
    UserTopicPreference,
    QuestionSubmission,
    TestPart,
    QuestionDifficulty,
    TopicCategory,
    TopicBrowseRequest,
    TopicBrowseResponse,
    QuestionResponse,
    DailyChallengeResponse,
    TrendingTopicsResponse,
    StartChallengeRequest,
    SubmitChallengeResponse,
    FavoriteTopicRequest,
    SubmitQuestionRequest,
    SAMPLE_TOPICS,
    SAMPLE_QUESTIONS
)
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/content", tags=["Content & Question Bank"])

# Mock data stores (replace with actual database in production)
topics_db: List[QuestionTopic] = []
questions_db: List[Question] = []
daily_challenges_db: List[DailyChallenge] = []
user_challenges_db: List[UserChallenge] = []
trending_topics_db: List[TrendingTopic] = []
user_preferences_db: List[UserTopicPreference] = []
question_submissions_db: List[QuestionSubmission] = []

# Initialize with sample data
def _initialize_sample_data():
    """Initialize database with sample topics and questions"""
    global topics_db, questions_db
    
    # Create topics from sample data
    for topic_data in SAMPLE_TOPICS:
        topic = QuestionTopic(**topic_data)
        topics_db.append(topic)
    
    # Create questions from sample data and link to topics
    for question_data in SAMPLE_QUESTIONS:
        # Find matching topic
        topic = None
        for t in topics_db:
            if t.category == question_data["category"]:
                topic = t
                break
        
        if topic:
            question_data["topic_id"] = topic.id
            question = Question(**question_data)
            questions_db.append(question)

# Initialize sample data on module load
_initialize_sample_data()

@router.get("/topics", response_model=TopicBrowseResponse)
async def browse_topics(
    category: Optional[TopicCategory] = Query(None),
    part: Optional[TestPart] = Query(None),
    difficulty: Optional[QuestionDifficulty] = Query(None),
    search_query: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("popularity"),
    include_favorites: bool = Query(False),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-6.1: Browse Question Topics
    Get organized list of IELTS topics with filtering and search
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Start with all topics
    filtered_topics = topics_db.copy()
    
    # Apply filters
    if category:
        filtered_topics = [t for t in filtered_topics if t.category == category]
    
    if difficulty:
        filtered_topics = [t for t in filtered_topics if t.difficulty_level == difficulty]
    
    # Search functionality
    if search_query:
        query_lower = search_query.lower()
        filtered_topics = [
            t for t in filtered_topics 
            if (query_lower in t.name.lower() or 
                query_lower in t.description.lower() or
                any(query_lower in tag.lower() for tag in t.tags) or
                any(query_lower in keyword.lower() for keyword in t.keywords))
        ]
    
    # Include favorites filter
    if include_favorites:
        user_favorites = [
            pref.topic_id for pref in user_preferences_db 
            if pref.user_id == user_id and pref.is_favorite
        ]
        filtered_topics = [t for t in filtered_topics if t.id in user_favorites]
    
    # Sort topics
    if sort_by == "popularity":
        filtered_topics.sort(key=lambda x: x.popularity_score, reverse=True)
    elif sort_by == "name":
        filtered_topics.sort(key=lambda x: x.name)
    elif sort_by == "difficulty":
        difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
        filtered_topics.sort(key=lambda x: difficulty_order.get(x.difficulty_level, 2))
    elif sort_by == "trending":
        filtered_topics.sort(key=lambda x: (x.is_trending, x.trend_score), reverse=True)
    
    # Pagination
    total_count = len(filtered_topics)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_topics = filtered_topics[start_idx:end_idx]
    
    # Get available categories
    categories = list(set(t.category for t in topics_db))
    
    # Get trending topic IDs
    trending_topic_ids = [t.id for t in topics_db if t.is_trending]
    
    return TopicBrowseResponse(
        topics=paginated_topics,
        total_count=total_count,
        page=page,
        per_page=per_page,
        has_more=end_idx < total_count,
        categories=categories,
        trending_topics=trending_topic_ids
    )

@router.get("/topics/{topic_id}", response_model=QuestionResponse)
async def get_topic_details(
    topic_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific topic including questions
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find topic
    topic = None
    for t in topics_db:
        if t.id == topic_id:
            topic = t
            break
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get questions for this topic
    topic_questions = [q for q in questions_db if q.topic_id == topic_id and q.is_active]
    
    # Get related questions (same category, different topic)
    related_questions = [
        q for q in questions_db 
        if q.category == topic.category and q.topic_id != topic_id and q.is_active
    ][:3]  # Limit to 3 related questions
    
    # Get user stats for this topic
    user_stats = None
    for pref in user_preferences_db:
        if pref.user_id == user_id and pref.topic_id == topic_id:
            user_stats = {
                "is_favorite": pref.is_favorite,
                "interest_level": pref.interest_level,
                "practice_count": pref.practice_count,
                "average_score": pref.average_score,
                "mastery_level": pref.mastery_level
            }
            break
    
    # If no user stats exist, create default
    if not user_stats:
        user_stats = {
            "is_favorite": False,
            "interest_level": 3,
            "practice_count": 0,
            "average_score": 0.0,
            "mastery_level": 0.0
        }
    
    # Return first question as main example
    main_question = topic_questions[0] if topic_questions else None
    
    return QuestionResponse(
        question=main_question,
        topic=topic,
        related_questions=related_questions,
        user_stats=user_stats
    )

@router.get("/questions")
async def get_questions(
    topic_id: Optional[str] = Query(None),
    part: Optional[TestPart] = Query(None),
    difficulty: Optional[QuestionDifficulty] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get questions with filtering options
    """
    # Start with all active questions
    filtered_questions = [q for q in questions_db if q.is_active]
    
    # Apply filters
    if topic_id:
        filtered_questions = [q for q in filtered_questions if q.topic_id == topic_id]
    
    if part:
        filtered_questions = [q for q in filtered_questions if q.part == part]
    
    if difficulty:
        filtered_questions = [q for q in filtered_questions if q.difficulty == difficulty]
    
    # Limit results
    filtered_questions = filtered_questions[:limit]
    
    return {
        "questions": filtered_questions,
        "total_count": len(filtered_questions)
    }

@router.get("/daily-challenge", response_model=DailyChallengeResponse)
async def get_daily_challenge(
    challenge_date: Optional[date] = Query(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-6.2: Daily Challenge
    Get today's or specific date's daily challenge
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Use today if no date specified
    if not challenge_date:
        challenge_date = date.today()
    
    # Find challenge for the date
    challenge = None
    for c in daily_challenges_db:
        if c.challenge_date == challenge_date and c.is_active:
            challenge = c
            break
    
    # Create challenge if none exists for today
    if not challenge and challenge_date == date.today():
        challenge = _create_daily_challenge(challenge_date)
        daily_challenges_db.append(challenge)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="No challenge found for this date")
    
    # Get questions for the challenge
    challenge_questions = []
    all_question_ids = (challenge.part_1_questions + 
                       ([challenge.part_2_question] if challenge.part_2_question else []) + 
                       challenge.part_3_questions)
    
    for q_id in all_question_ids:
        question = next((q for q in questions_db if q.id == q_id), None)
        if question:
            challenge_questions.append(question)
    
    # Get user participation
    user_participation = None
    for uc in user_challenges_db:
        if uc.user_id == user_id and uc.challenge_id == challenge.id:
            user_participation = uc
            break
    
    # Create mock leaderboard (top 5 participants)
    leaderboard = [
        {"rank": 1, "username": "Anonymous", "score": 8.5, "completion_time": 4},
        {"rank": 2, "username": "Anonymous", "score": 8.0, "completion_time": 5},
        {"rank": 3, "username": "Anonymous", "score": 7.5, "completion_time": 6},
        {"rank": 4, "username": "Anonymous", "score": 7.0, "completion_time": 5},
        {"rank": 5, "username": "Anonymous", "score": 6.5, "completion_time": 7}
    ]
    
    return DailyChallengeResponse(
        challenge=challenge,
        questions=challenge_questions,
        user_participation=user_participation,
        leaderboard=leaderboard
    )

@router.post("/daily-challenge/start")
async def start_daily_challenge(
    request: StartChallengeRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Start participating in today's daily challenge
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find the challenge
    challenge = None
    for c in daily_challenges_db:
        if c.id == request.challenge_id:
            challenge = c
            break
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if user already started this challenge
    existing_participation = None
    for uc in user_challenges_db:
        if uc.user_id == user_id and uc.challenge_id == challenge.id:
            existing_participation = uc
            break
    
    if existing_participation:
        return {
            "message": "Challenge already started",
            "participation_id": existing_participation.id,
            "started_at": existing_participation.started_at
        }
    
    # Create new participation
    user_challenge = UserChallenge(
        user_id=user_id,
        challenge_id=challenge.id
    )
    user_challenges_db.append(user_challenge)
    
    return {
        "message": "Challenge started successfully",
        "participation_id": user_challenge.id,
        "challenge": challenge,
        "started_at": user_challenge.started_at
    }

@router.post("/daily-challenge/complete")
async def complete_daily_challenge(
    request: SubmitChallengeResponse,
    current_user: Dict = Depends(get_current_user)
):
    """
    Submit completion of daily challenge
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find user participation
    user_participation = None
    for uc in user_challenges_db:
        if uc.user_id == user_id and uc.challenge_id == request.challenge_id:
            user_participation = uc
            break
    
    if not user_participation:
        raise HTTPException(status_code=404, detail="Challenge participation not found")
    
    if user_participation.is_completed:
        raise HTTPException(status_code=400, detail="Challenge already completed")
    
    # Calculate overall score (mock calculation)
    total_score = sum(response.get("score", 0) for response in request.responses)
    overall_score = total_score / len(request.responses) if request.responses else 0
    
    # Update participation
    user_participation.is_completed = True
    user_participation.completed_at = datetime.utcnow()
    user_participation.overall_score = overall_score
    user_participation.completion_time_minutes = request.completion_time_minutes
    user_participation.responses = request.responses
    
    # Update streak (mock logic)
    user_participation.is_streak_day = True
    user_participation.current_streak = _calculate_user_streak(user_id)
    
    return {
        "message": "Challenge completed successfully",
        "overall_score": overall_score,
        "completion_time": request.completion_time_minutes,
        "streak_count": user_participation.current_streak,
        "badge_earned": user_participation.current_streak > 0 and user_participation.current_streak % 7 == 0
    }

@router.get("/trending", response_model=TrendingTopicsResponse)
async def get_trending_topics(
    region: Optional[str] = Query(None),
    period: str = Query("weekly"),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-6.3: Trending Topics
    Get currently trending IELTS topics
    """
    # Filter trending topics
    filtered_trending = trending_topics_db.copy()
    
    if region:
        filtered_trending = [t for t in filtered_trending if t.region == region or t.region is None]
    
    if period:
        filtered_trending = [t for t in filtered_trending if t.trend_period == period]
    
    # Sort by trend score
    filtered_trending.sort(key=lambda x: x.trend_score, reverse=True)
    
    # Get corresponding topics
    trending_topic_ids = [t.topic_id for t in filtered_trending]
    trending_topics = [t for t in topics_db if t.id in trending_topic_ids]
    
    # Get available regions
    regions = list(set(t.region for t in trending_topics_db if t.region))
    
    return TrendingTopicsResponse(
        trending=filtered_trending[:10],  # Top 10 trending
        topics=trending_topics,
        regions=regions,
        last_updated=datetime.utcnow()
    )

@router.post("/favorites")
async def toggle_favorite_topic(
    request: FavoriteTopicRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-6.1: Favorite topics feature
    Add or remove topic from favorites
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Check if topic exists
    topic = None
    for t in topics_db:
        if t.id == request.topic_id:
            topic = t
            break
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Find existing preference
    preference = None
    for pref in user_preferences_db:
        if pref.user_id == user_id and pref.topic_id == request.topic_id:
            preference = pref
            break
    
    # Create or update preference
    if not preference:
        preference = UserTopicPreference(
            user_id=user_id,
            topic_id=request.topic_id,
            is_favorite=request.is_favorite,
            interest_level=request.interest_level or 3
        )
        user_preferences_db.append(preference)
    else:
        preference.is_favorite = request.is_favorite
        if request.interest_level:
            preference.interest_level = request.interest_level
        preference.updated_at = datetime.utcnow()
    
    return {
        "message": f"Topic {'added to' if request.is_favorite else 'removed from'} favorites",
        "topic_name": topic.name,
        "is_favorite": preference.is_favorite,
        "interest_level": preference.interest_level
    }

@router.get("/favorites")
async def get_favorite_topics(current_user: Dict = Depends(get_current_user)):
    """
    Get user's favorite topics
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get user's favorite topic IDs
    favorite_topic_ids = [
        pref.topic_id for pref in user_preferences_db 
        if pref.user_id == user_id and pref.is_favorite
    ]
    
    # Get the corresponding topics
    favorite_topics = [t for t in topics_db if t.id in favorite_topic_ids]
    
    # Get preferences for additional info
    preferences = {
        pref.topic_id: pref for pref in user_preferences_db 
        if pref.user_id == user_id and pref.is_favorite
    }
    
    # Combine topic info with preferences
    favorites_with_stats = []
    for topic in favorite_topics:
        pref = preferences.get(topic.id)
        topic_info = {
            "topic": topic,
            "interest_level": pref.interest_level if pref else 3,
            "practice_count": pref.practice_count if pref else 0,
            "average_score": pref.average_score if pref else 0.0,
            "last_practiced": pref.last_practiced if pref else None
        }
        favorites_with_stats.append(topic_info)
    
    return {
        "favorites": favorites_with_stats,
        "total_count": len(favorites_with_stats)
    }

@router.post("/submit-question")
async def submit_question(
    request: SubmitQuestionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-6.3: User-submitted questions for trending topics
    Submit a new question from recent test experience
    """
    user_id = current_user.get("uid", "unknown_user")
    
    submission = QuestionSubmission(
        user_id=user_id,
        question_text=request.question_text,
        suggested_part=request.part,
        suggested_category=request.category,
        test_location=request.test_context.get("location") if request.test_context else None,
        test_date=request.test_context.get("date") if request.test_context else None
    )
    
    question_submissions_db.append(submission)
    
    return {
        "message": "Question submitted successfully",
        "submission_id": submission.id,
        "status": "pending_review",
        "estimated_review_time": "24-48 hours"
    }

@router.get("/search")
async def search_content(
    query: str = Query(..., min_length=2),
    search_type: str = Query("all"),  # "topics", "questions", "all"
    limit: int = Query(20, ge=1, le=50),
    current_user: Dict = Depends(get_current_user)
):
    """
    US-6.1: Search functionality
    Search across topics and questions
    """
    query_lower = query.lower()
    results = {"topics": [], "questions": []}
    
    # Search topics
    if search_type in ["topics", "all"]:
        matching_topics = []
        for topic in topics_db:
            if (query_lower in topic.name.lower() or
                query_lower in topic.description.lower() or
                any(query_lower in tag.lower() for tag in topic.tags) or
                any(query_lower in keyword.lower() for keyword in topic.keywords)):
                matching_topics.append(topic)
        
        results["topics"] = matching_topics[:limit]
    
    # Search questions
    if search_type in ["questions", "all"]:
        matching_questions = []
        for question in questions_db:
            if (query_lower in question.text.lower() or
                any(query_lower in tag.lower() for tag in question.tags) or
                any(query_lower in keyword.lower() for keyword in question.keywords)):
                matching_questions.append(question)
        
        results["questions"] = matching_questions[:limit]
    
    return {
        "query": query,
        "results": results,
        "total_topics": len(results["topics"]),
        "total_questions": len(results["questions"])
    }

# Helper functions

def _create_daily_challenge(challenge_date: date) -> DailyChallenge:
    """Create a new daily challenge for the given date"""
    
    # Select random questions for different parts
    part1_questions = [q for q in questions_db if q.part == TestPart.PART_1 and q.is_active]
    part2_questions = [q for q in questions_db if q.part == TestPart.PART_2 and q.is_active]
    part3_questions = [q for q in questions_db if q.part == TestPart.PART_3 and q.is_active]
    
    # Randomly select questions
    selected_part1 = random.sample(part1_questions, min(2, len(part1_questions)))
    selected_part2 = random.sample(part2_questions, min(1, len(part2_questions)))
    selected_part3 = random.sample(part3_questions, min(1, len(part3_questions)))
    
    # Create theme based on selected questions
    themes = [
        "Personal Experiences",
        "Technology & Modern Life", 
        "Travel & Culture",
        "Work & Education",
        "Environment & Society"
    ]
    
    challenge = DailyChallenge(
        challenge_date=challenge_date,
        title=f"Daily Challenge - {challenge_date.strftime('%B %d')}",
        description="Today's speaking practice challenge",
        part_1_questions=[q.id for q in selected_part1],
        part_2_question=selected_part2[0].id if selected_part2 else None,
        part_3_questions=[q.id for q in selected_part3],
        theme=random.choice(themes),
        focus_skills=["fluency", "vocabulary", "pronunciation"],
        estimated_duration_minutes=5
    )
    
    return challenge

def _calculate_user_streak(user_id: str) -> int:
    """Calculate user's current challenge completion streak"""
    user_completions = [
        uc for uc in user_challenges_db 
        if uc.user_id == user_id and uc.is_completed
    ]
    
    if not user_completions:
        return 1
    
    # Sort by completion date
    user_completions.sort(key=lambda x: x.completed_at, reverse=True)
    
    # Count consecutive days
    streak = 1
    current_date = date.today()
    
    for completion in user_completions:
        completion_date = completion.completed_at.date()
        if completion_date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break
    
    return streak

# Initialize some trending topics
def _initialize_trending_data():
    """Initialize trending topics data"""
    global trending_topics_db
    
    if not trending_topics_db and topics_db:
        for i, topic in enumerate(topics_db[:3]):  # Make first 3 topics trending
            trending = TrendingTopic(
                topic_id=topic.id,
                trend_score=0.9 - (i * 0.1),
                position_change=random.randint(-2, 3),
                trend_start_date=date.today() - timedelta(days=random.randint(1, 7)),
                data_sources=["user_reports", "official_ielts"],
                confidence_score=0.8 + (i * 0.05)
            )
            trending_topics_db.append(trending)

# Initialize trending data
_initialize_trending_data()