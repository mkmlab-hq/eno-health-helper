from fastapi import APIRouter
<<<<<<< HEAD
from app.api.v1.endpoints import health, measurement, analyze

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(measurement.router, tags=["Measurement"])
api_router.include_router(analyze.router, tags=["Analysis"]) 
=======

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}
>>>>>>> cc17bd21ebec23ae8472e255a559b421cb47b61d
