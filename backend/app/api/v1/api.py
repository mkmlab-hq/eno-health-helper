from fastapi import APIRouter
from app.api.v1.endpoints import health, measurement, analyze

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(measurement.router, tags=["Measurement"])
api_router.include_router(analyze.router, tags=["Analysis"]) 