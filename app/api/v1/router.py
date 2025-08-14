"""
API v1 router configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, questions, attempts, scores

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
api_router.include_router(scores.router, prefix="/scores", tags=["scores"])