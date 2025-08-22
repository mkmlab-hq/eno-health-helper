from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import base64
from datetime import datetime
import numpy as np
import logging
from app.services.health_analyzer import HealthAnalyzer

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/measure")
async def measure_health(
    background_tasks: BackgroundTasks,
    rppg_data: str = Form(..., description="RPPG 분석용 데이터 (JSON 문자열)"),
    voice_data: str = Form(..., description="음성 분석용 데이터 (JSON 문자열)"),
    rppg_result: str = Form(..., description="RPPG 분석 결과 (JSON 문자열)"),
    voice_result: str = Form(..., description="음성 분석 결과 (JSON 문자열)")
):
    """
    RPPG + Voice 통합 건강 측정 API (실제 데이터 처리)
    
    - rppg_data: 프론트엔드에서 수집한 RPPG 원시 데이터
    - voice_data: 프론트엔드에서 수집한 음성 원시 데이터
    - rppg_result: 프론트엔드에서 분석한 RPPG 결과
    - voice_result: 프론트엔드에서 분석한 음성 결과
    """
    try:
        # JSON 문자열을 파싱
        rppg_data_parsed = json.loads(rppg_data)
        voice_data_parsed = json.loads(voice_data)
        rppg_result_parsed = json.loads(rppg_result)
        voice_result_parsed = json.loads(voice_result)
        
        # 데이터 유효성 검사
        if not rppg_data_parsed or not voice_data_parsed:
            raise HTTPException(
                status_code=400,
                detail="RPPG 또는 음성 데이터가 비어있습니다."
            )
        
        # 백엔드에서 추가 분석 수행
        analyzer = HealthAnalyzer()
        enhanced_result = await analyzer.enhance_analysis(
            rppg_data_parsed,
            voice_data_parsed,
            rppg_result_parsed,
            voice_result_parsed
        )
        
        return JSONResponse(
            content={
                "success": True,
                "message": "건강 측정이 완료되었습니다.",
                "data": enhanced_result,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_method": "enhanced_backend"
            },
            status_code=200
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"JSON 파싱 오류: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"측정 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/combined")
async def measure_health_combined(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(..., description="RPPG 분석용 영상 파일"),
    audio_file: UploadFile = File(..., description="음성 분석용 오디오 파일"),
    user_id: str = Form(..., description="사용자 ID")
):
    """
    프론트엔드 통합 측정 API - '불사조 엔진' 활용
    
    - video_file: 얼굴 측정 영상 (RPPG 분석용)
    - audio_file: 음성 측정 오디오 (음성 분석용)
    - user_id: Firebase 사용자 ID
    """
    try:
        logger.info(f"🚀 통합 측정 시작: 사용자 {user_id}")
        
        # 파일 유효성 검사
        if not video_file.content_type.startswith("video/"):
            raise HTTPException(
                status_code=400,
                detail="올바른 영상 파일을 업로드해주세요."
            )

        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail="올바른 오디오 파일을 업로드해주세요."
            )

        # 파일 크기 제한 (100MB)
        if video_file.size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="영상 파일 크기가 100MB를 초과합니다."
            )

        if audio_file.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="오디오 파일 크기가 50MB를 초과합니다."
            )

        # 파일 내용 읽기
        video_content = await video_file.read()
        audio_content = await audio_file.read()
        
        logger.info(f"📁 파일 로드 완료: 영상 {len(video_content)} bytes, 오디오 {len(audio_content)} bytes")
        
        # '불사조 엔진'으로 분석 수행
        from app.services.mae_rppg_analyzer import MAERPPGAnalyzer
        from app.services.voice_analyzer import VoiceAnalyzer
        
        # 1단계: MAE rPPG 분석 (Excellent 품질)
        mae_analyzer = MAERPPGAnalyzer()
        rppg_result = await mae_analyzer.analyze_rppg_with_mae(video_content, frame_count=300)
        
        logger.info(f"✅ MAE rPPG 분석 완료: HR={rppg_result.get('heart_rate', 'N/A')} BPM, 품질={rppg_result.get('signal_quality', 'N/A')}")
        
        # 2단계: 음성 분석
        voice_analyzer = VoiceAnalyzer()
        voice_result = await voice_analyzer.analyze_voice(audio_content)
        
        logger.info(f"✅ 음성 분석 완료: F0={voice_result.get('f0', 'N/A')} Hz")
        
        # 3단계: 종합 건강 점수 계산
        health_score = calculate_health_score(rppg_result, voice_result)
        
        # 4단계: 결과 구성
        measurement_id = f"measure_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        final_result = {
            "rppg_result": {
                "heart_rate": rppg_result.get("heart_rate", 0),
                "hrv": rppg_result.get("hrv", 0),
                "stress_level": rppg_result.get("stress_level", "보통"),
                "confidence": rppg_result.get("confidence", 0.5),
                "signal_quality": rppg_result.get("signal_quality", "unknown"),
                "analysis_method": rppg_result.get("analysis_method", "MAE ViT")
            },
            "voice_result": {
                "f0": voice_result.get("f0", 0),
                "jitter": voice_result.get("jitter", 0),
                "shimmer": voice_result.get("shimmer", 0),
                "hnr": voice_result.get("hnr", 0),
                "confidence": voice_result.get("confidence", 0.5)
            },
            "health_score": health_score,
            "measurement_id": measurement_id,
            "timestamp": datetime.utcnow().isoformat(),
            "engine_version": "불사조_엔진_v2.0"
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

