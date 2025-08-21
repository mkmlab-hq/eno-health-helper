import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import io
import wave
import tempfile
import os
from scipy import signal
from scipy.stats import linregress

logger = logging.getLogger(__name__)

class MedicalGradeVoiceAnalyzer:
    """
    의료기기 수준의 음성 분석 엔진 (Windows 호환)
    
    3단계 음성 특징 분석 파이프라인:
    1. 실제 오디오 처리 (librosa)
    2. 음성 특징 추출 (librosa + scipy)
    3. 품질 평가 및 분석
    """
    
    def __init__(self):
        # 음성 분석 파라미터
        self.sample_rate = 22050  # 표준 샘플 레이트
        self.min_duration = 3.0  # 최소 녹음 시간 (초)
        self.max_duration = 10.0  # 최대 녹음 시간 (초)
        
        # 음성 품질 임계값
        self.jitter_threshold = 2.0  # 지터 임계값 (%)
        self.shimmer_threshold = 3.0  # 쉼머 임계값 (dB)
        
        logger.info("의료기기 수준 음성 분석 엔진 초기화 완료 (Windows 호환)")
    
    def analyze_voice(self, audio_data: bytes) -> Dict:
        """
        음성 분석 메인 파이프라인
        
        Args:
            audio_data: 오디오 데이터 (bytes)
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            logger.info(f"음성 분석 시작: {len(audio_data)} bytes")
            
            # 1단계: 실제 오디오 처리
            audio_signal, sample_rate = self._load_audio_data(audio_data)
            
            # 녹음 시간 확인
            duration = len(audio_signal) / sample_rate
            if duration < self.min_duration:
                raise ValueError(f"녹음 시간이 너무 짧습니다: {duration:.1f}초 (최소 {self.min_duration}초 필요)")
            
            # 2단계: 음성 특징 추출
            voice_features = self._extract_voice_features_librosa(audio_signal, sample_rate)
            
            # 3단계: 품질 평가 및 분석
            results = self._evaluate_voice_quality(voice_features, duration)
            
            logger.info(f"음성 분석 완료: Pitch={results['pitch_hz']:.1f}Hz, Jitter={results['jitter_percent']:.1f}%")
            return results
            
        except Exception as e:
            logger.error(f"음성 분석 실패: {str(e)}")
            return self._get_error_result(str(e))
    
    def _load_audio_data(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """
        1단계: 실제 오디오 처리
        
        전송된 오디오 데이터를 librosa를 사용하여 로드하고
        실제 음성 신호(Waveform)로 변환
        """
        try:
            # 임시 파일로 저장 (librosa가 파일 경로를 요구함)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # librosa를 사용하여 오디오 로드
                audio_signal, sample_rate = librosa.load(
                    temp_file_path,
                    sr=self.sample_rate,
                    mono=True
                )
                
                logger.info(f"오디오 로드 완료: {len(audio_signal)} 샘플, {sample_rate}Hz")
                return audio_signal, sample_rate
                
            finally:
                # 임시 파일 정리
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"오디오 데이터 로드 실패: {str(e)}")
            raise
    
    def _extract_voice_features_librosa(self, audio_signal: np.ndarray, sample_rate: int) -> Dict:
        """
        2단계: 음성 특징 추출 (librosa + scipy 기반)
        
        librosa를 사용하여 음성의 핵심 건강 지표 추출:
        - 기본 주파수(F0/Pitch)
        - 지터(Jitter) - librosa 기반 근사
        - 쉼머(Shimmer) - librosa 기반 근사
        - HNR (Harmonic-to-Noise Ratio)
        """
        try:
            # 기본 주파수(F0) 추출 - librosa의 pitch 추출
            pitches, magnitudes = librosa.piptrack(
                y=audio_signal, 
                sr=sample_rate,
                threshold=0.1,
                hop_length=512
            )
            
            # 유효한 피치 값만 선택
            valid_pitches = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    valid_pitches.append(pitch)
            
            if len(valid_pitches) == 0:
                raise ValueError("유효한 음성 신호를 찾을 수 없습니다")
            
            # F0 통계 계산
            f0_values = np.array(valid_pitches)
            f0_mean = np.mean(f0_values)
            f0_std = np.std(f0_values)
            
            # 지터(Jitter) 계산 - librosa 기반 근사
            jitter_local = self._calculate_jitter_librosa(f0_values)
            
            # 쉼머(Shimmer) 계산 - librosa 기반 근사
            shimmer_local = self._calculate_shimmer_librosa(audio_signal)
            
            # HNR (Harmonic-to-Noise Ratio) 계산 - librosa 기반
            hnr = self._calculate_hnr_librosa(audio_signal, sample_rate)
            
            features = {
                "f0_mean": f0_mean,
                "f0_std": f0_std,
                "jitter_local": jitter_local,
                "shimmer_local": shimmer_local,
                "hnr": hnr,
                "f0_values": f0_values.tolist()
            }
            
            logger.info(f"음성 특징 추출 완료: F0={f0_mean:.1f}Hz, Jitter={jitter_local:.2f}%")
            return features
            
        except Exception as e:
            logger.error(f"음성 특징 추출 실패: {str(e)}")
            raise
    
    def _calculate_jitter_librosa(self, f0_values: np.ndarray) -> float:
        """
        지터(Jitter) 계산 - librosa 기반 근사
        
        연속된 F0 값들 간의 상대적 변동성 계산
        """
        try:
            if len(f0_values) < 2:
                return 0.0
            
            # 연속된 F0 값들 간의 차이
            f0_diff = np.abs(np.diff(f0_values))
            
            # 지터 계산 (평균 차이 / 평균 F0 * 100)
            jitter = (np.mean(f0_diff) / np.mean(f0_values)) * 100
            
            # 비정상 값 필터링 (0-10% 범위)
            jitter = np.clip(jitter, 0.0, 10.0)
            
            return jitter
            
        except Exception as e:
            logger.warning(f"지터 계산 실패: {str(e)}, 기본값 사용")
            return 1.0
    
    def _calculate_shimmer_librosa(self, audio_signal: np.ndarray) -> float:
        """
        쉼머(Shimmer) 계산 - librosa 기반 근사
        
        연속된 진폭 값들 간의 상대적 변동성 계산
        """
        try:
            if len(audio_signal) < 2:
                return 0.0
            
            # 프레임 단위로 진폭 분석
            frame_length = 2048
            hop_length = 512
            
            # STFT를 통한 진폭 분석
            stft = librosa.stft(audio_signal, n_fft=frame_length, hop_length=hop_length)
            magnitudes = np.abs(stft)
            
            # 프레임별 진폭 평균
            frame_amplitudes = np.mean(magnitudes, axis=0)
            
            # 연속된 프레임 간의 진폭 차이
            amp_diff = np.abs(np.diff(frame_amplitudes))
            
            # 쉼머 계산 (평균 차이 / 평균 진폭 * 100)
            if np.mean(frame_amplitudes) > 0:
                shimmer = (np.mean(amp_diff) / np.mean(frame_amplitudes)) * 100
            else:
                shimmer = 0.0
            
            # 비정상 값 필터링 (0-15% 범위)
            shimmer = np.clip(shimmer, 0.0, 15.0)
            
            return shimmer
            
        except Exception as e:
            logger.warning(f"쉼머 계산 실패: {str(e)}, 기본값 사용")
            return 2.0
    
    def _calculate_hnr_librosa(self, audio_signal: np.ndarray, sample_rate: int) -> float:
        """
        HNR (Harmonic-to-Noise Ratio) 계산 - librosa 기반
        
        음성의 하모닉 성분과 노이즈 성분의 비율
        """
        try:
            # 스펙트럼 분석
            stft = librosa.stft(audio_signal, n_fft=2048, hop_length=512)
            magnitudes = np.abs(stft)
            
            # 주파수 축 생성
            freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=2048)
            
            # 하모닉 성분 (기본 주파수와 배음)
            harmonic_power = 0
            noise_power = 0
            
            # 기본 주파수 대역 (80-400 Hz)에서 하모닉 검출
            fundamental_mask = (freqs >= 80) & (freqs <= 400)
            fundamental_freqs = freqs[fundamental_mask]
            fundamental_mags = magnitudes[fundamental_mask, :]
            
            if len(fundamental_freqs) > 0:
                # 가장 강한 주파수를 기본 주파수로 가정
                max_power_idx = np.argmax(np.mean(fundamental_mags, axis=1))
                fundamental_freq = fundamental_freqs[max_power_idx]
                
                # 하모닉 성분 (기본 주파수의 배수)
                for harmonic in range(1, 6):  # 1차~5차 하모닉
                    harmonic_freq = fundamental_freq * harmonic
                    if harmonic_freq < sample_rate / 2:
                        # 가장 가까운 주파수 인덱스 찾기
                        freq_idx = np.argmin(np.abs(freqs - harmonic_freq))
                        if freq_idx < len(magnitudes):
                            harmonic_power += np.mean(magnitudes[freq_idx, :] ** 2)
                
                # 노이즈 성분 (전체 파워에서 하모닉 파워 제외)
                total_power = np.mean(np.sum(magnitudes ** 2, axis=0))
                noise_power = total_power - harmonic_power
                
                if noise_power > 0:
                    hnr = 10 * np.log10(harmonic_power / noise_power)
                else:
                    hnr = 25.0  # 기본값
            else:
                hnr = 20.0  # 기본값
            
            # 비정상 값 필터링 (5-30dB 범위)
            hnr = np.clip(hnr, 5.0, 30.0)
            
            return hnr
            
        except Exception as e:
            logger.warning(f"HNR 계산 실패: {str(e)}, 기본값 사용")
            return 20.0
    
    def _evaluate_voice_quality(self, features: Dict, duration: float) -> Dict:
        """
        3단계: 품질 평가 및 분석
        
        추출된 지표들을 바탕으로 음성의 안정성을 평가하고
        "안정적", "보통", "불안정" 등으로 분류
        """
        try:
            # 음성 안정성 평가
            stability = self._evaluate_stability(features)
            
            # 음성 품질 등급
            quality_grade = self._evaluate_quality_grade(features)
            
            # 분석 신뢰도
            confidence = self._calculate_confidence(features, duration)
            
            results = {
                "pitch_hz": round(features["f0_mean"], 1),
                "jitter_percent": round(features["jitter_local"], 2),
                "shimmer_db": round(features["shimmer_local"], 2),
                "hnr_db": round(features["hnr"], 1),
                "stability": stability,
                "quality_grade": quality_grade,
                "analysis_confidence": confidence,
                "recording_duration": round(duration, 1)
            }
            
            logger.info(f"음성 품질 평가 완료: {stability}, {quality_grade}")
            return results
            
        except Exception as e:
            logger.error(f"음성 품질 평가 실패: {str(e)}")
            raise
    
    def _evaluate_stability(self, features: Dict) -> str:
        """
        음성 안정성 평가
        
        지터와 쉼머를 기반으로 안정성 판단
        """
        try:
            jitter = features["jitter_local"]
            shimmer = features["shimmer_local"]
            
            # 안정성 점수 계산 (낮을수록 안정적)
            stability_score = (jitter / self.jitter_threshold) + (shimmer / self.shimmer_threshold)
            
            if stability_score < 0.5:
                return "Very Stable"
            elif stability_score < 1.0:
                return "Stable"
            elif stability_score < 1.5:
                return "Moderate"
            else:
                return "Unstable"
                
        except Exception as e:
            logger.warning(f"안정성 평가 실패: {str(e)}, 기본값 사용")
            return "Moderate"
    
    def _evaluate_quality_grade(self, features: Dict) -> str:
        """
        음성 품질 등급 평가
        
        모든 지표를 종합하여 품질 등급 판단
        """
        try:
            jitter = features["jitter_local"]
            shimmer = features["shimmer_local"]
            hnr = features["hnr"]
            
            # 품질 점수 계산
            quality_score = 0
            
            # 지터 점수 (낮을수록 좋음)
            if jitter < 1.0:
                quality_score += 3
            elif jitter < 2.0:
                quality_score += 2
            elif jitter < 3.0:
                quality_score += 1
            
            # 쉼머 점수 (낮을수록 좋음)
            if shimmer < 2.0:
                quality_score += 3
            elif shimmer < 4.0:
                quality_score += 2
            elif shimmer < 6.0:
                quality_score += 1
            
            # HNR 점수 (높을수록 좋음)
            if hnr > 25:
                quality_score += 3
            elif hnr > 20:
                quality_score += 2
            elif hnr > 15:
                quality_score += 1
            
            # 총점 기반 등급
            if quality_score >= 8:
                return "Excellent"
            elif quality_score >= 6:
                return "Good"
            elif quality_score >= 4:
                return "Fair"
            else:
                return "Poor"
                
        except Exception as e:
            logger.warning(f"품질 등급 평가 실패: {str(e)}, 기본값 사용")
            return "Fair"
    
    def _calculate_confidence(self, features: Dict, duration: float) -> float:
        """
        분석 신뢰도 계산
        
        녹음 시간, 신호 품질 등을 종합하여 신뢰도 점수 계산
        """
        try:
            # 시간 기반 신뢰도
            time_confidence = min(1.0, duration / 5.0)
            
            # 신호 품질 기반 신뢰도
            quality_scores = {"Excellent": 0.95, "Good": 0.85, "Fair": 0.70, "Poor": 0.50}
            quality_confidence = quality_scores.get(self._evaluate_quality_grade(features), 0.60)
            
            # 종합 신뢰도 (가중 평균)
            confidence = 0.7 * time_confidence + 0.3 * quality_confidence
            
            return round(confidence, 2)
            
        except Exception as e:
            logger.warning(f"신뢰도 계산 실패: {str(e)}, 기본값 사용")
            return 0.75
    
    def _get_error_result(self, error_message: str) -> Dict:
        """오류 발생 시 결과"""
        return {
            "pitch_hz": 0,
            "jitter_percent": 0,
            "shimmer_db": 0,
            "hnr_db": 0,
            "stability": "Unknown",
            "quality_grade": "Unknown",
            "analysis_confidence": 0,
            "recording_duration": 0,
            "error": error_message
        } 