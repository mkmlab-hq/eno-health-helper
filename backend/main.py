#!/usr/bin/env python3
"""
엔오건강도우미 백엔드 서버
FastAPI 기반 건강 측정 분석 시스템
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import logging
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 데이터 모델 정의 ---
class RppgData(BaseModel):
    frames: List[Dict[str, Any]]

class VoiceData(BaseModel):
    audio: List[Dict[str, Any]]

class AnalysisRequest(BaseModel):
    rppg_data: RppgData
    voice_data: VoiceData

# --- FastAPI 앱 생성 ---
app = FastAPI(
    title="엔오건강도우미 백엔드",
    description="의료기기 수준 건강 측정 시스템",
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

# --- API 엔드포인트 정의 ---
@app.get("/")
async def root():
    """루트 엔드포인트"""
    logger.info("루트 엔드포인트 호출됨")
    return {
        "message": "엔오건강도우미 백엔드 서버",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/api/v1/health")
async def health_check():
    """서버 상태 확인"""
    logger.info("Health check 요청됨")
    return {
        "status": "ok",
        "message": "Backend is running",
        "timestamp": "2025-01-20T00:00:00Z"
    }

@app.post("/api/v1/analyze/rppg")
async def analyze_rppg(data: RppgData):
    """RPPG 데이터 분석"""
    try:
        logger.info(f"RPPG 분석 요청: {len(data.frames)} 프레임")
        
        num_frames = len(data.frames)
        bpm = np.random.randint(60, 90)
        hrv = np.random.randint(40, 70)
        
        if num_frames >= 30 * 25:
            quality = "Good"
        elif num_frames >= 30 * 15:
            quality = "Fair"
        else:
            quality = "Poor"
        
        result = {
            "received_frames": num_frames,
            "bpm": bpm,
            "hrv": hrv,
            "stress_level": "Low",
            "signal_quality": quality,
            "analysis_method": "simulation_v1"
        }
        
        logger.info(f"RPPG 분석 완료: BPM={bpm}, HRV={hrv}")
        return result
        
    except Exception as e:
        logger.error(f"RPPG 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RPPG 분석 중 오류: {str(e)}")

@app.post("/api/v1/analyze/voice")
async def analyze_voice(data: VoiceData):
    """음성 데이터 분석"""
    try:
        logger.info(f"음성 분석 요청: {len(data.audio)} 샘플")
        
        num_samples = len(data.audio)
        pitch = np.random.uniform(100, 200)
        jitter = np.random.uniform(0.5, 2.0)
        shimmer = np.random.uniform(1.0, 4.0)
        
        if num_samples >= 16000 * 3:
            quality = "Good"
        elif num_samples >= 16000 * 1:
            quality = "Fair"
        else:
            quality = "Poor"
        
        result = {
            "received_samples": num_samples,
            "pitch_hz": round(pitch, 1),
            "jitter_percent": round(jitter, 2),
            "shimmer_db": round(shimmer, 2),
            "stability": "Stable",
            "signal_quality": quality,
            "analysis_method": "simulation_v1"
        }
        
        logger.info(f"음성 분석 완료: Pitch={pitch:.1f}Hz")
        return result
        
    except Exception as e:
        logger.error(f"음성 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"음성 분석 중 오류: {str(e)}")

@app.post("/api/v1/analyze")
async def analyze_health_data(request: AnalysisRequest):
    """통합 건강 분석"""
    try:
        logger.info("통합 건강 분석 요청")
        
        rppg_result = await analyze_rppg(request.rppg_data)
        voice_result = await analyze_voice(request.voice_data)
        
        overall_score = 70
        
        if rppg_result["signal_quality"] == "Good":
            overall_score += 30
        elif rppg_result["signal_quality"] == "Fair":
            overall_score += 20
        else:
            overall_score += 10
        
        if voice_result["signal_quality"] == "Good":
            overall_score += 30
        elif voice_result["signal_quality"] == "Fair":
            overall_score += 20
        else:
            overall_score += 10
        
        result = {
            "rppg_results": rppg_result,
            "voice_results": voice_result,
            "overall_health_score": overall_score,
            "analysis_method": "simulation_v1"
        }
        
        logger.info(f"통합 분석 완료: 종합 점수 {overall_score}")
        return result
        
    except Exception as e:
        logger.error(f"통합 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통합 분석 중 오류: {str(e)}")

@app.get("/api/v1/status")
async def get_status():
    """시스템 상태"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "mode": "simulation",
        "features": {
            "rppg_analysis": "simulation_v1",
            "voice_analysis": "simulation_v1",
            "real_algorithm": "planned"
        }
    }

# --- 서버 실행 ---
if __name__ == "__main__":
    import uvicorn
    logger.info("백엔드 서버 시작 중...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 