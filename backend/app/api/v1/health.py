"""
Health check API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Eno Health Helper Backend",
        "timestamp": "2025-01-01T00:00:00Z"
    }
