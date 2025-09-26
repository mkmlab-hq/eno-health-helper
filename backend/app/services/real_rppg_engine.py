#!/usr/bin/env python3
"""
실제 rPPG 엔진 - MediaPipe 기반 고품질 심박수 추출
face_rppg_demo.py의 실제 알고리즘을 기반으로 완전 구현
"""

import cv2
import numpy as np
import mediapipe as mp
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from scipy import signal
from scipy.fft import fft, fftfreq
import json

logger = logging.getLogger(__name__)

class RealRPPGEngine:
    """실제 rPPG 엔진 - MediaPipe 기반 고품질 구현"""
    
    def __init__(self):
        # MediaPipe 얼굴 메시 초기화
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            static_image_mode=False, 
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # rPPG 파라미터
        self.sample_rate = 30.0  # 30 FPS
        self.min_duration = 10.0  # 최소 10초
        self.max_duration = 60.0  # 최대 60초
        
        # 심박수 범위 (BPM)
        self.min_bpm = 40
        self.max_bpm = 200
        
        # 신호 처리 파라미터
        self.lowcut = 0.7  # 0.7 Hz (42 BPM)
        self.highcut = 4.0  # 4.0 Hz (240 BPM)
        
        # 얼굴 영역 정의 (MediaPipe 랜드마크 인덱스)
        self.forehead_landmarks = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323]
        self.cheek_landmarks = [116, 117, 118, 119, 120, 121, 126, 142, 143, 144, 145, 146, 147]
        self.nose_landmarks = [1, 2, 5, 4, 6, 19, 20, 94, 125, 141, 235, 236, 3, 51, 48, 115, 131, 134, 102, 49, 220, 305, 281, 360, 279]
        
        logger.info("✅ 실제 rPPG 엔진 초기화 완료 (MediaPipe 기반)")
    
    def analyze_video_frames(self, video_frames: List[np.ndarray], duration: float) -> Dict[str, Any]:
        """
        비디오 프레임에서 실제 rPPG 분석 수행
        
        Args:
            video_frames: 비디오 프레임 리스트
            duration: 비디오 길이 (초)
            
        Returns:
            rPPG 분석 결과
        """
        try:
            logger.info(f"실제 rPPG 분석 시작: {len(video_frames)} 프레임, {duration}초")
            
            if len(video_frames) < 30:  # 최소 1초 (30fps 기준)
                raise ValueError(f"프레임 수가 부족합니다: {len(video_frames)} < 30")
            
            # 1단계: 얼굴 영역에서 RGB 신호 추출
            rgb_signals = self._extract_rgb_signals(video_frames)
            
            # 2단계: 신호 전처리 및 필터링
            processed_signals = self._preprocess_signals(rgb_signals, duration)
            
            # 3단계: 심박수 추출
            heart_rate_result = self._extract_heart_rate(processed_signals, duration)
            
            # 4단계: 심박변이도(HRV) 계산
            hrv_result = self._calculate_hrv(processed_signals, duration)
            
            # 5단계: 스트레스 수준 평가
            stress_result = self._assess_stress_level(heart_rate_result, hrv_result)
            
            # 6단계: 신호 품질 평가
            quality_result = self._assess_signal_quality(processed_signals, heart_rate_result)
            
            # 7단계: 결과 통합
            final_result = self._integrate_results(
                heart_rate_result, hrv_result, stress_result, quality_result, duration
            )
            
            logger.info(f"실제 rPPG 분석 완료: HR={final_result['heart_rate']:.1f} BPM, 품질={final_result['signal_quality']}")
            return final_result
            
        except Exception as e:
            logger.error(f"실제 rPPG 분석 실패: {e}")
            return self._get_error_result(str(e))
    
    def _extract_rgb_signals(self, video_frames: List[np.ndarray]) -> Dict[str, List[float]]:
        """비디오 프레임에서 RGB 신호 추출"""
        try:
            rgb_signals = {'red': [], 'green': [], 'blue': []}
            valid_frames = 0
            
            for frame in video_frames:
                # BGR to RGB 변환
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 얼굴 랜드마크 검출
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    h, w, _ = frame.shape
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # 이마 영역 마스크 생성
                    mask = self._create_face_mask(landmarks, h, w, self.forehead_landmarks)
                    
                    # RGB 채널별 평균값 추출
                    mean_rgb = cv2.mean(rgb_frame, mask=mask)
                    
                    rgb_signals['red'].append(mean_rgb[0])
                    rgb_signals['green'].append(mean_rgb[1])
                    rgb_signals['blue'].append(mean_rgb[2])
                    valid_frames += 1
                else:
                    # 얼굴이 검출되지 않은 경우 이전 값 유지
                    if rgb_signals['red']:
                        rgb_signals['red'].append(rgb_signals['red'][-1])
                        rgb_signals['green'].append(rgb_signals['green'][-1])
                        rgb_signals['blue'].append(rgb_signals['blue'][-1])
            
            logger.info(f"RGB 신호 추출 완료: {valid_frames}/{len(video_frames)} 프레임")
            return rgb_signals
            
        except Exception as e:
            logger.error(f"RGB 신호 추출 실패: {e}")
            raise
    
    def _create_face_mask(self, landmarks, height: int, width: int, landmark_indices: List[int]) -> np.ndarray:
        """얼굴 랜드마크를 기반으로 마스크 생성"""
        try:
            mask = np.zeros((height, width), dtype=np.uint8)
            
            # 랜드마크 좌표 추출
            points = []
            for idx in landmark_indices:
                if idx < len(landmarks.landmark):
                    lm = landmarks.landmark[idx]
                    x = int(lm.x * width)
                    y = int(lm.y * height)
                    points.append([x, y])
            
            if len(points) >= 3:
                # 다각형 마스크 생성
                pts = np.array(points, dtype=np.int32)
                cv2.fillPoly(mask, [pts], 255)
            
            return mask
            
        except Exception as e:
            logger.warning(f"얼굴 마스크 생성 실패: {e}")
            return np.zeros((height, width), dtype=np.uint8)
    
    def _preprocess_signals(self, rgb_signals: Dict[str, List[float]], duration: float) -> Dict[str, np.ndarray]:
        """RGB 신호 전처리 및 필터링"""
        try:
            processed_signals = {}
            
            for channel, signal_data in rgb_signals.items():
                if len(signal_data) < 10:
                    continue
                
                # numpy 배열로 변환
                signal_array = np.array(signal_data, dtype=np.float32)
                
                # 1. 이동평균 필터 (노이즈 제거)
                window_size = min(5, len(signal_array) // 10)
                if window_size > 1:
                    signal_array = self._moving_average(signal_array, window_size)
                
                # 2. 정규화 (Z-score)
                signal_array = (signal_array - np.mean(signal_array)) / (np.std(signal_array) + 1e-8)
                
                # 3. 대역통과 필터 (심박수 범위)
                nyquist = self.sample_rate / 2
                low = self.lowcut / nyquist
                high = self.highcut / nyquist
                
                if high < 1.0:  # 유효한 주파수 범위인지 확인
                    b, a = signal.butter(4, [low, high], btype='band')
                    signal_array = signal.filtfilt(b, a, signal_array)
                
                # 4. 이상치 제거 (IQR 방법)
                signal_array = self._remove_outliers(signal_array)
                
                processed_signals[channel] = signal_array
            
            return processed_signals
            
        except Exception as e:
            logger.error(f"신호 전처리 실패: {e}")
            raise
    
    def _moving_average(self, signal: np.ndarray, window_size: int) -> np.ndarray:
        """이동평균 필터"""
        try:
            if window_size <= 1:
                return signal
            
            # 패딩 추가
            padded = np.pad(signal, (window_size//2, window_size//2), mode='edge')
            
            # 이동평균 계산
            smoothed = np.convolve(padded, np.ones(window_size)/window_size, mode='valid')
            
            return smoothed
            
        except Exception as e:
            logger.warning(f"이동평균 필터 실패: {e}")
            return signal
    
    def _remove_outliers(self, signal: np.ndarray) -> np.ndarray:
        """IQR 방법으로 이상치 제거"""
        try:
            if len(signal) < 10:
                return signal
            
            q25 = np.percentile(signal, 25)
            q75 = np.percentile(signal, 75)
            iqr = q75 - q25
            
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            
            # 이상치를 경계값으로 클리핑
            signal_clipped = np.clip(signal, lower_bound, upper_bound)
            
            return signal_clipped
            
        except Exception as e:
            logger.warning(f"이상치 제거 실패: {e}")
            return signal
    
    def _extract_heart_rate(self, processed_signals: Dict[str, np.ndarray], duration: float) -> Dict[str, Any]:
        """심박수 추출"""
        try:
            if 'green' not in processed_signals:
                raise ValueError("녹색 채널 신호가 없습니다")
            
            green_signal = processed_signals['green']
            
            if len(green_signal) < 30:
                raise ValueError("신호 길이가 부족합니다")
            
            # FFT를 사용한 주파수 분석
            fft_result = fft(green_signal)
            freqs = fftfreq(len(green_signal), 1/self.sample_rate)
            
            # 양의 주파수만 사용
            positive_freqs = freqs[freqs > 0]
            positive_fft = fft_result[freqs > 0]
            power_spectrum = np.abs(positive_fft) ** 2
            
            # 심박수 범위 필터링 (0.67-3.33 Hz = 40-200 BPM)
            bpm_freq_range = (positive_freqs >= self.min_bpm/60) & (positive_freqs <= self.max_bpm/60)
            
            if not np.any(bpm_freq_range):
                raise ValueError("유효한 심박수 범위가 없습니다")
            
            # 최대 파워 주파수 찾기
            valid_freqs = positive_freqs[bpm_freq_range]
            valid_power = power_spectrum[bpm_freq_range]
            
            peak_idx = np.argmax(valid_power)
            peak_freq = valid_freqs[peak_idx]
            heart_rate = peak_freq * 60  # Hz to BPM
            
            # 신뢰도 계산 (피크의 상대적 강도)
            max_power = np.max(valid_power)
            mean_power = np.mean(valid_power)
            confidence = min(1.0, max_power / (mean_power + 1e-8))
            
            # 심박수 범위 검증
            if not (self.min_bpm <= heart_rate <= self.max_bpm):
                logger.warning(f"심박수가 범위를 벗어남: {heart_rate:.1f} BPM")
                heart_rate = np.clip(heart_rate, self.min_bpm, self.max_bpm)
                confidence *= 0.5  # 신뢰도 감소
            
            return {
                'heart_rate': float(heart_rate),
                'confidence': float(confidence),
                'peak_frequency': float(peak_freq),
                'power_spectrum': valid_power.tolist(),
                'frequency_range': valid_freqs.tolist()
            }
            
        except Exception as e:
            logger.error(f"심박수 추출 실패: {e}")
            raise
    
    def _calculate_hrv(self, processed_signals: Dict[str, np.ndarray], duration: float) -> Dict[str, Any]:
        """심박변이도(HRV) 계산"""
        try:
            if 'green' not in processed_signals:
                return {'hrv': 0.0, 'confidence': 0.0}
            
            green_signal = processed_signals['green']
            
            # 피크 검출을 통한 RR 간격 계산
            peaks = self._detect_peaks(green_signal)
            
            if len(peaks) < 3:
                return {'hrv': 0.0, 'confidence': 0.0}
            
            # RR 간격 계산 (샘플 단위)
            rr_intervals = np.diff(peaks) / self.sample_rate  # 초 단위로 변환
            
            # RMSSD 계산 (Root Mean Square of Successive Differences)
            if len(rr_intervals) > 1:
                successive_diffs = np.diff(rr_intervals)
                rmssd = np.sqrt(np.mean(successive_diffs ** 2)) * 1000  # ms 단위
            else:
                rmssd = 0.0
            
            # SDNN 계산 (Standard Deviation of NN intervals)
            sdnn = np.std(rr_intervals) * 1000  # ms 단위
            
            # HRV 점수 정규화 (0-100)
            hrv_score = min(100, max(0, (rmssd - 10) / 50 * 100))
            
            return {
                'hrv': float(rmssd),
                'sdnn': float(sdnn),
                'hrv_score': float(hrv_score),
                'rr_intervals': rr_intervals.tolist(),
                'confidence': min(1.0, len(peaks) / (duration * 2))  # 초당 2회 피크 기준
            }
            
        except Exception as e:
            logger.warning(f"HRV 계산 실패: {e}")
            return {'hrv': 0.0, 'confidence': 0.0}
    
    def _detect_peaks(self, signal: np.ndarray) -> np.ndarray:
        """신호에서 피크 검출"""
        try:
            # 간단한 피크 검출 알고리즘
            peaks = []
            min_distance = int(self.sample_rate * 0.4)  # 최소 0.4초 간격
            
            for i in range(min_distance, len(signal) - min_distance):
                if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                    # 주변 최대값인지 확인
                    is_peak = True
                    for j in range(max(0, i-min_distance), min(len(signal), i+min_distance)):
                        if j != i and signal[j] >= signal[i]:
                            is_peak = False
                            break
                    
                    if is_peak:
                        peaks.append(i)
            
            return np.array(peaks)
            
        except Exception as e:
            logger.warning(f"피크 검출 실패: {e}")
            return np.array([])
    
    def _assess_stress_level(self, heart_rate_result: Dict, hrv_result: Dict) -> Dict[str, Any]:
        """스트레스 수준 평가"""
        try:
            hr = heart_rate_result['heart_rate']
            hrv = hrv_result['hrv']
            
            stress_score = 0.0
            stress_level = "보통"
            
            # 심박수 기반 스트레스 평가
            if hr > 100:
                stress_score += 0.4
            elif hr > 85:
                stress_score += 0.2
            elif hr < 60:
                stress_score += 0.1
            
            # HRV 기반 스트레스 평가
            if hrv < 20:
                stress_score += 0.4
            elif hrv < 30:
                stress_score += 0.2
            elif hrv > 50:
                stress_score -= 0.1
            
            # 스트레스 수준 분류
            if stress_score >= 0.6:
                stress_level = "높음"
            elif stress_score >= 0.3:
                stress_level = "보통"
            else:
                stress_level = "낮음"
            
            return {
                'stress_level': stress_level,
                'stress_score': float(stress_score),
                'heart_rate_factor': float(hr),
                'hrv_factor': float(hrv)
            }
            
        except Exception as e:
            logger.warning(f"스트레스 평가 실패: {e}")
            return {'stress_level': "알 수 없음", 'stress_score': 0.5}
    
    def _assess_signal_quality(self, processed_signals: Dict[str, np.ndarray], heart_rate_result: Dict) -> Dict[str, Any]:
        """신호 품질 평가"""
        try:
            if 'green' not in processed_signals:
                return {'signal_quality': "Poor", 'quality_score': 0.0}
            
            green_signal = processed_signals['green']
            
            # 1. 신호 대 노이즈 비율 (SNR)
            signal_power = np.mean(green_signal ** 2)
            noise_estimate = np.var(green_signal)
            snr = 10 * np.log10(signal_power / (noise_estimate + 1e-8))
            
            # 2. 신호 안정성 (변동계수)
            cv = np.std(green_signal) / (np.mean(np.abs(green_signal)) + 1e-8)
            
            # 3. 심박수 신뢰도
            hr_confidence = heart_rate_result.get('confidence', 0.0)
            
            # 종합 품질 점수 계산
            quality_score = 0.0
            
            # SNR 점수 (0-40%)
            if snr > 20:
                quality_score += 0.4
            elif snr > 15:
                quality_score += 0.3
            elif snr > 10:
                quality_score += 0.2
            else:
                quality_score += 0.1
            
            # 안정성 점수 (0-30%)
            if cv < 0.1:
                quality_score += 0.3
            elif cv < 0.2:
                quality_score += 0.2
            elif cv < 0.3:
                quality_score += 0.1
            
            # 신뢰도 점수 (0-30%)
            quality_score += hr_confidence * 0.3
            
            # 품질 등급 분류
            if quality_score >= 0.8:
                quality_grade = "Excellent"
            elif quality_score >= 0.6:
                quality_grade = "Good"
            elif quality_score >= 0.4:
                quality_grade = "Fair"
            else:
                quality_grade = "Poor"
            
            return {
                'signal_quality': quality_grade,
                'quality_score': float(quality_score),
                'snr_db': float(snr),
                'coefficient_of_variation': float(cv),
                'hr_confidence': float(hr_confidence)
            }
            
        except Exception as e:
            logger.warning(f"신호 품질 평가 실패: {e}")
            return {'signal_quality': "Unknown", 'quality_score': 0.0}
    
    def _integrate_results(self, heart_rate_result: Dict, hrv_result: Dict, 
                          stress_result: Dict, quality_result: Dict, duration: float) -> Dict[str, Any]:
        """모든 결과를 통합하여 최종 결과 생성"""
        try:
            # 기본 결과 구성
            result = {
                'analysis_id': f"real_rppg_{int(datetime.now().timestamp())}",
                'timestamp': datetime.now().isoformat(),
                'analysis_method': 'real_rppg_mediapipe_v1',
                'duration': duration,
                'status': 'success'
            }
            
            # 심박수 결과
            result.update({
                'heart_rate': heart_rate_result['heart_rate'],
                'hr_confidence': heart_rate_result['confidence'],
                'peak_frequency': heart_rate_result['peak_frequency']
            })
            
            # HRV 결과
            result.update({
                'hrv': hrv_result['hrv'],
                'sdnn': hrv_result['sdnn'],
                'hrv_score': hrv_result['hrv_score'],
                'hrv_confidence': hrv_result['confidence']
            })
            
            # 스트레스 결과
            result.update({
                'stress_level': stress_result['stress_level'],
                'stress_score': stress_result['stress_score']
            })
            
            # 품질 결과
            result.update({
                'signal_quality': quality_result['signal_quality'],
                'quality_score': quality_result['quality_score'],
                'snr_db': quality_result.get('snr_db', 0.0)
            })
            
            # 종합 건강 점수 계산
            health_score = self._calculate_overall_health_score(result)
            result['overall_health_score'] = health_score
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(result)
            result['recommendations'] = recommendations
            
            return result
            
        except Exception as e:
            logger.error(f"결과 통합 실패: {e}")
            return self._get_error_result(str(e))
    
    def _calculate_overall_health_score(self, result: Dict) -> float:
        """종합 건강 점수 계산"""
        try:
            score = 0.0
            
            # 심박수 점수 (0-40%)
            hr = result['heart_rate']
            if 60 <= hr <= 100:
                score += 0.4
            elif 50 <= hr <= 110:
                score += 0.3
            elif 40 <= hr <= 120:
                score += 0.2
            else:
                score += 0.1
            
            # HRV 점수 (0-30%)
            hrv_score = result.get('hrv_score', 0)
            score += (hrv_score / 100) * 0.3
            
            # 스트레스 점수 (0-20%)
            stress_score = result.get('stress_score', 0.5)
            score += (1 - stress_score) * 0.2
            
            # 품질 점수 (0-10%)
            quality_score = result.get('quality_score', 0.0)
            score += quality_score * 0.1
            
            return min(100.0, max(0.0, score * 100))
            
        except Exception as e:
            logger.warning(f"건강 점수 계산 실패: {e}")
            return 50.0
    
    def _generate_recommendations(self, result: Dict) -> List[str]:
        """건강 권장사항 생성"""
        recommendations = []
        
        try:
            hr = result['heart_rate']
            stress_level = result['stress_level']
            quality = result['signal_quality']
            
            # 심박수 기반 권장사항
            if hr > 100:
                recommendations.append("심박수가 높습니다. 스트레스를 줄이고 휴식을 취하세요.")
            elif hr < 60:
                recommendations.append("심박수가 낮습니다. 적절한 운동을 권장합니다.")
            
            # 스트레스 기반 권장사항
            if stress_level == "높음":
                recommendations.append("스트레스 수준이 높습니다. 명상이나 호흡 운동을 시도해보세요.")
            
            # 품질 기반 권장사항
            if quality == "Poor":
                recommendations.append("측정 품질이 낮습니다. 조명을 개선하고 얼굴을 정면으로 향하세요.")
            
            # 기본 권장사항
            if not recommendations:
                recommendations.append("전반적으로 건강한 상태입니다. 현재 생활습관을 유지하세요.")
            
            return recommendations
            
        except Exception as e:
            logger.warning(f"권장사항 생성 실패: {e}")
            return ["건강한 생활습관을 유지하세요."]
    
    def _get_error_result(self, error_message: str) -> Dict[str, Any]:
        """오류 결과 반환"""
        return {
            'analysis_id': f"real_rppg_error_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'analysis_method': 'real_rppg_mediapipe_v1',
            'status': 'error',
            'error_message': error_message,
            'heart_rate': 72.0,
            'hrv': 0.0,
            'stress_level': "알 수 없음",
            'signal_quality': "Unknown",
            'overall_health_score': 0.0,
            'recommendations': ["측정 중 오류가 발생했습니다. 다시 시도해주세요."]
        }

# 전역 엔진 인스턴스
real_rppg_engine = RealRPPGEngine()

# 사용 예시
if __name__ == "__main__":
    # 테스트용 더미 프레임 생성
    test_frames = []
    for i in range(300):  # 10초 (30fps)
        # 더미 프레임 생성 (실제로는 웹캠에서 가져옴)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_frames.append(frame)
    
    # rPPG 분석 실행
    result = real_rppg_engine.analyze_video_frames(test_frames, 10.0)
    print("실제 rPPG 분석 결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))











