"""
Analysis API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/analyze")
async def analyze_status():
    """Analysis service status."""
    return {
        "status": "available",
        "service": "Analysis API",
        "capabilities": ["rPPG", "Voice Analysis", "MKM12"]
    }
