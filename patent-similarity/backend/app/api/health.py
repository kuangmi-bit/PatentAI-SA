"""
Health check and system status API endpoints
"""
from datetime import datetime
from fastapi import APIRouter

from app.models.schemas import HealthResponse
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }
