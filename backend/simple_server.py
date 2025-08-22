#!/usr/bin/env python3
"""
간단한 테스트 서버 - '불사조 엔진' API 테스트용
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="불사조 엔진 테스트 서버",
    description="Phase 3 웹 앱 통합 테스트용 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "불사조 엔진 테스트 서버가 실행 중입니다!"}

@app.get("/api/v1/ping")
async def ping():
    """서버 상태 확인"""
    return {"message": "pong", "status": "running", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/measure/combined")
async def measure_health_combined(
    video_file: UploadFile = File(..., description="RPPG 분석용 영상 파일"),
    audio_file: UploadFile = File(..., description="음성 분석용 오디오 파일"),
    user_id: str = Form(..., description="사용자 ID")
):
    """통합 측정 API - '불사조 엔진' 시뮬레이션"""
    try:
        logger.info(f"🚀 통합 측정 시작: 사용자 {user_id}")
        
        # 파일 내용 읽기
        video_content = await video_file.read()
        audio_content = await audio_file.read()
        
        logger.info(f"📁 파일 로드 완료: 영상 {len(video_content)} bytes, 오디오 {len(audio_content)} bytes")
        
        # 시뮬레이션된 분석 결과
        rppg_result = {
            "heart_rate": 72.0,
            "hrv": 45.0,
            "stress_level": "보통",
            "confidence": 0.85,
            "signal_quality": "excellent",
            "analysis_method": "MAE ViT - 시뮬레이션"
        }
        
        voice_result = {
            "f0": 180.0,
            "jitter": 0.25,
            "shimmer": 0.30,
            "hnr": 22.0,
            "confidence": 0.80
        }
        
        # 건강 점수 계산
        health_score = 85.5
        
        # 측정 ID 생성
        measurement_id = f"measure_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        final_result = {
            "rppg_result": rppg_result,
            "voice_result": voice_result,
            "health_score": health_score,
            "measurement_id": measurement_id,
            "timestamp": datetime.now().isoformat(),
            "engine_version": "불사조_엔진_v2.0_시뮬레이션"
        }
        
        logger.info(f"🎉 통합 측정 완료: 건강점수 {health_score}, 측정ID {measurement_id}")
        
        return JSONResponse(
            content=final_result,
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"❌ 통합 측정 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"측정 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/api/v1/health")
async def health_check():
    """건강 상태 확인"""
    return {
        "status": "healthy",
        "engine": "불사조_엔진_v2.0",
        "phase": "Phase 3 - 웹 앱 통합",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 불사조 엔진 테스트 서버 시작...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
