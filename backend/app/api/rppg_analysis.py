from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import base64
import cv2
import numpy as np
from PIL import Image
import io
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rppg", tags=["rPPG Analysis"])


class RPPGAnalyzer:
    """실제 rPPG 알고리즘을 구현한 클래스"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def detect_face(self, frame: np.ndarray) -> tuple:
        """얼굴 감지 및 ROI 추출"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None, None
            
        # 가장 큰 얼굴 선택
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        # ROI 추출 (얼굴 중앙 부분)
        roi = frame[y:y+h, x:x+w]
        return roi, (x, y, w, h)
    
    def extract_skin_region(self, face_roi: np.ndarray) -> np.ndarray:
        """피부 영역 추출 (HSV 색상 공간 활용)"""
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        
        # 피부색 범위 정의
        lower_skin = np.array([0, 20, 70])
        upper_skin = np.array([20, 255, 255])
        
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((3, 3), np.uint8)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        
        return skin_mask
    
    def calculate_heart_rate(self, frames: List[np.ndarray], 
                           frame_rate: int = 30) -> dict:
        """실제 rPPG 알고리즘을 이용한 심박수 계산"""
        if len(frames) < frame_rate * 2:  # 최소 2초 필요
            raise ValueError("최소 2초의 프레임이 필요합니다")
        
        # 각 프레임에서 피부 영역의 평균 RGB 값 추출
        skin_values = []
        
        for frame in frames:
            face_roi, _ = self.detect_face(frame)
            if face_roi is not None:
                skin_mask = self.extract_skin_region(face_roi)
                if np.sum(skin_mask) > 0:
                    # 피부 영역의 평균 RGB 값 계산
                    skin_pixels = face_roi[skin_mask > 0]
                    if len(skin_pixels) > 0:
                        avg_rgb = np.mean(skin_pixels, axis=0)
                        skin_values.append(avg_rgb)
        
        # 50% 이상의 프레임에서 얼굴 감지 필요
        if len(skin_values) < len(frames) * 0.5:
            raise ValueError("충분한 얼굴 프레임을 감지할 수 없습니다")
        
        skin_values = np.array(skin_values)
        
        # FFT를 이용한 주파수 분석
        green_channel = skin_values[:, 1]  # G 채널이 혈류 변화에 민감
        
        # 신호 전처리
        green_channel = green_channel - np.mean(green_channel)
        
        # FFT 적용
        fft_result = np.fft.fft(green_channel)
        freqs = np.fft.fftfreq(len(green_channel), 1/frame_rate)
        
        # 유효한 주파수 범위 (0.8Hz ~ 3Hz, 48-180 BPM)
        valid_mask = (freqs > 0.8) & (freqs < 3.0)
        valid_freqs = freqs[valid_mask]
        valid_fft = np.abs(fft_result[valid_mask])
        
        if len(valid_freqs) == 0:
            raise ValueError("유효한 주파수를 찾을 수 없습니다")
        
        # 최대 진폭의 주파수 찾기
        max_idx = np.argmax(valid_fft)
        heart_rate_freq = valid_freqs[max_idx]
        heart_rate_bpm = heart_rate_freq * 60
        
        # 신호 품질 평가
        signal_quality = self.assess_signal_quality(valid_fft, heart_rate_bpm)
        
        # HRV 계산 (간단한 버전)
        hrv = self.calculate_hrv(green_channel, frame_rate)
        
        return {
            "heart_rate": round(heart_rate_bpm, 1),
            "hrv": round(hrv, 1),
            "signal_quality": signal_quality,
            "confidence": self.calculate_confidence(valid_fft, max_idx)
        }
    
    def assess_signal_quality(self, fft_magnitude: np.ndarray, 
                            heart_rate: float) -> str:
        """신호 품질 평가"""
        max_magnitude = np.max(fft_magnitude)
        mean_magnitude = np.mean(fft_magnitude)
        
        snr = max_magnitude / mean_magnitude if mean_magnitude > 0 else 0
        
        if snr > 5.0:
            return "우수"
        elif snr > 3.0:
            return "양호"
        elif snr > 2.0:
            return "보통"
        else:
            return "낮음"
    
    def calculate_hrv(self, signal: np.ndarray, frame_rate: int) -> float:
        """심박변이도 계산 (간단한 버전)"""
        # 피크 감지
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                peaks.append(i)
        
        if len(peaks) < 2:
            return 0.0
        
        # R-R 간격 계산
        rr_intervals = np.diff(peaks) / frame_rate
        
        # HRV (RMSSD)
        hrv = np.sqrt(np.mean(np.diff(rr_intervals) ** 2)) * 1000  # ms 단위
        
        return hrv
    
    def calculate_confidence(self, fft_magnitude: np.ndarray, 
                           max_idx: int) -> float:
        """측정 신뢰도 계산"""
        max_magnitude = fft_magnitude[max_idx]
        total_energy = np.sum(fft_magnitude ** 2)
        
        if total_energy == 0:
            return 0.0
        
        confidence = (max_magnitude ** 2) / total_energy
        return min(confidence * 100, 100.0)  # 0-100% 범위


