"""
Progress tracking API endpoints
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import random
import jwt

router = APIRouter(prefix="/api/progress", tags=["progress"])

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

class ProgressStats(BaseModel):
    totalTests: int
    averageScore: float
    improvement: float
    currentStreak: int
    bestStreak: int
    practiceMinutes: int

class WeeklyProgress(BaseModel):
    date: str
    score: float

class SkillProgress(BaseModel):
    skill: str
    score: float
    change: float

class DashboardResponse(BaseModel):
    stats: ProgressStats
    weeklyProgress: List[WeeklyProgress]
    skillBreakdown: List[SkillProgress]
    recentTests: List[dict]
    achievements: List[dict]

def get_user_id_from_token(authorization: str) -> str:
    """Extract user ID from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(authorization: Optional[str] = Header(None)):
    """
    Get user's progress dashboard data
    """
    user_id = get_user_id_from_token(authorization) if authorization else "guest"
    
    # Generate mock data (replace with database queries in production)
    stats = ProgressStats(
        totalTests=12,
        averageScore=6.5,
        improvement=15.2,
        currentStreak=5,
        bestStreak=8,
        practiceMinutes=480
    )
    
    # Generate weekly progress for last 7 days
    weekly_progress = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        score = round(5.5 + random.random() * 2, 1)
        weekly_progress.append(WeeklyProgress(date=date, score=score))
    
    # Skill breakdown
    skill_breakdown = [
        SkillProgress(skill="Fluency", score=7.0, change=5.2),
        SkillProgress(skill="Grammar", score=6.5, change=8.1),
        SkillProgress(skill="Vocabulary", score=6.8, change=12.3),
        SkillProgress(skill="Pronunciation", score=6.2, change=-2.1),
    ]
    
    # Recent tests
    recent_tests = [
        {
            "id": "test1",
            "date": datetime.now().isoformat(),
            "topic": "Technology",
            "score": 7.0,
            "duration": 900
        },
        {
            "id": "test2",
            "date": (datetime.now() - timedelta(days=2)).isoformat(),
            "topic": "Education",
            "score": 6.5,
            "duration": 850
        }
    ]
    
    # Achievements
    achievements = [
        {
            "id": "streak5",
            "title": "5 Day Streak",
            "description": "Practice 5 days in a row",
            "earnedAt": datetime.now().isoformat(),
            "icon": "🔥"
        },
        {
            "id": "first_7",
            "title": "Band 7 Achieved",
            "description": "Score 7.0 or higher",
            "earnedAt": (datetime.now() - timedelta(days=1)).isoformat(),
            "icon": "🏆"
        }
    ]
    
    return DashboardResponse(
        stats=stats,
        weeklyProgress=weekly_progress,
        skillBreakdown=skill_breakdown,
        recentTests=recent_tests,
        achievements=achievements
    )

@router.get("/tests")
async def get_test_history(
    authorization: Optional[str] = Header(None),
    limit: int = 20,
    offset: int = 0
):
    """Get user's test history"""
    user_id = get_user_id_from_token(authorization) if authorization else "guest"
    
    # Mock test history
    tests = []
    for i in range(limit):
        tests.append({
            "id": f"test_{offset + i}",
            "date": (datetime.now() - timedelta(days=i)).isoformat(),
            "topic": random.choice(["Technology", "Education", "Health", "Environment", "Culture"]),
            "score": round(5.5 + random.random() * 2.5, 1),
            "duration": random.randint(600, 1200),
            "feedback": "Good performance overall. Focus on pronunciation."
        })
    
    return {
        "tests": tests,
        "total": 50,
        "limit": limit,
        "offset": offset
    }

@router.get("/achievements")
async def get_achievements(authorization: Optional[str] = Header(None)):
    """Get user's achievements"""
    user_id = get_user_id_from_token(authorization) if authorization else "guest"
    
    return {
        "achievements": [
            {
                "id": "beginner",
                "title": "First Steps",
                "description": "Complete your first test",
                "earned": True,
                "earnedAt": datetime.now().isoformat(),
                "icon": "👶"
            },
            {
                "id": "streak10",
                "title": "10 Day Streak",
                "description": "Practice 10 days in a row",
                "earned": False,
                "progress": 0.5,
                "icon": "🔥"
            },
            {
                "id": "band8",
                "title": "Band 8 Master",
                "description": "Score 8.0 or higher",
                "earned": False,
                "progress": 0.8125,
                "icon": "🌟"
            }
        ]
    }