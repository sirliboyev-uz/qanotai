"""
Complete FastAPI app with all API endpoints for mobile app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import all routers
from app.api.auth_enhanced import router as auth_enhanced_router
from app.api.progress import router as progress_router
from app.api.subscription import router as subscription_router
from app.api.content import router as content_router
from app.api.social import router as social_router
from app.api.test_simulation import router as test_router
from app.api.localization import router as localization_router
from app.routers.payment import router as payment_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("Starting Complete QanotAI API...")
    logger.info("All endpoints are now available for mobile app")
    yield
    logger.info("Shutting down...")


# Create app
app = FastAPI(
    title="QanotAI Complete API",
    version="2.0.0",
    description="Complete IELTS Speaking Test Platform API for Mobile App",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_enhanced_router)  # Enhanced auth with phone/Google
app.include_router(progress_router)       # Progress tracking
app.include_router(subscription_router)   # Subscription management
app.include_router(content_router)        # Content & questions
app.include_router(social_router)         # Social features
app.include_router(test_router)          # Test endpoints
app.include_router(localization_router)  # Localization
app.include_router(payment_router)       # Payme payment integration


@app.get("/")
async def root():
    return {
        "message": "QanotAI Complete API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth",
            "progress": "/api/progress",
            "subscription": "/api/subscription",
            "content": "/api/content",
            "social": "/api/social",
            "test": "/api/test",
            "localization": "/api/localization"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "qanotai-api",
        "endpoints_available": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_complete:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )