"""Common API routes (health, supported tests) without rate limiting."""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["common"])

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "medical-report-processor"}