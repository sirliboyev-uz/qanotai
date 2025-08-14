"""
FastAPI app with authentication (Epic 1 implementation)
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.api.auth import router as auth_router
from app.core.auth import get_current_user
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("Starting QanotAI API with Authentication...")
    yield
    logger.info("Shutting down...")


# Create app
app = FastAPI(
    title="QanotAI API",
    version="1.0.0",
    description="IELTS Speaking Test Platform with Authentication",
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "QanotAI API",
        "version": "1.0.0",
        "status": "running",
        "authentication": "enabled",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}


@app.get("/api/v1/protected")
async def protected_route(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Example protected endpoint"""
    if not current_user:
        return {"message": "This endpoint is public but can detect auth"}
    
    return {
        "message": "You are authenticated!",
        "user": current_user
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)