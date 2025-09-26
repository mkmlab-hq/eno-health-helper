#!/usr/bin/env python3
"""
엔오건강도우미 백엔드 서버
FastAPI 기반 건강 측정 분석 시스템 - 진짜 기능 연결
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import sys

# 실제 분석기 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- mkm-core-ai 통합 인터페이스 import ---
try:
    from app.services.mkm_core_ai_integration import MKMCoreAIIntegration
    from app.services.voice_analyzer import VoiceAnalyzer
    REAL_ANALYZERS_AVAILABLE = True
    logger.info("✅ mkm-core-ai 통합 인터페이스 로드 성공")
except ImportError as e:
    logger.warning(f"⚠️ mkm-core-ai 통합 인터페이스 로드 실패: {e}")
    logger.warning("시뮬레이션 모드로 작동합니다.")
    REAL_ANALYZERS_AVAILABLE = False

# --- 데이터 모델 정의 ---
class HealthMeasurementRequest(BaseModel):
    user_id: Optional[str] = "anonymous"
    measurement_type: str = "combined"  # "rppg", "voice", "combined"

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
logger.info("FastAPI 앱 생성 시작...")
app = FastAPI(
    title="엔오건강도우미 백엔드 - 진짜 기능",
    description="시뮬레이션이 아닌 실제 알고리즘 기반 건강 측정 시스템",
    version="2.0.0"
)

logger.info(f"FastAPI 앱 생성 완료: {type(app)}")

# Redis 기반 FastAPI 캐시 초기화
try:
    from app import init_cache
    init_cache(app)
    logger.info("FastAPI Cache with Redis 초기화 완료")
except Exception as e:
    logger.warning(f"FastAPI Cache 초기화 실패: {e}")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS 미들웨어 추가 완료")

# --- mkm-core-ai 통합 인터페이스 인스턴스 생성 ---
if REAL_ANALYZERS_AVAILABLE:
    rppg_analyzer = MKMCoreAIIntegration()
    voice_analyzer = VoiceAnalyzer()
    logger.info("✅ mkm-core-ai 통합 인터페이스 인스턴스 생성 완료")
else:
    rppg_analyzer = None
    voice_analyzer = None
    logger.warning("⚠️ 시뮬레이션 모드로 작동")

# --- 실제 RPPG 분석 함수 ---
async def analyze_rppg_from_video(video_data: bytes, frame_count: int = 300) -> RPPGResult:
    """
    비디오 데이터에서 RPPG 분석 수행
    실제 분석기가 있으면 실제 알고리즘, 없으면 서비스 불가
    """
    try:
        if REAL_ANALYZERS_AVAILABLE and rppg_analyzer:
            logger.info("🔬 mkm-core-ai RPPG 분석기 사용")
            result = await rppg_analyzer.analyze_rppg(video_data, frame_count)
            
            return RPPGResult(
                heart_rate=result["heart_rate"],
                hrv=result["hrv"],
                stress_level=result["stress_level"],
                confidence=result["confidence"],
                processing_time=result["processing_time"],
                analysis_method=result["analysis_method"],
                signal_quality=result["signal_quality"],
                frame_count=frame_count,
                data_points=result["data_points"]
            )
        else:
            logger.error("❌ 실제 RPPG 분석기를 사용할 수 없습니다")
            raise HTTPException(
                status_code=503, 
                detail="건강 분석 서비스를 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요."
            )
        
    except Exception as e:
        logger.error(f"RPPG 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"RPPG 분석 실패: {str(e)}")

# --- 실제 음성 분석 함수 ---
def analyze_voice_from_audio(audio_data: bytes, duration: float = 5.0) -> VoiceResult:
    """
    오디오 데이터에서 음성 분석 수행
    실제 분석기가 있으면 실제 알고리즘, 없으면 서비스 불가
    """
    try:
        if REAL_ANALYZERS_AVAILABLE and voice_analyzer:
            logger.info("🔬 실제 음성 분석기 사용")
            result = voice_analyzer.analyze_audio_data(audio_data, duration)
            
            return VoiceResult(
                f0=result["f0"],
                jitter=result["jitter"],
                shimmer=result["shimmer"],
                hnr=result["hnr"],
                confidence=result["confidence"],
                processing_time=result["processing_time"],
                analysis_method=result["analysis_method"],
                signal_quality=result["signal_quality"],
                duration=result["duration"],
                data_points=result["data_points"]
            )
        else:
            logger.error("❌ 실제 음성 분석기를 사용할 수 없습니다")
            raise HTTPException(
                status_code=503, 
                detail="건강 분석 서비스를 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요."
            )
        
    except Exception as e:
        logger.error(f"음성 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"음성 분석 실패: {str(e)}")

# --- API 엔드포인트 정의 ---

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "엔오건강도우미 백엔드 서버 - 실제 건강 분석 도구",
        "status": "running",
        "real_analyzers": REAL_ANALYZERS_AVAILABLE,
        "version": "2.0.0"
    }

@app.get("/api/v1/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "ok",
        "message": "Backend is running",
        "timestamp": "2025-01-20T00:00:00Z",
        "services": {
            "rppg_analysis": "available (real)" if REAL_ANALYZERS_AVAILABLE else "unavailable",
            "voice_analysis": "available (real)" if REAL_ANALYZERS_AVAILABLE else "unavailable",
            "data_storage": "available",
            "real_analyzers_loaded": REAL_ANALYZERS_AVAILABLE
        }
    }

@app.post("/api/v1/measure/rppg")
async def measure_rppg(
    video_file: UploadFile = File(...),
    user_id: str = Form("anonymous"),
    frame_count: int = Form(300)
):
    """RPPG 측정 API - 진짜 기능"""
    try:
        # 비디오 파일 검증
        if not video_file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="비디오 파일이 아닙니다")
        
        # 비디오 데이터 읽기
        video_data = await video_file.read()
        logger.info(f"🔬 RPPG 측정 요청: {len(video_data)} bytes, {frame_count} 프레임, 사용자: {user_id}")
        
        # RPPG 분석 수행
        rppg_result = await analyze_rppg_from_video(video_data, frame_count)
        
        # 결과 반환
        return {
            "success": True,
            "measurement_id": f"rppg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "result": rppg_result.model_dump(),
            "analysis_type": "real"
        }
        
    except Exception as e:
        logger.error(f"RPPG 측정 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/measure/voice")
async def measure_voice(
    audio_file: UploadFile = File(...),
    user_id: str = Form("anonymous"),
    duration: float = Form(5.0)
):
    """음성 분석 API - 진짜 기능"""
    try:
        # 오디오 파일 검증
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="오디오 파일이 아닙니다")
        
        # 오디오 데이터 읽기
        audio_data = await audio_file.read()
        logger.info(f"🔬 음성 분석 요청: {len(audio_data)} bytes, {duration}초, 사용자: {user_id}")
        
        # 음성 분석 수행
        voice_result = analyze_voice_from_audio(audio_data, duration)
        
        # 결과 반환
        return {
            "success": True,
            "measurement_id": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "result": voice_result.model_dump(),
            "analysis_type": "real"
        }
        
    except Exception as e:
        logger.error(f"음성 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/measure/combined")
async def measure_combined_health(
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    user_id: str = Form("anonymous"),
    frame_count: int = Form(300),
    duration: float = Form(5.0)
):
    """통합 건강 측정 API - 진짜 기능 (RPPG + 음성)"""
    try:
        # 파일 검증
        if not video_file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="비디오 파일이 아닙니다")
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="오디오 파일이 아닙니다")
        
        # 데이터 읽기
        video_data = await video_file.read()
        audio_data = await audio_file.read()
        logger.info(f"🔬 통합 건강 측정 요청: 비디오 {len(video_data)} bytes, 오디오 {len(audio_data)} bytes, 사용자: {user_id}")
        
        # 분석 수행
        rppg_result = await analyze_rppg_from_video(video_data, frame_count)
        voice_result = analyze_voice_from_audio(audio_data, duration)
        
        # 종합 건강 점수 계산
        health_score = calculate_health_score(rppg_result, voice_result)
        
        # 권장사항 생성
        recommendations = generate_recommendations(rppg_result, voice_result)
        
        # 결과 반환
        return {
            "success": True,
            "measurement_id": f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "rppg_result": rppg_result.model_dump(),
            "voice_result": voice_result.model_dump(),
            "overall_health_score": health_score,
            "recommendations": recommendations,
            "analysis_type": "real"
        }
        
    except Exception as e:
        logger.error(f"통합 건강 측정 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_health_score(rppg_result: RPPGResult, voice_result: VoiceResult) -> float:
    """종합 건강 점수 계산"""
    # RPPG 점수 (0-100)
    hr_score = max(0, 100 - abs(rppg_result.heart_rate - 72) * 2)  # 72 BPM 기준
    hrv_score = max(0, 100 - abs(rppg_result.hrv - 50) * 1.5)  # 50ms 기준
    
    # 음성 점수 (0-100)
    f0_score = max(0, 100 - abs(voice_result.f0 - 150) * 0.5)  # 150Hz 기준
    jitter_score = max(0, 100 - voice_result.jitter * 1000)  # 지터 낮을수록 좋음
    shimmer_score = max(0, 100 - voice_result.shimmer * 800)  # 시머 낮을수록 좋음
    hnr_score = max(0, min(100, voice_result.hnr * 4))  # HNR 높을수록 좋음
    
    # 가중 평균 계산
    rppg_weight = 0.6
    voice_weight = 0.4
    
    rppg_avg = (hr_score + hrv_score) / 2
    voice_avg = (f0_score + jitter_score + shimmer_score + hnr_score) / 4
    
    overall_score = rppg_avg * rppg_weight + voice_avg * voice_weight
    
    return round(overall_score, 1)

def generate_recommendations(rppg_result: RPPGResult, voice_result: VoiceResult) -> List[str]:
    """건강 권장사항 생성"""
    recommendations = []
    
    # RPPG 기반 권장사항
    if rppg_result.heart_rate > 85:
        recommendations.append("심박수가 높습니다. 스트레스를 줄이고 휴식을 취하세요.")
    elif rppg_result.heart_rate < 60:
        recommendations.append("심박수가 낮습니다. 적절한 운동을 권장합니다.")
    
    if rppg_result.hrv < 30:
        recommendations.append("심박변이도가 낮습니다. 스트레스 관리가 필요합니다.")
    
    if rppg_result.stress_level == "높음":
        recommendations.append("스트레스 수준이 높습니다. 명상이나 호흡 운동을 시도해보세요.")
    
    # 음성 기반 권장사항
    if voice_result.jitter > 0.05:
        recommendations.append("음성 안정성이 낮습니다. 목 건강에 주의하세요.")
    
    if voice_result.shimmer > 0.08:
        recommendations.append("음성 품질이 저하되었습니다. 충분한 수분 섭취를 권장합니다.")
    
    if voice_result.hnr < 15:
        recommendations.append("음성 노이즈가 높습니다. 목소리 휴식이 필요합니다.")
    
    # 기본 권장사항
    if not recommendations:
        recommendations.append("전반적으로 건강한 상태입니다. 현재 생활습관을 유지하세요.")
    
    return recommendations

# --- 디버깅 정보 출력 ---
logger.info(f"등록된 라우트 수: {len(app.routes)}")
for route in app.routes:
    logger.info(f"라우트: {route.path} [{route.methods}]")

logger.info(f"실제 분석기 상태: {'✅ 사용 가능' if REAL_ANALYZERS_AVAILABLE else '⚠️ 시뮬레이션 모드'}")

# --- 서버 실행 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 