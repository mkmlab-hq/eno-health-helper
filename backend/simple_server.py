#!/usr/bin/env python3
"""
엔오건강도우미 간단 백엔드 서버
즉시 실행 가능한 건강 측정 분석 시스템
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 데이터 모델 정의 ---
class HealthMeasurementRequest(BaseModel):
    user_id: Optional[str] = "anonymous"
    measurement_type: str = "combined"

class RPPGResult(BaseModel):
    heart_rate: float
    hrv: float
    stress_level: str
    confidence: float
    processing_time: float
    analysis_method: str
    signal_quality: str
    frame_count: int
    data_points: int

class VoiceResult(BaseModel):
    f0: float
    jitter: float
    shimmer: float
    hnr: float
    confidence: float
    processing_time: float
    analysis_method: str
    signal_quality: str
    duration: float
    data_points: int

class HealthMeasurementResult(BaseModel):
    measurement_id: str
    timestamp: str
    rppg_result: Optional[RPPGResult] = None
    voice_result: Optional[VoiceResult] = None
    overall_health_score: float
    recommendations: List[str]

# --- FastAPI 앱 생성 ---
app = FastAPI(
    title="엔오건강도우미 백엔드 - 간단 버전",
    description="즉시 실행 가능한 건강 측정 분석 시스템",
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

# --- API 엔드포인트 ---

@app.get("/")
async def root():
    return {"message": "엔오건강도우미 백엔드 서버가 실행 중입니다!"}

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "eno-health-helper-backend",
        "version": "1.0.0"
    }

@app.post("/api/v1/analyze")
async def analyze_health_data(request: HealthMeasurementRequest):
    """건강 데이터 분석 API"""
    start_time = time.time()
    
    try:
        # RPPG 분석 (시뮬레이션)
        rppg_result = RPPGResult(
            heart_rate=68.0 + np.random.normal(0, 5),
            hrv=55.0 + np.random.normal(0, 10),
            stress_level="Low" if np.random.random() > 0.5 else "Medium",
            confidence=85.0 + np.random.normal(0, 10),
            processing_time=time.time() - start_time,
            analysis_method="Simple RPPG Analysis",
            signal_quality="Good",
            frame_count=900,
            data_points=900
        )
        
        # 음성 분석 (시뮬레이션)
        voice_result = VoiceResult(
            f0=120.0 + np.random.normal(0, 20),
            jitter=1.2 + np.random.normal(0, 0.5),
            shimmer=2.1 + np.random.normal(0, 0.8),
            hnr=18.5 + np.random.normal(0, 3),
            confidence=88.0 + np.random.normal(0, 8),
            processing_time=time.time() - start_time,
            analysis_method="Simple Voice Analysis",
            signal_quality="Good",
            duration=5.0,
            data_points=22050
        )
        
        # 전체 건강 점수 계산
        overall_score = (
            (100 - abs(rppg_result.heart_rate - 70) / 70 * 100) * 0.4 +
            (100 - abs(rppg_result.hrv - 50) / 50 * 100) * 0.3 +
            (100 - voice_result.jitter * 10) * 0.3
        )
        
        # 건강 조언 생성
        recommendations = []
        if rppg_result.heart_rate > 80:
            recommendations.append("심박수가 높습니다. 스트레스 관리가 필요합니다.")
        if rppg_result.hrv < 40:
            recommendations.append("HRV가 낮습니다. 휴식과 명상이 도움이 됩니다.")
        if voice_result.jitter > 2.0:
            recommendations.append("음성 안정성이 낮습니다. 충분한 휴식을 취하세요.")
        
        if not recommendations:
            recommendations.append("전반적으로 건강한 상태입니다. 현재 생활을 유지하세요.")
        
        result = HealthMeasurementResult(
            measurement_id=f"measurement_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            rppg_result=rppg_result,
            voice_result=voice_result,
            overall_health_score=max(0, min(100, overall_score)),
            recommendations=recommendations
        )
        
        logger.info(f"건강 데이터 분석 완료: {result.measurement_id}")
        return result
        
    except Exception as e:
        logger.error(f"건강 데이터 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/v1/status")
async def get_status():
    """서버 상태 확인"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/",
            "/api/v1/health",
            "/api/v1/analyze",
            "/api/v1/status"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