@router.post("/analyze")
async def analyze_rppg(frames: List[str], frame_rate: int = 30):
    """rPPG 분석 API 엔드포인트"""
    try:
        logger.info(f"rPPG 분석 시작: {len(frames)}개 프레임, {frame_rate}fps")
        
        if len(frames) < frame_rate:
            raise HTTPException(
                status_code=400, 
                detail="최소 1초의 프레임이 필요합니다"
            )
        
        # Base64 디코딩 및 프레임 변환
        decoded_frames = []
        for i, frame_b64 in enumerate(frames):
            try:
                # Base64 디코딩
                frame_data = base64.b64decode(
                    frame_b64.split(',')[1] if ',' in frame_b64 else frame_b64
                )
                
                # PIL Image로 변환
                image = Image.open(io.BytesIO(frame_data))
                
                # OpenCV 형식으로 변환
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                decoded_frames.append(frame)
                
                if i % 30 == 0:  # 30프레임마다 로그
                    logger.info(f"프레임 {i+1}/{len(frames)} 처리 완료")
                    
            except Exception as e:
                logger.warning(f"프레임 {i} 디코딩 실패: {str(e)}")
                continue
        
        if len(decoded_frames) < frame_rate:
            raise HTTPException(
                status_code=400, 
                detail="유효한 프레임이 부족합니다"
            )
        
        # rPPG 분석 실행
        analyzer = RPPGAnalyzer()
        result = analyzer.calculate_heart_rate(decoded_frames, frame_rate)
        
        # 스트레스 레벨 추정
        stress_level = estimate_stress_level(result["heart_rate"], result["hrv"])
        
        # 최종 결과
        final_result = {
            "success": True,
            "heart_rate": result["heart_rate"],
            "hrv": result["hrv"],
            "stress_level": stress_level,
            "signal_quality": result["signal_quality"],
            "confidence": result["confidence"],
            "analysis_time": len(decoded_frames) / frame_rate,
            "frames_processed": len(decoded_frames)
        }
        
        logger.info(
            f"rPPG 분석 완료: 심박수 {result['heart_rate']} BPM, "
            f"HRV {result['hrv']} ms"
        )
        
        return JSONResponse(content=final_result)
        
    except Exception as e:
        logger.error(f"rPPG 분석 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"rPPG 분석 중 오류 발생: {str(e)}"
        )


def estimate_stress_level(heart_rate: float, hrv: float) -> str:
    """심박수와 HRV를 기반으로 스트레스 레벨 추정"""
    # 스트레스 점수 계산 (0-100)
    stress_score = 0
    
    # 심박수 기반 스트레스 (60-100 BPM이 정상)
    if heart_rate < 60:
        stress_score += 20  # 서맥
    elif heart_rate > 100:
        stress_score += 30  # 빈맥
    elif heart_rate > 80:
        stress_score += 15  # 약간 높음
    
    # HRV 기반 스트레스 (높을수록 스트레스 낮음)
    if hrv < 20:
        stress_score += 40  # 매우 높은 스트레스
    elif hrv < 40:
        stress_score += 25  # 높은 스트레스
    elif hrv < 60:
        stress_score += 15  # 보통 스트레스
    
    # 스트레스 레벨 분류
    if stress_score >= 60:
        return "높음"
    elif stress_score >= 40:
        return "보통"
    elif stress_score >= 20:
        return "낮음"
    else:
        return "매우 낮음"


@router.get("/health")
async def rppg_health_check():
    """rPPG 서비스 상태 확인"""
    return {
        "service": "rPPG Analysis", 
        "status": "healthy", 
        "version": "2.0.0",
        "features": [
            "실제 OpenCV 기반 얼굴 감지",
            "피부 영역 추출 및 분석",
            "FFT 기반 심박수 계산",
            "HRV 및 스트레스 레벨 추정",
            "신호 품질 평가"
        ]
    }
