from fastapi import APIRouter
from app.api.v1.endpoints import health, measurement, analyze

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(measurement.router, tags=["Measurement"])
api_router.include_router(analyze.router, tags=["Analysis"])

# 기본 ping 엔드포인트 추가
@api_router.get("/ping")
def ping():
    return {"message": "pong"}
