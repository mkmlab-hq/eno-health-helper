#!/usr/bin/env python3
"""
MKM Lab eno-health-helper 통합 API 서버

핵심 기능:
1. rPPG-음성 융합 분석
2. 건강 상태 종합 진단
3. 4대 디지털 기질 분석
4. 실시간 모니터링
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

# FastAPI 및 관련 라이브러리
try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from starlette.middleware.gzip import GZipMiddleware
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    print(f"FastAPI 관련 라이브러리 설치 필요: {e}")
    print("pip install fastapi uvicorn python-multipart")
    sys.exit(1)

# MKM Lab 서비스들
try:
    from app.services import (
        AdvancedFusionAnalyzer,
        EnhancedRPPGAnalyzer,
        VoiceAnalyzer,
        HealthAnalyzer
    )
except ImportError as e:
    print(f"서비스 import 오류: {e}")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="MKM Lab eno-health-helper API",
    description="AI 기반 건강 분석 및 4대 디지털 기질 진단 시스템",
    version="1.0.0"
)

# CORS/보안/성능 미들웨어
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
allow_credentials_env = os.getenv("ALLOW_CREDENTIALS", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials_env,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

force_https = os.getenv("FORCE_HTTPS", "false").lower() == "true" or os.getenv("ENV", "").lower() == "production"
if force_https:
    app.add_middleware(HTTPSRedirectMiddleware)

trusted_hosts_env = os.getenv("ALLOWED_HOSTS", "").strip()
if trusted_hosts_env:
    trusted_hosts = [h.strip() for h in trusted_hosts_env.split(",") if h.strip()]
    if trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
    )
    is_https = force_https or request.headers.get("x-forwarded-proto", "").lower() == "https"
    if is_https:
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return response

# Pydantic 모델들
class HealthData(BaseModel):
    user_id: str
    timestamp: str
    rppg_data: Optional[Dict[str, Any]] = None
    voice_data: Optional[Dict[str, Any]] = None
    emotion_data: Optional[Dict[str, Any]] = None

class AnalysisRequest(BaseModel):
    user_id: str
    analysis_type: str  # 'rppg', 'voice', 'fusion', 'health'
    data: Dict[str, Any]

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    analysis_type: str

# 서비스 인스턴스들
fusion_analyzer = AdvancedFusionAnalyzer()
rppg_analyzer = EnhancedRPPGAnalyzer()
voice_analyzer = VoiceAnalyzer()
health_analyzer = HealthAnalyzer()

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    logger.info("🚀 MKM Lab eno-health-helper API 서버 시작")
    logger.info("✅ 모든 서비스 초기화 완료")
    logger.info(f"📊 서버 시작 시간: {datetime.now()}")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "MKM Lab eno-health-helper API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "services": {
            "fusion_analyzer": "ready",
            "rppg_analyzer": "ready", 
            "voice_analyzer": "ready",
            "health_analyzer": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze/fusion", response_model=AnalysisResponse)
async def analyze_fusion(request: AnalysisRequest):
    """rPPG-음성 융합 분석"""
    try:
        logger.info(f"융합 분석 요청: {request.user_id}")
        
        # 융합 분석 실행
        result = fusion_analyzer.analyze_fusion(
            rppg_data=request.data.get('rppg_data', {}),
            voice_data=request.data.get('voice_data', {})
        )
        
        return AnalysisResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            analysis_type="fusion"
        )
        
    except Exception as e:
        logger.error(f"융합 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            analysis_type="fusion"
        )

@app.post("/api/analyze/rppg", response_model=AnalysisResponse)
async def analyze_rppg(request: AnalysisRequest):
    """rPPG 분석"""
    try:
        logger.info(f"rPPG 분석 요청: {request.user_id}")
        
        # rPPG 분석 실행
        result = rppg_analyzer.analyze_measurement_data()
        
        return AnalysisResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            analysis_type="rppg"
        )
        
    except Exception as e:
        logger.error(f"rPPG 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            analysis_type="rppg"
        )

@app.post("/api/analyze/voice", response_model=AnalysisResponse)
async def analyze_voice(request: AnalysisRequest):
    """음성 분석"""
    try:
        logger.info(f"음성 분석 요청: {request.user_id}")
        
        # 음성 분석 실행
        result = voice_analyzer.analyze_voice_data(
            audio_data=request.data.get('audio_data', {})
        )
        
        return AnalysisResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            analysis_type="voice"
        )
        
    except Exception as e:
        logger.error(f"음성 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            analysis_type="voice"
        )

@app.post("/api/analyze/health", response_model=AnalysisResponse)
async def analyze_health(request: AnalysisRequest):
    """종합 건강 분석"""
    try:
        logger.info(f"건강 분석 요청: {request.user_id}")
        
        # 종합 건강 분석 실행
        result = health_analyzer.analyze_health_data(
            health_data=request.data
        )
        
        return AnalysisResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            analysis_type="health"
        )
        
    except Exception as e:
        logger.error(f"건강 분석 오류: {e}")
        return AnalysisResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            analysis_type="health"
        )

@app.get("/api/status")
async def get_status():
    """시스템 상태 및 메트릭"""
    return {
        "status": "operational",
        "services": {
            "fusion_analyzer": "active",
            "rppg_analyzer": "active",
            "voice_analyzer": "active", 
            "health_analyzer": "active"
        },
        "uptime": "running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # 서버 실행
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌐 서버 시작: http://{host}:{port}")
    
    uvicorn.run(
        "integrated_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
