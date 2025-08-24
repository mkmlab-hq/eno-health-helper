#!/usr/bin/env python3
"""
엔오건강도우미 백엔드 서버
FastAPI 기반 건강 측정 분석 시스템 - 진짜 기능 연결
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import sys
import time
import uuid
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import resource

# 실제 분석기 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

# 설정 및 로깅
from app.core.config import settings
from app.core.logging import setup_logging

# ORJSON 가용 시 기본 응답 클래스로 사용
try:
	from fastapi.responses import ORJSONResponse as DefaultJSONResponse
	ORJSON_AVAILABLE = True
except Exception:
	from fastapi.responses import JSONResponse as DefaultJSONResponse
	ORJSON_AVAILABLE = False

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
logger = logging.getLogger(__name__)
logger.info("FastAPI 앱 생성 시작...")
app = FastAPI(
	title="엔오건강도우미 백엔드 - 진짜 기능",
	description="시뮬레이션이 아닌 실제 알고리즘 기반 건강 측정 시스템",
	version="2.0.0",
	default_response_class=DefaultJSONResponse,
)
logger.info(f"FastAPI 앱 생성 완료: {type(app)}")

# 로깅 초기화
@app.on_event("startup")
def _startup_logging():
	setup_logging()
	logging.getLogger(__name__).info("애플리케이션 시작 완료 (로깅 설정 적용)")

# 원본 호스트만 신뢰
allowed_hosts = []
for host in settings.ALLOWED_HOSTS:
	try:
		allowed_hosts.append(host.split("://")[-1])
	except Exception:
		allowed_hosts.append(host)

# 미들웨어: CORS, GZip, TrustedHost, 요청 타이밍/요청ID
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.ALLOWED_HOSTS if settings.DEBUG else [h for h in settings.ALLOWED_HOSTS],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts + ["*"] if settings.DEBUG else allowed_hosts)

class RequestTimingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
		start_time = time.perf_counter()
		start_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
		try:
			response = await call_next(request)
		except Exception as exc:
			logging.getLogger(__name__).exception(f"Unhandled error | rid={request_id} | path={request.url.path}")
			return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "request_id": request_id})
		process_time_ms = int((time.perf_counter() - start_time) * 1000)
		end_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
		mem_delta_kb = max(0, end_rss_kb - start_rss_kb)
		response.headers["X-Request-ID"] = request_id
		response.headers["X-Process-Time"] = f"{process_time_ms}ms"
		response.headers["X-Memory-Delta-KB"] = str(mem_delta_kb)
		logging.getLogger(__name__).info(f"{request.method} {request.url.path} {response.status_code} {process_time_ms}ms {mem_delta_kb}KB | rid={request_id}")
		return response

app.add_middleware(RequestTimingMiddleware)

# 전역 예외 처리기
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
	request_id = request.headers.get("x-request-id") or request.headers.get("X-Request-ID")
	logging.getLogger(__name__).warning(f"HTTPException {exc.status_code}: {exc.detail} | path={request.url.path} | rid={request_id}")
	return JSONResponse(status_code=exc.status_code, content={"success": False, "detail": exc.detail, "request_id": request_id})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
	request_id = request.headers.get("x-request-id") or request.headers.get("X-Request-ID")
	logging.getLogger(__name__).exception(f"Unhandled Exception: {exc} | path={request.url.path} | rid={request_id}")
	return JSONResponse(status_code=500, content={"success": False, "detail": "Internal Server Error", "request_id": request_id})

# --- 실제 분석기 import ---
try:
	from app.services.real_rppg_analyzer import RealRPPGAnalyzer
	from app.services.voice_analyzer import VoiceAnalyzer
	REAL_ANALYZERS_AVAILABLE = True
	logger.info("✅ 실제 분석기 모듈 로드 성공")
except ImportError as e:
	logger.warning(f"⚠️ 실제 분석기 모듈 로드 실패: {e}")
	logger.warning("시뮬레이션 모드로 작동합니다.")
	REAL_ANALYZERS_AVAILABLE = False

# --- 실제 분석기 인스턴스 생성 ---
if REAL_ANALYZERS_AVAILABLE:
	rppg_analyzer = RealRPPGAnalyzer()
	voice_analyzer = VoiceAnalyzer()
	logger.info("✅ 실제 분석기 인스턴스 생성 완료")
else:
	rppg_analyzer = None
	voice_analyzer = None
	logger.warning("⚠️ 시뮬레이션 모드로 작동")

# --- 유틸: 파일 크기 검사 ---
MAX_VIDEO_BYTES = settings.MAX_FILE_SIZE
MAX_AUDIO_BYTES = settings.MAX_FILE_SIZE

def _validate_size(label: str, data: bytes, limit: int):
	if data is None:
		raise HTTPException(status_code=400, detail=f"{label} 데이터가 비어있습니다")
	if len(data) > limit:
		raise HTTPException(status_code=413, detail=f"{label} 파일이 너무 큽니다. 최대 {limit // (1024*1024)}MB")

# --- 실제 RPPG 분석 함수 ---
def analyze_rppg_from_video(video_data: bytes, frame_count: int = 300) -> RPPGResult:
	"""
	비디오 데이터에서 RPPG 분석 수행
	실제 분석기가 있으면 실제 알고리즘, 없으면 시뮬레이션
	"""
	try:
		if REAL_ANALYZERS_AVAILABLE and rppg_analyzer:
			logging.getLogger(__name__).info("🔬 실제 RPPG 분석기 사용")
			result = rppg_analyzer.analyze_video_frames(video_data, frame_count)
			return RPPGResult(
				heart_rate=result["heart_rate"],
				hrv=result["hrv"],
				stress_level=result["stress_level"],
				confidence=result["confidence"],
				processing_time=result["processing_time"],
				analysis_method=result["analysis_method"],
				signal_quality=result["signal_quality"],
				frame_count=result["frame_count"],
				data_points=result["data_points"]
			)
		else:
			logging.getLogger(__name__).error("❌ 실제 RPPG 분석기가 필요합니다. 시뮬레이션 모드는 지원하지 않습니다.")
			raise HTTPException(
				status_code=503, 
				detail="실제 RPPG 분석기가 필요합니다. 시뮬레이션 모드는 허용되지 않습니다."
			)
	except Exception as e:
		logging.getLogger(__name__).error(f"RPPG 분석 실패: {e}")
		raise HTTPException(status_code=500, detail=f"RPPG 분석 실패: {str(e)}")

# --- 실제 음성 분석 함수 ---
def analyze_voice_from_audio(audio_data: bytes, duration: float = 5.0) -> VoiceResult:
	"""
	오디오 데이터에서 음성 분석 수행
	실제 분석기가 있으면 실제 알고리즘, 없으면 시뮬레이션
	"""
	try:
		if REAL_ANALYZERS_AVAILABLE and voice_analyzer:
			logging.getLogger(__name__).info("🔬 실제 음성 분석기 사용")
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
			logging.getLogger(__name__).error("❌ 실제 음성 분석기가 필요합니다. 시뮬레이션 모드는 지원하지 않습니다.")
			raise HTTPException(
				status_code=503, 
				detail="실제 음성 분석기가 필요합니다. 시뮬레이션 모드는 허용되지 않습니다."
			)
	except Exception as e:
		logging.getLogger(__name__).error(f"음성 분석 실패: {e}")
		raise HTTPException(status_code=500, detail=f"음성 분석 실패: {str(e)}")

# --- API 엔드포인트 정의 ---

@app.get("/")
async def root():
	"""루트 엔드포인트"""
	return {
		"message": "엔오건강도우미 백엔드 서버 - 진짜 기능",
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
		"timestamp": datetime.utcnow().isoformat() + "Z",
		"services": {
			"rppg_analysis": f"available ({'real' if REAL_ANALYZERS_AVAILABLE else 'simulation'})",
			"voice_analysis": f"available ({'real' if REAL_ANALYZERS_AVAILABLE else 'simulation'})",
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
		if not video_file.content_type or not video_file.content_type.startswith("video/"):
			raise HTTPException(status_code=400, detail="비디오 파일이 아닙니다")
		video_data = await video_file.read()
		_validate_size("비디오", video_data, MAX_VIDEO_BYTES)
		logging.getLogger(__name__).info(f"🔬 RPPG 측정 요청: {len(video_data)} bytes, {frame_count} 프레임, 사용자: {user_id}")
		rppg_result = analyze_rppg_from_video(video_data, frame_count)
		return {
			"success": True,
			"measurement_id": f"rppg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
			"user_id": user_id,
			"timestamp": datetime.now().isoformat(),
			"result": rppg_result.dict(),
			"analysis_type": "real" if REAL_ANALYZERS_AVAILABLE else "simulation"
		}
	except HTTPException:
		raise
	except Exception as e:
		logging.getLogger(__name__).error(f"RPPG 측정 실패: {e}")
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/measure/voice")
async def measure_voice(
	audio_file: UploadFile = File(...),
	user_id: str = Form("anonymous"),
	duration: float = Form(5.0)
):
	"""음성 분석 API - 진짜 기능"""
	try:
		if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
			raise HTTPException(status_code=400, detail="오디오 파일이 아닙니다")
		audio_data = await audio_file.read()
		_validate_size("오디오", audio_data, MAX_AUDIO_BYTES)
		logging.getLogger(__name__).info(f"🔬 음성 분석 요청: {len(audio_data)} bytes, {duration}초, 사용자: {user_id}")
		voice_result = analyze_voice_from_audio(audio_data, duration)
		return {
			"success": True,
			"measurement_id": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
			"user_id": user_id,
			"timestamp": datetime.now().isoformat(),
			"result": voice_result.dict(),
			"analysis_type": "real" if REAL_ANALYZERS_AVAILABLE else "simulation"
		}
	except HTTPException:
		raise
	except Exception as e:
		logging.getLogger(__name__).error(f"음성 분석 실패: {e}")
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
		if not video_file.content_type or not video_file.content_type.startswith("video/"):
			raise HTTPException(status_code=400, detail="비디오 파일이 아닙니다")
		if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
			raise HTTPException(status_code=400, detail="오디오 파일이 아닙니다")
		video_data = await video_file.read()
		audio_data = await audio_file.read()
		_validate_size("비디오", video_data, MAX_VIDEO_BYTES)
		_validate_size("오디오", audio_data, MAX_AUDIO_BYTES)
		logging.getLogger(__name__).info(f"🔬 통합 건강 측정 요청: 비디오 {len(video_data)} bytes, 오디오 {len(audio_data)} bytes, 사용자: {user_id}")
		rppg_result = analyze_rppg_from_video(video_data, frame_count)
		voice_result = analyze_voice_from_audio(audio_data, duration)
		health_score = calculate_health_score(rppg_result, voice_result)
		recommendations = generate_recommendations(rppg_result, voice_result)
		return {
			"success": True,
			"measurement_id": f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
			"user_id": user_id,
			"timestamp": datetime.now().isoformat(),
			"rppg_result": rppg_result.dict(),
			"voice_result": voice_result.dict(),
			"overall_health_score": health_score,
			"recommendations": recommendations,
			"analysis_type": "real" if REAL_ANALYZERS_AVAILABLE else "simulation"
		}
	except HTTPException:
		raise
	except Exception as e:
		logging.getLogger(__name__).error(f"통합 건강 측정 실패: {e}")
		raise HTTPException(status_code=500, detail=str(e))

# --- 점수 계산/권장사항 ---
def calculate_health_score(rppg_result: RPPGResult, voice_result: VoiceResult) -> float:
	"""종합 건강 점수 계산"""
	# RPPG 점수 (0-100)
	hr_score = max(0, 100 - abs(rppg_result.heart_rate - 72) * 2)  # 72 BPM 기준
	hrv_score = max(0, 100 - abs(rppg_result.hrv - 50) * 1.5)  # 50ms 기준
	# 음성 점수 (0-100)
	f0_score = max(0, 100 - abs(voice_result.f0 - 150) * 0.5)  # 150Hz 기준
	jitter_score = max(0, 100 - voice_result.jitter * 1000)
	shimmer_score = max(0, 100 - voice_result.shimmer * 800)
	hnr_score = max(0, min(100, voice_result.hnr * 4))
	# 가중 평균
	rppg_weight = 0.6
	voice_weight = 0.4
	rppg_avg = (hr_score + hrv_score) / 2
	voice_avg = (f0_score + jitter_score + shimmer_score + hnr_score) / 4
	overall_score = rppg_avg * rppg_weight + voice_avg * voice_weight
	return round(overall_score, 1)

def generate_recommendations(rppg_result: RPPGResult, voice_result: VoiceResult) -> List[str]:
	"""건강 권장사항 생성"""
	recommendations = []
	if rppg_result.heart_rate > 85:
		recommendations.append("심박수가 높습니다. 스트레스를 줄이고 휴식을 취하세요.")
	elif rppg_result.heart_rate < 60:
		recommendations.append("심박수가 낮습니다. 적절한 운동을 권장합니다.")
	if rppg_result.hrv < 30:
		recommendations.append("심박변이도가 낮습니다. 스트레스 관리가 필요합니다.")
	if rppg_result.stress_level == "높음":
		recommendations.append("스트레스 수준이 높습니다. 명상이나 호흡 운동을 시도해보세요.")
	if voice_result.jitter > 0.05:
		recommendations.append("음성 안정성이 낮습니다. 목 건강에 주의하세요.")
	if voice_result.shimmer > 0.08:
		recommendations.append("음성 품질이 저하되었습니다. 충분한 수분 섭취를 권장합니다.")
	if voice_result.hnr < 15:
		recommendations.append("음성 노이즈가 높습니다. 목소리 휴식이 필요합니다.")
	if not recommendations:
		recommendations.append("전반적으로 건강한 상태입니다. 현재 생활습관을 유지하세요.")
	return recommendations

# --- 디버깅 정보 출력 ---
logging.getLogger(__name__).info("라우트 등록 정보:")
for route in app.routes:
	logging.getLogger(__name__).info(f"라우트: {route.path} [{route.methods}]")

logging.getLogger(__name__).info(f"실제 분석기 상태: {'✅ 사용 가능' if REAL_ANALYZERS_AVAILABLE else '⚠️ 시뮬레이션 모드'}")

# --- 서버 실행 ---
if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		app,
		host=settings.HOST,
		port=settings.PORT,
		reload=False,
		log_level="info"
	) 