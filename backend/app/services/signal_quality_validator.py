import cv2
import numpy as np
from scipy import signal
from scipy.stats import pearsonr
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SignalQualityValidator:
    """
    생체신호 측정 품질 검증 시스템
    
    측정 품질을 실시간으로 모니터링하고 검증하여
    신뢰할 수 있는 결과만을 제공합니다.
    """
    
    def __init__(self):
        # 품질 기준 설정
        self.min_face_size = (80, 80)  # 최소 얼굴 크기
        self.min_measurement_duration = 10.0  # 최소 측정 시간 (초)
        self.min_signal_strength = 0.3  # 최소 신호 강도
        self.max_motion_threshold = 0.15  # 최대 움직임 허용치
        self.min_confidence = 0.7  # 최소 신뢰도
        
        logger.info("신호 품질 검증 시스템 초기화 완료")
    
    def validate_face_detection(self, frame: np.ndarray) -> Dict[str, any]:
        """
        얼굴 감지 품질 검증
        
        Args:
            frame: 입력 프레임
            
        Returns:
            검증 결과 딕셔너리
        """
        try:
            # OpenCV 얼굴 감지
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 대비 향상을 위한 CLAHE 적용
            try:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                gray_proc = clahe.apply(gray)
            except Exception:
                gray_proc = gray
            
            # 동적 최소 얼굴 크기
            h_img, w_img = gray_proc.shape[:2]
            dyn_min_size = (
                max(self.min_face_size[0], w_img // 10),
                max(self.min_face_size[1], h_img // 10)
            )
            faces = face_cascade.detectMultiScale(
                gray_proc, 
                scaleFactor=1.05, 
                minNeighbors=4, 
                minSize=dyn_min_size
            )
            
            if len(faces) == 0:
                return {
                    'valid': False,
                    'confidence': 0.0,
                    'error': '얼굴이 감지되지 않았습니다.',
                    'recommendation': '카메라를 얼굴에 맞춰주세요.'
                }
            
            if len(faces) > 1:
                return {
                    'valid': False,
                    'confidence': 0.3,
                    'error': '여러 얼굴이 감지되었습니다.',
                    'recommendation': '한 명의 얼굴만 화면에 보이도록 해주세요.'
                }
            
            # 얼굴 크기 및 위치 검증
            x, y, w, h = faces[0]
            face_area = w * h
            frame_area = frame.shape[0] * frame.shape[1]
            face_ratio = face_area / frame_area
            
            if face_ratio < 0.05:  # 얼굴이 너무 작음
                return {
                    'valid': False,
                    'confidence': 0.4,
                    'error': '얼굴이 너무 작습니다.',
                    'recommendation': '카메라에 더 가까이 다가가주세요.'
                }
            
            if face_ratio > 0.8:  # 얼굴이 너무 큼
                return {
                    'valid': False,
                    'confidence': 0.5,
                    'error': '얼굴이 너무 큽니다.',
                    'recommendation': '카메라에서 조금 멀어져주세요.'
                }
            
            # 얼굴 위치 검증 (화면 중앙에 있는지)
            center_x = frame.shape[1] // 2
            center_y = frame.shape[0] // 2
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            distance_from_center = np.sqrt(
                (face_center_x - center_x) ** 2 + 
                (face_center_y - center_y) ** 2
            )
            max_distance = min(frame.shape[0], frame.shape[1]) * 0.3
            
            if distance_from_center > max_distance:
                return {
                    'valid': False,
                    'confidence': 0.6,
                    'error': '얼굴이 화면 중앙에 있지 않습니다.',
                    'recommendation': '얼굴을 화면 중앙에 위치시켜주세요.'
                }
            
            # 품질 점수 계산
            size_score = min(face_ratio / 0.15, 1.0)  # 이상적인 얼굴 비율: 15%
            position_score = 1.0 - (distance_from_center / max_distance)
            confidence = (size_score + position_score) / 2
            
            return {
                'valid': True,
                'confidence': confidence,
                'face_bbox': faces[0],
                'face_ratio': face_ratio,
                'position_score': position_score,
                'recommendation': '측정 준비가 완료되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"얼굴 감지 검증 실패: {str(e)}")
            return {
                'valid': False,
                'confidence': 0.0,
                'error': f'얼굴 감지 검증 중 오류가 발생했습니다: {str(e)}',
                'recommendation': '페이지를 새로고침하고 다시 시도해주세요.'
            }
    
    def validate_signal_quality(self, signal_data: np.ndarray, fps: float) -> Dict[str, any]:
        """
        신호 품질 검증
        
        Args:
            signal_data: 신호 데이터 (1D 배열)
            fps: 프레임 레이트
            
        Returns:
            신호 품질 검증 결과
        """
        try:
            if len(signal_data) < fps * self.min_measurement_duration:
                return {
                    'valid': False,
                    'confidence': 0.0,
                    'error': f'측정 시간이 너무 짧습니다. 최소 {self.min_measurement_duration}초 필요.',
                    'recommendation': '더 오래 측정해주세요.'
                }
            
            # 신호 강도 검증
            signal_mean = np.mean(signal_data)
            signal_std = np.std(signal_data)
            signal_strength = signal_std / (signal_mean + 1e-8)
            
            if signal_strength < self.min_signal_strength:
                return {
                    'valid': False,
                    'confidence': 0.2,
                    'error': '신호가 너무 약합니다.',
                    'recommendation': '조명을 밝게 하고 정지 상태를 유지해주세요.'
                }
            
            # 움직임 검증 (신호 변화량)
            signal_diff = np.diff(signal_data)
            motion_level = np.std(signal_diff) / (signal_std + 1e-8)
            
            if motion_level > self.max_motion_threshold:
                return {
                    'valid': False,
                    'confidence': 0.3,
                    'error': '움직임이 너무 많습니다.',
                    'recommendation': '가능한 한 정지 상태를 유지해주세요.'
                }
            
            # 신호 일관성 검증 (연속성)
            signal_autocorr = np.correlate(signal_data, signal_data, mode='full')
            signal_autocorr = signal_autocorr[len(signal_data)-1:]
            consistency_score = np.max(signal_autocorr[1:]) / signal_autocorr[0]
            
            # 주파수 도메인 검증
            freqs, psd = signal.welch(signal_data, fps, nperseg=min(256, len(signal_data)//4))
            dominant_freq = freqs[np.argmax(psd)]
            
            # 심박수 범위 검증 (0.7Hz ~ 4.0Hz = 42 ~ 240 BPM)
            if not (0.7 <= dominant_freq <= 4.0):
                return {
                    'valid': False,
                    'confidence': 0.4,
                    'error': '심박수 범위를 벗어났습니다.',
                    'recommendation': '정상적인 상태에서 측정해주세요.'
                }
            
            # 종합 품질 점수 계산
            strength_score = min(signal_strength / 0.5, 1.0)
            motion_score = 1.0 - min(motion_level / 0.3, 1.0)
            consistency_score = min(consistency_score, 1.0)
            
            overall_confidence = (strength_score + motion_score + consistency_score) / 3
            
            if overall_confidence < self.min_confidence:
                return {
                    'valid': False,
                    'confidence': overall_confidence,
                    'error': '신호 품질이 기준에 미달합니다.',
                    'recommendation': '조명, 거리, 움직임을 조정하여 다시 측정해주세요.'
                }
            
            return {
                'valid': True,
                'confidence': overall_confidence,
                'signal_strength': signal_strength,
                'motion_level': motion_level,
                'consistency_score': consistency_score,
                'dominant_freq': dominant_freq,
                'estimated_bpm': dominant_freq * 60,
                'recommendation': '신호 품질이 양호합니다. 측정을 계속하세요.'
            }
            
        except Exception as e:
            logger.error(f"신호 품질 검증 실패: {str(e)}")
            return {
                'valid': False,
                'confidence': 0.0,
                'error': f'신호 품질 검증 중 오류가 발생했습니다: {str(e)}',
                'recommendation': '측정을 다시 시작해주세요.'
            }
    
    def validate_measurement_environment(self, frame: np.ndarray) -> Dict[str, any]:
        """
        측정 환경 품질 검증
        
        Args:
            frame: 입력 프레임
            
        Returns:
            환경 품질 검증 결과
        """
        try:
            # 조명 검증
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            if brightness < 50:
                return {
                    'valid': False,
                    'confidence': 0.2,
                    'error': '조명이 너무 어둡습니다.',
                    'recommendation': '더 밝은 곳에서 측정해주세요.'
                }
            
            if brightness > 200:
                return {
                    'valid': False,
                    'confidence': 0.3,
                    'error': '조명이 너무 밝습니다.',
                    'recommendation': '직사광선을 피하고 적당한 조명에서 측정해주세요.'
                }
            
            # 대비 검증
            contrast = np.std(gray)
            if contrast < 20:
                return {
                    'valid': False,
                    'confidence': 0.4,
                    'error': '대비가 너무 낮습니다.',
                    'recommendation': '배경과 구분되는 환경에서 측정해주세요.'
                }
            
            # 노이즈 검증 (가우시안 블러와 원본의 차이)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise_level = np.mean(np.abs(gray.astype(float) - blurred.astype(float)))
            
            if noise_level > 15:
                return {
                    'valid': False,
                    'confidence': 0.5,
                    'error': '노이즈가 너무 많습니다.',
                    'recommendation': '카메라를 고정하고 안정적인 환경에서 측정해주세요.'
                }
            
            # 환경 품질 점수 계산
            brightness_score = 1.0 - abs(brightness - 125) / 125
            contrast_score = min(contrast / 50, 1.0)
            noise_score = 1.0 - min(noise_level / 20, 1.0)
            
            environment_confidence = (brightness_score + contrast_score + noise_score) / 3
            
            return {
                'valid': True,
                'confidence': environment_confidence,
                'brightness': brightness,
                'contrast': contrast,
                'noise_level': noise_level,
                'recommendation': '측정 환경이 양호합니다.'
            }
            
        except Exception as e:
            logger.error(f"환경 품질 검증 실패: {str(e)}")
            return {
                'valid': False,
                'confidence': 0.0,
                'error': f'환경 품질 검증 중 오류가 발생했습니다: {str(e)}',
                'recommendation': '측정 환경을 점검하고 다시 시도해주세요.'
            }
    
    def get_measurement_protocol(self) -> Dict[str, any]:
        """
        표준화된 측정 프로토콜 제공
        
        Returns:
            측정 프로토콜 가이드
        """
        return {
            'preparation': {
                'duration': '5분',
                'activities': [
                    '측정 전 5분간 안정 상태 유지',
                    '카페인, 알코올 섭취 금지',
                    '과도한 운동 금지',
                    '정상적인 호흡 유지'
                ]
            },
            'measurement': {
                'duration': '30초',
                'position': '카메라에서 30-50cm 거리',
                'posture': '정면을 바라보며 정지 상태',
                'lighting': '적당한 조명, 직사광선 피하기',
                'background': '단순한 배경, 움직임 최소화'
            },
            'quality_checks': [
                '얼굴이 화면 중앙에 위치',
                '적절한 얼굴 크기 (화면의 10-20%)',
                '안정적인 조명',
                '최소 움직임',
                '명확한 얼굴 윤곽'
            ],
            'troubleshooting': {
                'poor_quality': '조명, 거리, 움직임 조정',
                'face_not_detected': '카메라 각도 및 거리 조정',
                'too_much_motion': '안정적인 자세 유지',
                'low_light': '더 밝은 환경에서 측정'
            }
        }
    
    def generate_quality_report(self, validation_results: List[Dict]) -> Dict[str, any]:
        """
        종합 품질 보고서 생성
        
        Args:
            validation_results: 각 검증 단계의 결과 리스트
            
        Returns:
            종합 품질 보고서
        """
        try:
            valid_count = sum(1 for result in validation_results if result.get('valid', False))
            total_count = len(validation_results)
            
            if total_count == 0:
                return {
                    'overall_quality': 'unknown',
                    'confidence': 0.0,
                    'recommendations': ['측정 데이터가 부족합니다.']
                }
            
            overall_confidence = sum(
                result.get('confidence', 0) for result in validation_results
            ) / total_count
            
            # 품질 등급 결정
            if overall_confidence >= 0.8:
                quality_grade = 'excellent'
            elif overall_confidence >= 0.6:
                quality_grade = 'good'
            elif overall_confidence >= 0.4:
                quality_grade = 'fair'
            else:
                quality_grade = 'poor'
            
            # 권장사항 수집
            recommendations = []
            for result in validation_results:
                if not result.get('valid', False):
                    rec = result.get('recommendation', '')
                    if rec and rec not in recommendations:
                        recommendations.append(rec)
            
            if not recommendations:
                recommendations = ['측정 품질이 양호합니다.']
            
            return {
                'overall_quality': quality_grade,
                'confidence': overall_confidence,
                'valid_checks': valid_count,
                'total_checks': total_count,
                'quality_breakdown': validation_results,
                'recommendations': recommendations,
                'timestamp': np.datetime64('now').isoformat()
            }
            
        except Exception as e:
            logger.error(f"품질 보고서 생성 실패: {str(e)}")
            return {
                'overall_quality': 'error',
                'confidence': 0.0,
                'error': str(e),
                'recommendations': ['품질 검증 중 오류가 발생했습니다.']
            }
