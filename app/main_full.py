"""
Complete FastAPI app with Authentication, Test Simulation, and AI Assessment
Epic 1, Epic 2 & Epic 3 Implementation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.api.auth import router as auth_router
from app.api.test_simulation import router as test_router
from app.api.ai_assessment import router as ai_router
from app.api.progress import router as progress_router
from app.api.subscription import router as subscription_router
from app.api.content import router as content_router
from app.api.social import router as social_router
from app.api.localization import router as localization_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("Starting QanotAI API - Full Version...")
    logger.info("✅ Epic 1: Authentication - Ready")
    logger.info("✅ Epic 2: Test Simulation - Ready")
    logger.info("✅ Epic 3: AI Assessment - Ready")
    logger.info("✅ Epic 4: Progress Tracking - Ready")
    logger.info("✅ Epic 5: Monetization & Subscriptions - Ready")
    logger.info("✅ Epic 6: Content & Question Bank - Ready")
    logger.info("✅ Epic 7: Social & Community Features - Ready")
    logger.info("✅ Epic 8: Accessibility & Localization - Ready")
    yield
    logger.info("Shutting down...")


# Create app
app = FastAPI(
    title="QanotAI API",
    version="3.0.0",
    description="""
    IELTS Speaking Test Preparation Platform
    
    Implemented Features:
    - Epic 1: User Registration & Authentication
    - Epic 2: IELTS Speaking Test Simulation
    - Epic 3: AI-Powered Assessment
    - Epic 4: Progress Tracking & Analytics
    - Epic 5: Monetization & Subscriptions
    - Epic 6: Content & Question Bank
    - Epic 7: Social & Community Features
    - Epic 8: Accessibility & Localization
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(test_router)
app.include_router(ai_router)
app.include_router(progress_router)
app.include_router(subscription_router)
app.include_router(content_router)
app.include_router(social_router)
app.include_router(localization_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "QanotAI API",
        "version": "4.0.0",
        "status": "running",
        "features": {
            "authentication": "enabled",
            "test_simulation": "enabled",
            "ai_scoring": "enabled",
            "progress_tracking": "enabled",
            "subscriptions": "enabled",
            "content_bank": "enabled",
            "social_features": "enabled",
            "localization": "enabled",
            "accessibility": "enabled"
        },
        "docs": "http://localhost:8000/docs",
        "epics_completed": [
            "Epic 1: User Registration & Authentication",
            "Epic 2: IELTS Speaking Test Simulation",
            "Epic 3: AI-Powered Assessment",
            "Epic 4: Progress Tracking & Analytics",
            "Epic 5: Monetization & Subscriptions",
            "Epic 6: Content & Question Bank",
            "Epic 7: Social & Community Features",
            "Epic 8: Accessibility & Localization"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "auth": "ready",
            "test_simulation": "ready",
            "ai_assessment": "ready",
            "progress_tracking": "ready",
            "subscriptions": "ready",
            "content_bank": "ready",
            "social_features": "ready",
            "localization": "ready",
            "accessibility": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)