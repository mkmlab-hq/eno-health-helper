"""
rPPG-음성 융합 분석 API 엔드포인트

이 모듈은 융합 분석을 위한 REST API 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import numpy as np
import cv2
import librosa
import tempfile
import os
from datetime import datetime
import logging

# 상위 디렉토리 import
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.append(str(backend_path))

from app.services.fusion_analyzer import AdvancedFusionAnalyzer
from app.services.rppg_analyzer import MedicalGradeRPPGAnalyzer
from app.services.voice_analyzer import MedicalGradeVoiceAnalyzer
from config.fusion_config import get_config, PerformanceOptimizer

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/fusion", tags=["fusion-analysis"])

# 융합 분석기 초기화
fusion_analyzer = AdvancedFusionAnalyzer()
rppg_analyzer = MedicalGradeRPPGAnalyzer()
voice_analyzer = MedicalGradeVoiceAnalyzer()

# 성능 최적화기 초기화
config = get_config()
performance_optimizer = PerformanceOptimizer(config)


@router.post("/analyze")
async def analyze_fusion(
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...)
) -> Dict[str, Any]:
    """
    rPPG-음성 융합 분석 수행
    
    Args:
        video_file: 비디오 파일 (MP4, AVI 등)
        audio_file: 오디오 파일 (WAV, MP3 등)
        user_id: 사용자 ID
        session_id: 세션 ID
        
    Returns:
        융합 분석 결과
    """
    try:
        logger.info(f"융합 분석 시작: user_id={user_id}, session_id={session_id}")
        
        # 파일 유효성 검사
        if not video_file.filename or not audio_file.filename:
            raise HTTPException(status_code=400, detail="비디오와 오디오 파일이 필요합니다")
        
        # 파일 확장자 검사
        video_ext = video_file.filename.lower().split('.')[-1]
        audio_ext = audio_file.filename.lower().split('.')[-1]
        
        if video_ext not in ['mp4', 'avi', 'mov', 'mkv']:
            raise HTTPException(status_code=400, detail="지원하지 않는 비디오 형식입니다")
        
        if audio_ext not in ['wav', 'mp3', 'm4a', 'flac']:
            raise HTTPException(status_code=400, detail="지원하지 않는 오디오 형식입니다")
        
        # 파일 처리
        video_frames = await process_video_file(video_file)
        audio_signal = await process_audio_file(audio_file)
        
        # 개별 분석 수행
        rppg_result = await analyze_rppg(video_frames)
        voice_result = await analyze_voice(audio_signal)
        
        # 융합 분석 수행
        fusion_result = await perform_fusion_analysis(
            rppg_result, voice_result, video_frames, audio_signal
        )
        
        # 결과에 메타데이터 추가
        fusion_result.update({
            "user_id": user_id,
            "session_id": session_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "file_info": {
                "video_file": video_file.filename,
                "audio_file": audio_file.filename,
                "video_frames": len(video_frames),
                "audio_duration": len(audio_signal) / 22050  # 샘플레이트 가정
            }
        })
        
        logger.info(f"융합 분석 완료: user_id={user_id}, session_id={session_id}")
        return fusion_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"융합 분석 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")


@router.post("/analyze-json")
async def analyze_fusion_json(
    rppg_data: Dict[str, Any],
    voice_data: Dict[str, Any],
    user_id: str,
    session_id: str
) -> Dict[str, Any]:
    """
    JSON 데이터를 통한 융합 분석 (기존 분석 결과 활용)
    
    Args:
        rppg_data: rPPG 분석 결과
        voice_data: 음성 분석 결과
        user_id: 사용자 ID
        session_id: 세션 ID
        
    Returns:
        융합 분석 결과
    """
    try:
        logger.info(f"JSON 융합 분석 시작: user_id={user_id}, session_id={session_id}")
        
        # 융합 분석 수행
        fusion_result = await perform_fusion_analysis(
            rppg_data, voice_data, None, None
        )
        
        # 결과에 메타데이터 추가
        fusion_result.update({
            "user_id": user_id,
            "session_id": session_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "input_type": "json_data"
        })
        
        logger.info(f"JSON 융합 분석 완료: user_id={user_id}, session_id={session_id}")
        return fusion_result
        
    except Exception as e:
        logger.error(f"JSON 융합 분석 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/performance")
async def get_performance_summary() -> Dict[str, Any]:
    """융합 분석기 성능 요약 반환"""
    try:
        performance_summary = fusion_analyzer.get_performance_summary()
        return {
            "status": "success",
            "data": performance_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"성능 요약 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"성능 요약 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """융합 분석기 상태 확인"""
    try:
        return {
            "status": "healthy",
            "service": "fusion-analyzer",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {
                "fusion_analyzer": "active",
                "rppg_analyzer": "active",
                "voice_analyzer": "active"
            }
        }
    except Exception as e:
        logger.error(f"상태 확인 중 오류 발생: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def process_video_file(video_file: UploadFile) -> List[np.ndarray]:
    """비디오 파일 처리 및 프레임 추출"""
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix=f'.{video_file.filename.split(".")[-1]}', delete=False) as temp_file:
            content = await video_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # OpenCV로 비디오 읽기
            cap = cv2.VideoCapture(temp_file_path)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 프레임 크기 조정 (메모리 최적화)
                frame = cv2.resize(frame, (640, 480))
                frames.append(frame)
                
                # 최대 프레임 수 제한
                if len(frames) >= 300:  # 10초 @ 30fps
                    break
            
            cap.release()
            
            logger.info(f"비디오 처리 완료: {len(frames)} 프레임 추출")
            return frames
            
        finally:
            # 임시 파일 정리
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"비디오 파일 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"비디오 파일 처리 중 오류가 발생했습니다: {str(e)}")


async def process_audio_file(audio_file: UploadFile) -> np.ndarray:
    """오디오 파일 처리 및 신호 추출"""
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix=f'.{audio_file.filename.split(".")[-1]}', delete=False) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # librosa로 오디오 로드
            audio_signal, sample_rate = librosa.load(
                temp_file_path,
                sr=22050,  # 표준 샘플레이트
                mono=True
            )
            # 1) 앞뒤 무음 제거
            trimmed, _ = librosa.effects.trim(audio_signal, top_db=30)
            # 2) 간단한 에너지 기반 VAD
            frame_length = 2048
            hop_length = 512
            energy = librosa.feature.rms(y=trimmed, frame_length=frame_length, hop_length=hop_length)[0]
            vad_mask = energy > (np.median(energy) * 0.6)
            reconstructed = []
            for i, keep in enumerate(vad_mask):
                start = i * hop_length
                end = min(len(trimmed), start + frame_length)
                if keep:
                    reconstructed.append(trimmed[start:end])
            if reconstructed:
                vad_signal = np.concatenate(reconstructed)
            else:
                vad_signal = trimmed
            # 3) 프리엠퍼시스 + 정규화
            pre_emphasis = 0.97
            emphasized = np.append(vad_signal[0], vad_signal[1:] - pre_emphasis * vad_signal[:-1])
            if np.max(np.abs(emphasized)) > 0:
                emphasized = emphasized / np.max(np.abs(emphasized))
            
            logger.info(f"오디오 처리 완료: {len(emphasized)} 샘플, {sample_rate}Hz")
            return emphasized
            
        finally:
            # 임시 파일 정리
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"오디오 파일 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"오디오 파일 처리 중 오류가 발생했습니다: {str(e)}")


async def analyze_rppg(video_frames: List[np.ndarray]) -> Dict[str, Any]:
    """rPPG 분석 수행"""
    try:
        if not video_frames:
            return {"error": "비디오 프레임이 없습니다"}
        
        # rPPG 분석 수행
        rppg_result = rppg_analyzer.analyze_rppg(video_frames)
        
        logger.info("rPPG 분석 완료")
        return rppg_result
        
    except Exception as e:
        logger.error(f"rPPG 분석 중 오류: {e}")
        return {"error": f"rPPG 분석 실패: {str(e)}"}


async def analyze_voice(audio_signal: np.ndarray) -> Dict[str, Any]:
    """음성 분석 수행"""
    try:
        if len(audio_signal) == 0:
            return {"error": "오디오 신호가 없습니다"}
        
        # 음성을 bytes로 변환 (기존 voice_analyzer 인터페이스 맞춤)
        audio_bytes = audio_signal.tobytes()
        
        # 음성 분석 수행
        voice_result = voice_analyzer.analyze_voice(audio_bytes)
        
        logger.info("음성 분석 완료")
        return voice_result
        
    except Exception as e:
        logger.error(f"음성 분석 중 오류: {e}")
        return {"error": f"음성 분석 실패: {str(e)}"}


async def perform_fusion_analysis(
    rppg_result: Dict[str, Any],
    voice_result: Dict[str, Any],
    video_frames: Optional[List[np.ndarray]],
    audio_signal: Optional[np.ndarray]
) -> Dict[str, Any]:
    """융합 분석 수행"""
    try:
        # 오류 체크
        if "error" in rppg_result:
            logger.warning(f"rPPG 분석 오류: {rppg_result['error']}")
        
        if "error" in voice_result:
            logger.warning(f"음성 분석 오류: {voice_result['error']}")
        
        # 융합 분석 수행
        fusion_result = fusion_analyzer.analyze_fusion(
            rppg_result, voice_result, video_frames, audio_signal
        )
        
        # 성능 최적화 제안 추가
        if hasattr(fusion_analyzer, 'get_performance_summary'):
            performance_summary = fusion_analyzer.get_performance_summary()
            if performance_summary and "total_analyses" in performance_summary:
                if performance_summary["total_analyses"] > 10:
                    optimization_suggestions = performance_optimizer.suggest_optimizations(
                        performance_summary
                    )
                    fusion_result["optimization_suggestions"] = optimization_suggestions
        
        logger.info("융합 분석 완료")
        return fusion_result
        
    except Exception as e:
        logger.error(f"융합 분석 중 오류: {e}")
        return {
            "error": f"융합 분석 실패: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        } 