def calculate_health_score(rppg_result: Dict[str, Any], voice_result: Dict[str, Any]) -> float:
    """종합 건강 점수 계산"""
    try:
        # RPPG 점수 (0-50점)
        hr = rppg_result.get("heart_rate", 72)
        hrv = rppg_result.get("hrv", 50)
        
        # 심박수 점수 (정상 범위: 60-100 BPM)
        hr_score = 0
        if 60 <= hr <= 100:
            hr_score = 25
        elif 50 <= hr <= 110:
            hr_score = 20
        elif 40 <= hr <= 120:
            hr_score = 15
        else:
            hr_score = 10
        
        # HRV 점수 (정상 범위: 20-100ms)
        hrv_score = 0
        if 20 <= hrv <= 100:
            hrv_score = 25
        elif 15 <= hrv <= 120:
            hrv_score = 20
        elif 10 <= hrv <= 150:
            hrv_score = 15
        else:
            hrv_score = 10
        
        # 음성 점수 (0-50점)
        f0 = voice_result.get("f0", 200)
        jitter = voice_result.get("jitter", 0.5)
        shimmer = voice_result.get("shimmer", 0.5)
        
        # F0 점수 (정상 범위: 150-300 Hz)
        f0_score = 0
        if 150 <= f0 <= 300:
            f0_score = 25
        elif 100 <= f0 <= 400:
            f0_score = 20
        elif 80 <= f0 <= 500:
            f0_score = 15
        else:
            f0_score = 10
        
        # 음성 품질 점수
        voice_quality_score = 0
        if jitter < 0.3 and shimmer < 0.3:
            voice_quality_score = 25
        elif jitter < 0.5 and shimmer < 0.5:
            voice_quality_score = 20
        elif jitter < 0.8 and shimmer < 0.8:
            voice_quality_score = 15
        else:
            voice_quality_score = 10
        
        # 총점 계산 (0-100점)
        total_score = hr_score + hrv_score + f0_score + voice_quality_score
        
        return round(total_score, 1)
        
    except Exception as e:
        logger.error(f"건강 점수 계산 실패: {e}")
        return 50.0  # 기본값

@router.post("/measure/file")
async def measure_health_files(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(..., description="RPPG 분석용 영상 파일"),
    audio: UploadFile = File(..., description="음성 분석용 오디오 파일")
):
    """
    파일 업로드를 통한 RPPG + Voice 통합 건강 측정 API
    
    - video: MP4, AVI 등 영상 파일 (RPPG 분석용)
    - audio: WAV, MP3 등 오디오 파일 (음성 분석용)
    """
    try:
        # 파일 유효성 검사
        if not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=400,
                detail="올바른 영상 파일을 업로드해주세요."
            )

        if not audio.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail="올바른 오디오 파일을 업로드해주세요."
            )

        # 파일 크기 제한 (100MB)
        if video.size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="영상 파일 크기는 100MB 이하여야 합니다."
            )

        if audio.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="오디오 파일 크기는 50MB 이하여야 합니다."
            )

        # 파일 내용 읽기
        video_content = await video.read()
        audio_content = await audio.read()

        # 건강 분석 실행
        analyzer = HealthAnalyzer()
        result = await analyzer.analyze_health(video_content, audio_content)

        return JSONResponse(
            content={
                "success": True,
                "message": "건강 측정이 완료되었습니다.",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=200
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"측정 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/measure/status/{measurement_id}")
async def get_measurement_status(measurement_id: str):
    """측정 진행 상태 확인"""
    return {
        "measurement_id": measurement_id,
        "status": "completed",
        "progress": 100,
        "message": "측정이 완료되었습니다."
    }

@router.get("/measure/history")
async def get_measurement_history(
    limit: int = 10,
    offset: int = 0
):
    """측정 기록 조회"""
    # TODO: 데이터베이스에서 실제 기록 조회
    return {
        "measurements": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

@router.post("/measure/validate")
async def validate_measurement_data(
    rppg_data: str = Form(..., description="RPPG 데이터 유효성 검사"),
    voice_data: str = Form(..., description="음성 데이터 유효성 검사")
):
    """측정 데이터 유효성 검사"""
    try:
        rppg_data_parsed = json.loads(rppg_data)
        voice_data_parsed = json.loads(voice_data)
        
        # 데이터 품질 검사
        rppg_quality = len(rppg_data_parsed) >= 30  # 최소 30프레임
        voice_quality = len(voice_data_parsed) >= 3   # 최소 3초
        
        return {
            "rppg_quality": "good" if rppg_quality else "poor",
            "voice_quality": "good" if voice_quality else "poor",
            "overall_quality": "good" if (rppg_quality and voice_quality) else "poor",
            "recommendation": "측정을 진행할 수 있습니다." if (rppg_quality and voice_quality) else "더 안정적인 환경에서 다시 측정해주세요."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"데이터 검증 실패: {str(e)}"
        ) 