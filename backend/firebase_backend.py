"""
Firebase 우선 연동 백엔드
rPPG 및 음성 분석을 Firebase와 연동하여 처리
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, firestore, storage
import numpy as np
import cv2

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(title="Firebase 우선 연동 백엔드", version="1.0.0")

# CORS 설정 (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://eno.no1kmedi.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 초기화
try:
    # Firebase Admin SDK 초기화 (서비스 계정 키 필요)
    if not firebase_admin._apps:
        # 새로 생성된 서비스 계정 키 파일 경로
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'eno-health-helper.firebasestorage.app'
        })
    
    db = firestore.client()
    bucket = storage.bucket()
    logger.info("✅ Firebase 연결 성공")
    
except Exception as e:
    logger.error(f"❌ Firebase 연결 실패: {e}")
    # Firebase 연결 실패 시에도 기본 기능 제공
    db = None
    bucket = None

class FirebaseHealthAnalyzer:
    """Firebase 연동 건강 분석기"""
    
    def __init__(self):
        self.db = db
        self.bucket = bucket
    
    async def analyze_rppg_from_video(self, video_data: bytes, user_id: str) -> Dict[str, Any]:
        """비디오에서 rPPG 분석 (Firebase 연동)"""
        try:
            # 간단한 rPPG 분석 (실제 구현 필요)
            analysis_result = {
                "heart_rate": 72,
                "hrv": 50,
                "stress_level": "낮음",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Firebase에 결과 저장
            if self.db:
                doc_ref = self.db.collection('rppg_analyses').document()
                doc_ref.set(analysis_result)
                analysis_result['firebase_id'] = doc_ref.id
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ rPPG 분석 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def analyze_voice_from_audio(self, audio_data: bytes, user_id: str) -> Dict[str, Any]:
        """오디오에서 음성 분석 (Firebase 연동)"""
        try:
            # 간단한 음성 분석 (실제 구현 필요)
            analysis_result = {
                "f0": 175,
                "jitter": 1.5,
                "shimmer": 2.0,
                "hnr": 18.5,
                "confidence": 0.88,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Firebase에 결과 저장
            if self.db:
                doc_ref = self.db.collection('voice_analyses').document()
                doc_ref.set(analysis_result)
                analysis_result['firebase_id'] = doc_ref.id
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 음성 분석 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def save_measurement_data(self, user_id: str, data_type: str, 
                                   file_data: bytes, analysis_result: Dict[str, Any]) -> str:
        """측정 데이터를 Firebase Storage에 저장"""
        try:
            if not self.bucket:
                return "firebase_storage_unavailable"
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{user_id}/{data_type}/{timestamp}.bin"
            
            # Firebase Storage에 업로드
            blob = self.bucket.blob(filename)
            blob.upload_from_string(file_data, content_type='application/octet-stream')
            
            # 메타데이터 저장
            metadata = {
                "filename": filename,
                "user_id": user_id,
                "data_type": data_type,
                "upload_time": timestamp,
                "analysis_result": analysis_result
            }
            
            if self.db:
                doc_ref = self.db.collection('measurement_files').document()
                doc_ref.set(metadata)
                return doc_ref.id
            
            return "metadata_saved"
            
        except Exception as e:
            logger.error(f"❌ 데이터 저장 실패: {e}")
            return "storage_failed"

# 전역 분석기 인스턴스
health_analyzer = FirebaseHealthAnalyzer()

# API 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Firebase 우선 연동 백엔드 서버",
        "status": "running",
        "firebase_connected": db is not None,
        "version": "1.0.0"
    }

@app.post("/api/v1/measure/rppg")
async def measure_rppg(
    video_file: UploadFile = File(...),
    user_id: str = Form("anonymous")
):
    """rPPG 측정 API (Firebase 연동)"""
    try:
        # 비디오 파일 검증
        if not video_file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="비디오 파일이 아닙니다")
        
        # 비디오 데이터 읽기
        video_data = await video_file.read()
        logger.info(f"🔬 rPPG 측정 요청: {len(video_data)} bytes, 사용자: {user_id}")
        
        # rPPG 분석 수행
        analysis_result = await health_analyzer.analyze_rppg_from_video(video_data, user_id)
        
        # 데이터 저장
        file_id = await health_analyzer.save_measurement_data(
            user_id, "rppg_video", video_data, analysis_result
        )
        
        return {
            "success": True,
            "measurement_id": f"rppg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "result": analysis_result,
            "file_id": file_id,
            "analysis_type": "firebase_integrated"
        }
        
    except Exception as e:
        logger.error(f"rPPG 측정 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/measure/voice")
async def measure_voice(
    audio_file: UploadFile = File(...),
    user_id: str = Form("anonymous")
):
    """음성 분석 API (Firebase 연동)"""
    try:
        # 오디오 파일 검증
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="오디오 파일이 아닙니다")
        
        # 오디오 데이터 읽기
        audio_data = await audio_file.read()
        logger.info(f"🔬 음성 분석 요청: {len(audio_data)} bytes, 사용자: {user_id}")
        
        # 음성 분석 수행
        analysis_result = await health_analyzer.analyze_voice_from_audio(audio_data, user_id)
        
        # 데이터 저장
        file_id = await health_analyzer.save_measurement_data(
            user_id, "voice_audio", audio_data, analysis_result
        )
        
        return {
            "success": True,
            "measurement_id": f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "result": analysis_result,
            "file_id": file_id,
            "analysis_type": "firebase_integrated"
        }
        
    except Exception as e:
        logger.error(f"음성 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/measure/combined")
async def measure_combined_health(
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    user_id: str = Form("anonymous")
):
    """통합 건강 측정 API (Firebase 연동)"""
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
        rppg_result = await health_analyzer.analyze_rppg_from_video(video_data, user_id)
        voice_result = await health_analyzer.analyze_voice_from_audio(audio_data, user_id)
        
        # 종합 건강 점수 계산
        health_score = (rppg_result.get("confidence", 0) + voice_result.get("confidence", 0)) / 2 * 100
        
        # 데이터 저장
        video_file_id = await health_analyzer.save_measurement_data(
            user_id, "combined_video", video_data, rppg_result
        )
        audio_file_id = await health_analyzer.save_measurement_data(
            user_id, "combined_audio", audio_data, voice_result
        )
        
        return {
            "success": True,
            "measurement_id": f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "rppg_result": rppg_result,
            "voice_result": voice_result,
            "health_score": round(health_score, 1),
            "video_file_id": video_file_id,
            "audio_file_id": audio_file_id,
            "analysis_type": "firebase_integrated"
        }
        
    except Exception as e:
        logger.error(f"통합 건강 측정 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/user/{user_id}/measurements")
async def get_user_measurements(user_id: str):
    """사용자 측정 기록 조회 (Firebase 연동)"""
    try:
        if not db: # Corrected: db is a global variable, no need to pass self
            raise HTTPException(status_code=503, detail="Firebase 연결이 불가능합니다")
        
        # 사용자의 측정 기록 조회
        rppg_docs = db.collection('rppg_analyses').where('user_id', '==', user_id).stream()
        voice_docs = db.collection('voice_analyses').where('user_id', '==', user_id).stream()
        
        measurements = {
            "rppg_analyses": [doc.to_dict() for doc in rppg_docs],
            "voice_analyses": [doc.to_dict() for doc in voice_docs]
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "measurements": measurements
        }
        
    except Exception as e:
        logger.error(f"측정 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 