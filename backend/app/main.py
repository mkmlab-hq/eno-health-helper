from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import fusion_analysis, user_measurements, rppg_analysis, voice_analysis, health_score

app = FastAPI(
    title="Eno Health Helper API",
    description="AI rPPG와 음성 분석을 통한 건강 상태 측정 및 모니터링 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(fusion_analysis.router, prefix="/api")
app.include_router(user_measurements.router, prefix="/api")
app.include_router(rppg_analysis.router, prefix="/api")
app.include_router(voice_analysis.router, prefix="/api")
app.include_router(health_score.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Eno Health Helper API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-01-27T00:00:00Z"
    }
