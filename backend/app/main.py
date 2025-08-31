"""
Main FastAPI application for eno-health-helper backend.

This module provides the main application entry point and
integrates all API routers including the new MKM12 endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

# Import API routers
from app.api.v1 import health, analyze, mkm12

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Eno Health Helper Backend",
    description="Backend API for Eno Health Helper application with MKM12 theory integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(mkm12.router, prefix="/api/v1")  # MKM12 API integration

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing application information."""
    return {
        "application": "Eno Health Helper Backend",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Health monitoring",
            "Biometric analysis",
            "MKM12 theory integration",
            "Digital fingerprint generation",
            "Personalized advice"
        ],
        "api_docs": "/docs",
        "health_check": "/api/v1/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check."""
    return {
        "status": "healthy",
        "application": "Eno Health Helper Backend",
        "timestamp": "2025-01-01T00:00:00Z"
    }

# MKM12 theory information endpoint
@app.get("/mkm12-info")
async def mkm12_info():
    """Information about MKM12 theory integration."""
    return {
        "theory": "MKM12 (4 Forces, 3 Modes)",
        "description": "Mathematical theory for analyzing human behavioral patterns",
        "forces": {
            "K": "Solar force - Energy and vitality",
            "L": "Lesser Yang force - Stability and balance", 
            "S": "Lesser Yin force - Emotional expression",
            "M": "Greater Yin force - Wisdom and reflection"
        },
        "modes": {
            "A1": "Solar Mode - Leadership and creativity",
            "A2": "Yang Mode - Teamwork and collaboration",
            "A3": "Yin Mode - Intuition and emotion"
        },
        "mathematical_model": "Continuous-time nonlinear state-space dynamics",
        "api_endpoints": {
            "persona_analysis": "/api/v1/mkm12/analyze/persona",
            "digital_fingerprint": "/api/v1/mkm12/generate/digital-fingerprint",
            "personalized_advice": "/api/v1/mkm12/get/personalized-advice",
            "status": "/api/v1/mkm12/status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting Eno Health Helper Backend on {host}:{port}")
    logger.info("MKM12 theory integration enabled")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
