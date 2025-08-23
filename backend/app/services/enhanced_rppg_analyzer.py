import cv2
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, List, Optional, Tuple, Any
import logging
import json
import os
from pathlib import Path
from datetime import datetime

# 새로 생성된 서비스들 import
from .signal_quality_validator import SignalQualityValidator
from .error_handler import MeasurementErrorHandler
from .measurement_protocol_manager import MeasurementProtocolManager, MeasurementPhase

logger = logging.getLogger(__name__)

class EnhancedRPPGAnalyzer:
    """
    향상된 RPPG 분석 엔진
    
    기존 RPPG 분석 기능에 다음을 추가:
    1. 신호 품질 검증
    2. 에러 핸들링 및 복구
    3. 표준화된 측정 프로토콜
    4. 실시간 품질 모니터링
    """
    
    def __init__(self):
        # 기존 RPPG 분석기 초기화
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # RPPG 분석 파라미터
        self.fps = 30
        self.min_face_size = (50, 50)
        self.roi_padding = 20
        self.min_hr = 40
        self.max_hr = 200
        self.min_freq = 0.7
        self.max_freq = 4.0
        
        # 새로 추가된 서비스들
        self.quality_validator = SignalQualityValidator()
        self.error_handler = MeasurementErrorHandler()
        self.protocol_manager = MeasurementProtocolManager()
        
        # 측정 상태
        self.measurement_session = None
        self.current_frames = []
        self.quality_history = []
        
        logger.info("향상된 RPPG 분석 엔진 초기화 완료")
    
    def start_measurement_session(self, protocol_name: str = "standard_health_check") -> Dict[str, Any]:
        """
        측정 세션 시작
        
        Args:
            protocol_name: 사용할 측정 프로토콜
            
        Returns:
            세션 시작 결과
        """
        try:
            # 프로토콜 시작
            protocol_result = self.protocol_manager.start_protocol(protocol_name)
            
            # 측정 세션 초기화
            self.measurement_session = {
                "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "protocol_name": protocol_name,
                "start_time": datetime.now().isoformat(),
                "frames": [],
                "quality_metrics": [],
                "errors": []
            }
            
            logger.info(f"측정 세션 시작: {self.measurement_session['session_id']}")
            
            return {
                "status": "success",
                "session_id": self.measurement_session["session_id"],
                "protocol_info": protocol_result,
                "message": "측정 세션이 시작되었습니다."
            }
            
        except Exception as e:
            logger.error(f"측정 세션 시작 실패: {str(e)}")
            error_response = self.error_handler.handle_error(e, {"action": "start_session"})
            return {
                "status": "error",
                "error": error_response,
                "message": "측정 세션 시작에 실패했습니다."
            }
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        프레임 처리 및 품질 검증
        
        Args:
            frame: 입력 프레임
            
        Returns:
            프레임 처리 결과
        """
        try:
            if self.measurement_session is None:
                raise RuntimeError("측정 세션이 시작되지 않았습니다")
            
            # 프레임 품질 검증
            face_validation = self.quality_validator.validate_face_detection(frame)
            environment_validation = self.quality_validator.validate_measurement_environment(frame)
            
            # 품질 점수 계산
            quality_score = (face_validation.get('confidence', 0) + 
                           environment_validation.get('confidence', 0)) / 2
            
            # 품질 이력 기록
            self.quality_history.append({
                "timestamp": datetime.now().isoformat(),
                "quality_score": quality_score,
                "face_validation": face_validation,
                "environment_validation": environment_validation
            })
            
            # 프레임 저장
            self.current_frames.append(frame)
            
            # 품질 기준 확인
            current_step_info = self.protocol_manager.get_current_step_info()
            if current_step_info:
                quality_threshold = current_step_info.get("quality_threshold", 0.8)
                
                if quality_score >= quality_threshold:
                    # 품질 기준 통과
                    return {
                        "status": "success",
                        "quality_score": quality_score,
                        "face_validation": face_validation,
                        "environment_validation": environment_validation,
                        "message": "프레임 품질이 양호합니다.",
                        "can_proceed": True
                    }
                else:
                    # 품질 기준 미달
                    return {
                        "status": "warning",
                        "quality_score": quality_score,
                        "face_validation": face_validation,
                        "environment_validation": environment_validation,
                        "message": "프레임 품질이 기준에 미달합니다.",
                        "can_proceed": False,
                        "recommendations": face_validation.get('recommendation', '') + 
                                         " " + environment_validation.get('recommendation', '')
                    }
            else:
                return {
                    "status": "error",
                    "message": "프로토콜 정보를 가져올 수 없습니다.",
                    "can_proceed": False
                }
                
        except Exception as e:
            logger.error(f"프레임 처리 실패: {str(e)}")
            error_response = self.error_handler.handle_error(e, {"action": "process_frame"})
            return {
                "status": "error",
                "error": error_response,
                "message": "프레임 처리에 실패했습니다.",
                "can_proceed": False
            }
    
    def analyze_measurement_data(self) -> Dict[str, Any]:
        """
        측정 데이터 분석
        
        Returns:
            분석 결과
        """
        try:
            if not self.current_frames:
                raise ValueError("분석할 프레임이 없습니다")
            
            # 기존 RPPG 분석 수행
            rppg_result = self._perform_rppg_analysis(self.current_frames)
            
            # 신호 품질 검증
            if 'heart_rate_signal' in rppg_result:
                signal_validation = self.quality_validator.validate_signal_quality(
                    rppg_result['heart_rate_signal'], 
                    self.fps
                )
            else:
                signal_validation = {"valid": False, "confidence": 0.0}
            
            # 종합 품질 보고서 생성
            validation_results = [
                self.quality_history[-1]["face_validation"] if self.quality_history else {},
                self.quality_history[-1]["environment_validation"] if self.quality_history else {},
                signal_validation
            ]
            
            quality_report = self.quality_validator.generate_quality_report(validation_results)
            
            # 측정 결과 생성
            measurement_result = {
                "session_id": self.measurement_session["session_id"],
                "timestamp": datetime.now().isoformat(),
                "rppg_analysis": rppg_result,
                "quality_report": quality_report,
                "protocol_status": self.protocol_manager.get_protocol_status(),
                "recommendations": self._generate_recommendations(quality_report, rppg_result)
            }
            
            return {
                "status": "success",
                "result": measurement_result,
                "message": "측정 분석이 완료되었습니다."
            }
            
        except Exception as e:
            logger.error(f"측정 데이터 분석 실패: {str(e)}")
            error_response = self.error_handler.handle_error(e, {"action": "analyze_data"})
            return {
                "status": "error",
                "error": error_response,
                "message": "측정 데이터 분석에 실패했습니다."
            }
    
    def _perform_rppg_analysis(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """기존 RPPG 분석 수행"""
        try:
            # 얼굴 감지
            faces = self._detect_faces(frames[0])
            if not faces:
                return {"error": "얼굴이 감지되지 않았습니다"}
            
            # ROI 추출
            roi_data = self._extract_roi_data(frames, faces[0])
            
            # 신호 처리
            heart_rate_signal = self._process_heart_rate_signal(roi_data)
            
            # 주파수 분석
            heart_rate, hrv = self._analyze_frequency_domain(heart_rate_signal)
            
            # 스트레스 레벨 계산
            stress_level = self._calculate_stress_level(hrv, heart_rate)
            
            return {
                "heart_rate": heart_rate,
                "hrv": hrv,
                "stress_level": stress_level,
                "heart_rate_signal": heart_rate_signal,
                "confidence": self._calculate_confidence(heart_rate_signal),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RPPG 분석 실패: {str(e)}")
            raise
    
    def _detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """얼굴 감지"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=self.min_face_size
        )
        return faces
    
    def _extract_roi_data(self, frames: List[np.ndarray], face_bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """관심 영역 데이터 추출"""
        x, y, w, h = face_bbox
        roi_data = []
        
        for frame in frames:
            # ROI 추출 (얼굴 영역 + 패딩)
            roi = frame[max(0, y-self.roi_padding):min(frame.shape[0], y+h+self.roi_padding),
                       max(0, x-self.roi_padding):min(frame.shape[1], x+w+self.roi_padding)]
            
            if roi.size > 0:
                # 그린 채널 평균값 (rPPG에 가장 적합)
                roi_green = np.mean(roi[:, :, 1])
                roi_data.append(roi_green)
        
        return np.array(roi_data)
    
    def _process_heart_rate_signal(self, roi_data: np.ndarray) -> np.ndarray:
        """심박수 신호 처리"""
        if len(roi_data) < 2:
            return roi_data
        
        # 노이즈 제거 (이동 평균)
        window_size = min(5, len(roi_data) // 4)
        if window_size > 1:
            smoothed = np.convolve(roi_data, np.ones(window_size)/window_size, mode='valid')
        else:
            smoothed = roi_data
        
        # 트렌드 제거
        detrended = signal.detrend(smoothed)
        
        return detrended
    
    def _analyze_frequency_domain(self, signal_data: np.ndarray) -> Tuple[float, float]:
        """주파수 도메인 분석"""
        if len(signal_data) < 10:
            return 0.0, 0.0
        
        # FFT 수행
        fft_result = fft(signal_data)
        freqs = fftfreq(len(signal_data), 1/self.fps)
        
        # 양의 주파수만 고려
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_result[:len(fft_result)//2])
        
        # 심박수 범위 내에서 최대 주파수 찾기
        hr_mask = (positive_freqs >= self.min_freq) & (positive_freqs <= self.max_freq)
        if np.any(hr_mask):
            dominant_freq_idx = np.argmax(positive_fft[hr_mask])
            dominant_freq = positive_freqs[hr_mask][dominant_freq_idx]
            heart_rate = dominant_freq * 60  # BPM
        else:
            heart_rate = 0.0
        
        # HRV 계산 (간단한 표준편차 기반)
        hrv = np.std(signal_data) if len(signal_data) > 1 else 0.0
        
        return heart_rate, hrv
    
    def _calculate_stress_level(self, hrv: float, heart_rate: float) -> str:
        """스트레스 레벨 계산"""
        if heart_rate == 0:
            return "unknown"
        
        # 간단한 스트레스 지표 (실제로는 더 복잡한 알고리즘 필요)
        stress_score = 0
        
        if heart_rate > 100:
            stress_score += 2
        elif heart_rate > 80:
            stress_score += 1
        
        if hrv < 20:
            stress_score += 2
        elif hrv < 40:
            stress_score += 1
        
        if stress_score >= 3:
            return "high"
        elif stress_score >= 1:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, signal_data: np.ndarray) -> float:
        """신호 신뢰도 계산"""
        if len(signal_data) < 10:
            return 0.0
        
        # 신호 대비 노이즈 비율
        signal_power = np.var(signal_data)
        noise_power = np.var(np.diff(signal_data))
        
        if noise_power == 0:
            return 1.0
        
        snr = signal_power / noise_power
        confidence = min(1.0, snr / 10.0)  # SNR 10 이상을 최고 신뢰도로 설정
        
        return confidence
    
    def _generate_recommendations(self, quality_report: Dict, rppg_result: Dict) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 품질 기반 권장사항
        if quality_report.get('overall_quality') == 'poor':
            recommendations.append("측정 품질이 낮습니다. 조명과 자세를 조정하여 재측정을 권장합니다.")
        
        # 결과 기반 권장사항
        if 'heart_rate' in rppg_result:
            hr = rppg_result['heart_rate']
            if hr > 100:
                recommendations.append("심박수가 높습니다. 안정 상태에서 재측정을 권장합니다.")
            elif hr < 50:
                recommendations.append("심박수가 낮습니다. 정상적인 상태에서 재측정을 권장합니다.")
        
        if 'stress_level' in rppg_result:
            stress = rppg_result['stress_level']
            if stress == 'high':
                recommendations.append("스트레스 수준이 높습니다. 휴식을 취한 후 재측정을 권장합니다.")
        
        if not recommendations:
            recommendations.append("측정 결과가 양호합니다. 정기적인 측정을 권장합니다.")
        
        return recommendations
    
    def complete_measurement(self) -> Dict[str, Any]:
        """측정 완료"""
        try:
            if self.measurement_session is None:
                raise RuntimeError("완료할 측정 세션이 없습니다")
            
            # 최종 분석 수행
            analysis_result = self.analyze_measurement_data()
            
            if analysis_result["status"] == "success":
                # 프로토콜 단계 진행
                final_quality = analysis_result["result"]["quality_report"].get("confidence", 0.0)
                protocol_result = self.protocol_manager.advance_step(final_quality)
                
                # 측정 세션 완료
                self.measurement_session["end_time"] = datetime.now().isoformat()
                self.measurement_session["final_result"] = analysis_result["result"]
                self.measurement_session["protocol_result"] = protocol_result
                
                return {
                    "status": "success",
                    "session_summary": {
                        "session_id": self.measurement_session["session_id"],
                        "duration": (datetime.fromisoformat(self.measurement_session["end_time"]) - 
                                   datetime.fromisoformat(self.measurement_session["start_time"])).total_seconds(),
                        "final_quality": final_quality,
                        "protocol_status": protocol_result.get("status", "unknown")
                    },
                    "result": analysis_result["result"],
                    "message": "측정이 성공적으로 완료되었습니다."
                }
            else:
                return analysis_result
                
        except Exception as e:
            logger.error(f"측정 완료 실패: {str(e)}")
            error_response = self.error_handler.handle_error(e, {"action": "complete_measurement"})
            return {
                "status": "error",
                "error": error_response,
                "message": "측정 완료에 실패했습니다."
            }
    
    def get_measurement_status(self) -> Dict[str, Any]:
        """측정 상태 조회"""
        if self.measurement_session is None:
            return {"status": "no_session", "message": "진행 중인 측정이 없습니다"}
        
        protocol_status = self.protocol_manager.get_protocol_status()
        current_step = self.protocol_manager.get_current_step_info()
        
        return {
            "session_id": self.measurement_session["session_id"],
            "protocol_status": protocol_status,
            "current_step": current_step,
            "quality_history": self.quality_history[-10:] if self.quality_history else [],  # 최근 10개
            "frame_count": len(self.current_frames),
            "session_duration": (datetime.now() - 
                               datetime.fromisoformat(self.measurement_session["start_time"])).total_seconds()
        }
    
    def reset_measurement(self):
        """측정 초기화"""
        self.measurement_session = None
        self.current_frames = []
        self.quality_history = []
        self.protocol_manager.reset_protocol()
        
        logger.info("측정이 초기화되었습니다")
    
    def export_measurement_report(self, filepath: str = None) -> str:
        """측정 보고서 내보내기"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"measurement_report_{timestamp}.json"
        
        try:
            report = {
                "measurement_session": self.measurement_session,
                "quality_history": self.quality_history,
                "protocol_report": self.protocol_manager.export_protocol_report(),
                "error_statistics": self.error_handler.get_error_statistics(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"측정 보고서가 {filepath}에 저장되었습니다")
            return filepath
            
        except Exception as e:
            logger.error(f"측정 보고서 내보내기 실패: {str(e)}")
            raise
