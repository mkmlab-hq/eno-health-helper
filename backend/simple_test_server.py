"""
간단한 테스트용 FastAPI 서버
엔오건강도우미 API 테스트용
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(title="엔오건강도우미 테스트 서버", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "엔오건강도우미 테스트 서버",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "message": "서버 정상 작동 중"}

@app.post("/api/v1/measure/combined")
async def measure_combined(
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """통합 건강 측정 API (테스트용)"""
    try:
        logger.info(f"측정 요청 받음: 사용자={user_id}, 비디오={video_file.filename}, 오디오={audio_file.filename}")
        
        # 파일 크기 확인
        video_size = len(await video_file.read())
        audio_size = len(await audio_file.read())
        
        # 테스트용 결과 생성
        result = {
            "success": True,
            "measurement_id": f"test_{user_id}_{video_file.filename}",
            "user_id": user_id,
            "timestamp": "2025-08-22T02:30:00",
            "result": {
                "rppg_result": {
                    "heart_rate": 75,
                    "hrv": 45,
                    "stress_level": "보통",
                    "confidence": 0.85
                },
                "voice_result": {
                    "f0": 120.5,
                    "jitter": 0.02,
                    "shimmer": 0.03,
                    "hnr": 15.2,
                    "confidence": 0.88
                },
                "health_score": 78,
                "measurement_id": f"test_{user_id}"
            },
            "file_sizes": {
                "video_bytes": video_size,
                "audio_bytes": audio_size
            },
            "analysis_type": "test_mode"
        }
        
        logger.info(f"측정 완료: {result['measurement_id']}")
        return result
        
    except Exception as e:
        logger.error(f"측정 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "측정 중 오류가 발생했습니다"
        }

@app.get("/api/v1/measure/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {
        "message": "API 엔드포인트 정상 작동",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/measure/combined",
            "/api/v1/measure/test"
        ]
    }

if __name__ == "__main__":
    logger.info("🚀 엔오건강도우미 테스트 서버 시작 중...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 