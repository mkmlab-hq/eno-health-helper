from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import base64
from datetime import datetime
import numpy as np
from app.services.health_analyzer import HealthAnalyzer

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