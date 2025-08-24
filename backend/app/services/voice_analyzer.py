#!/usr/bin/env python3
"""
음성 분석 서비스 - '불사조 엔진' 음성 분석 모듈
"""

import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    """음성 분석기 - 음성 품질 및 건강 지표 분석"""
    
    def __init__(self):
        self.sample_rate = 44100  # 기본 샘플링 레이트
        self.analysis_duration = 5.0  # 분석할 음성 길이 (초)
        
        # 품질/신뢰도 임계값
        self.min_snr_db = 15.0              # 최소 허용 SNR(dB)
        self.min_signal_strength = 0.08     # 최소 신호 강도(RMS)
        self.max_noise_level = 0.15         # 최대 허용 노이즈 레벨(RMS)
        
        # 실시간 모니터링 상태
        self._rt_buffer: Optional[np.ndarray] = None
        self._rt_sample_rate: int = self.sample_rate
        self._rt_max_seconds: float = 6.0   # 최근 N초 윈도우로 모니터링
        
        # 음성 품질 임계값
        self.jitter_thresholds = {
            'excellent': 0.2,
            'good': 0.4,
            'fair': 0.6,
            'poor': 0.8
        }
        
        self.shimmer_thresholds = {
            'excellent': 0.2,
            'good': 0.4,
            'fair': 0.6,
            'poor': 0.8
        }
        
        logger.info("✅ VoiceAnalyzer 초기화 완료")
    
    async def analyze_voice(self, audio_data: bytes) -> Dict[str, Any]:
        """음성 데이터 분석"""
        import asyncio
        try:
            logger.info(f"🎵 음성 분석 시작: {len(audio_data)} bytes")
            # 1) 실제 오디오 품질 평가 (SNR/강도/노이즈)
            quality = await asyncio.to_thread(self._analyze_real_audio_quality, audio_data)
            
            # 2) 음성 특징(피치/지터/시머/HNR)은 기존 시뮬레이션을 유지하되, 신뢰도는 품질 기반으로 보정
            base_result = await asyncio.to_thread(self._analyze_voice_simulation, audio_data)
            
            reliability_score = self._compute_reliability_score(quality, base_result)
            remeasure, reasons = self._should_request_remeasurement(quality)
            quality_report = self.generate_quality_report(quality, base_result, reliability_score, remeasure, reasons)
            
            # 추가 통합 필드 (호환성): pitch_hz, jitter_percent, shimmer_db, hnr_db, stability
            pitch_hz = base_result.get("f0")
            jitter_percent = float(base_result.get("jitter", 0.0)) * 100.0
            shimmer_val = float(base_result.get("shimmer", 0.0))
            shimmer_db = float(20.0 * np.log10((1.0 + shimmer_val) / (1.0 - shimmer_val + 1e-10)))
            hnr_db = float(base_result.get("hnr", 0.0))
            stability_map = {
                "excellent": "Very Stable",
                "good": "Stable",
                "fair": "Moderate",
                "poor": "Unstable",
                "unknown": "Unknown"
            }
            stability = stability_map.get(base_result.get("voice_quality", "unknown"), "Unknown")

            result = {
                **base_result,
                "snr_db": round(quality.get("snr_db", 0.0), 2),
                "signal_strength": round(quality.get("signal_strength", 0.0), 4),
                "noise_level": round(quality.get("noise_level", 0.0), 4),
                "quality_grade": quality.get("quality_grade", "unknown"),
                "analysis_confidence": round(min(0.99, max(0.0, reliability_score / 100.0)), 3),
                "reliability_score": int(round(reliability_score)),
                "remeasurement_required": remeasure,
                "remeasurement_reasons": reasons,
                "quality_report": quality_report,
                "analysis_method": "voice_analysis_with_quality_v1",
                # 호환 필드
                "pitch_hz": pitch_hz,
                "jitter_percent": round(jitter_percent, 3),
                "shimmer_db": round(shimmer_db, 3),
                "hnr_db": round(hnr_db, 2),
                "stability": stability
            }
            
            logger.info(f"✅ 음성 분석 완료: F0={result.get('f0', 'N/A')} Hz")
            return result
        except Exception as e:
            logger.error(f"❌ 음성 분석 실패: {e}")
            return self._get_fallback_result()
    
    def _analyze_voice_simulation(self, audio_data: bytes) -> Dict[str, Any]:
        """음성 분석 시뮬레이션 (실제 구현 시 교체)"""
        try:
            # 시뮬레이션된 음성 분석 결과
            # 실제로는 librosa.analysis.pitch, parselmouth 등을 사용
            
            # 기본 음성 특성 (성인 남성 기준)
            base_f0 = 120.0  # 기본 주파수 (Hz)
            f0_variation = np.random.normal(0, 10)  # 주파수 변화
            f0 = base_f0 + f0_variation
            
            # Jitter (주파수 변화율)
            jitter = np.random.uniform(0.1, 0.6)
            
            # Shimmer (진폭 변화율)
            shimmer = np.random.uniform(0.1, 0.7)
            
            # HNR (Harmonic-to-Noise Ratio)
            hnr = np.random.uniform(8.0, 25.0)
            
            # 신뢰도 계산
            confidence = self._calculate_voice_confidence(f0, jitter, shimmer, hnr)
            
            # 음성 품질 평가
            voice_quality = self._assess_voice_quality(jitter, shimmer)
            
            result = {
                "f0": round(f0, 1),
                "jitter": round(jitter, 3),
                "shimmer": round(shimmer, 3),
                "hnr": round(hnr, 1),
                "confidence": round(confidence, 2),  # 유지 (0~1)
                "voice_quality": voice_quality,
                "analysis_method": "voice_analysis_simulation",
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"음성 분석 시뮬레이션 실패: {e}")
            return self._get_fallback_result()

    # ----------------------
    # 실제 음성 품질 분석 모듈
    # ----------------------
    def _analyze_real_audio_quality(self, audio_data: bytes) -> Dict[str, Any]:
        """
        실제 오디오 바이트로부터 신호 품질 지표 계산
        - SNR(dB), 신호 강도(RMS), 노이즈 레벨(RMS), 품질 등급
        """
        try:
            signal_array, sr = self._bytes_to_signal(audio_data)
            if signal_array is None or len(signal_array) == 0:
                return {
                    "snr_db": 0.0,
                    "signal_strength": 0.0,
                    "noise_level": 1.0,
                    "quality_grade": "poor",
                    "sample_rate": self.sample_rate,
                    "duration": 0.0
                }
            
            # 정규화 및 DC 제거
            x = signal_array.astype(np.float32)
            x = x - float(np.mean(x))
            max_abs = float(np.max(np.abs(x))) if np.max(np.abs(x)) > 0 else 1.0
            x = x / max_abs
            
            # 신호/노이즈 파워 추정
            signal_power = float(np.var(x))
            noise_power = float(np.var(np.diff(x)))  # 고주파 성분을 노이즈로 근사
            snr_db = 10.0 * np.log10((signal_power + 1e-12) / (noise_power + 1e-12))
            
            # 강도/노이즈 수준
            signal_strength = float(np.sqrt(np.mean(x ** 2)))  # RMS
            noise_level = float(np.sqrt(noise_power))
            
            # 품질 등급
            quality_grade = self._grade_quality(snr_db, signal_strength, noise_level)
            
            return {
                "snr_db": float(np.clip(snr_db, -10, 60)),
                "signal_strength": signal_strength,
                "noise_level": noise_level,
                "quality_grade": quality_grade,
                "sample_rate": sr,
                "duration": len(x) / sr
            }
        except Exception as e:
            logger.error(f"실제 오디오 품질 분석 실패: {e}")
            return {
                "snr_db": 0.0,
                "signal_strength": 0.0,
                "noise_level": 1.0,
                "quality_grade": "unknown",
                "sample_rate": self.sample_rate,
                "duration": 0.0
            }

    def _grade_quality(self, snr_db: float, strength: float, noise_level: float) -> str:
        """품질 등급화"""
        score = 0
        if snr_db > 25: score += 3
        elif snr_db > 20: score += 2
        elif snr_db > 15: score += 1
        
        if strength > 0.20: score += 3
        elif strength > 0.12: score += 2
        elif strength > 0.08: score += 1
        
        if noise_level < 0.06: score += 3
        elif noise_level < 0.10: score += 2
        elif noise_level < 0.15: score += 1
        
        if score >= 7: return "excellent"
        if score >= 5: return "good"
        if score >= 3: return "fair"
        return "poor"

    def _bytes_to_signal(self, audio_data: bytes) -> Tuple[Optional[np.ndarray], int]:
        """
        오디오 바이트를 단일 채널 신호(np.float32, -1~1)로 변환.
        - 간단한 WAV(PCM16) 헤더 파싱 시도 후, 실패 시 일반 PCM16 가정
        """
        try:
            if len(audio_data) < 8:
                return None, self.sample_rate
            
            # WAV 포맷 간단 파싱
            if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                try:
                    sr = int.from_bytes(audio_data[24:28], byteorder='little', signed=False)
                    bits_per_sample = int.from_bytes(audio_data[34:36], byteorder='little', signed=False)
                    # data 청크 오프셋 탐색
                    offset = 12
                    data_offset = None
                    while offset + 8 <= len(audio_data):
                        chunk_id = audio_data[offset:offset+4]
                        chunk_size = int.from_bytes(audio_data[offset+4:offset+8], 'little')
                        if chunk_id == b'data':
                            data_offset = offset + 8
                            break
                        offset += 8 + chunk_size
                    if data_offset is None:
                        data_offset = 44  # 일반적 기본값
                    pcm = audio_data[data_offset:]
                    if bits_per_sample == 16:
                        arr = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
                    elif bits_per_sample == 32:
                        # 부호 있는 32비트 정수 또는 float32일 수 있음. 우선 int32로 시도
                        try:
                            arr = np.frombuffer(pcm, dtype=np.int32).astype(np.float32) / 2147483648.0
                        except Exception:
                            arr = np.frombuffer(pcm, dtype=np.float32)
                    else:
                        # 미지원 비트 깊이: 바이트를 int16로 다운샘플
                        arr = np.frombuffer(pcm, dtype=np.uint8).astype(np.float32)
                        arr = (arr - 128.0) / 128.0
                    return arr, sr if sr > 0 else self.sample_rate
                except Exception:
                    pass
            
            # 일반 PCM16 가정 (헤더 없음)
            if len(audio_data) % 2 == 0:
                arr = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                return arr, self.sample_rate
            
            # 마지막 수단: 바이트를 0-255로 정규화 후 -1~1 변환
            arr = np.frombuffer(audio_data, dtype=np.uint8).astype(np.float32)
            arr = (arr - 128.0) / 128.0
            return arr, self.sample_rate
        except Exception:
            return None, self.sample_rate

    # ----------------------
    # 실시간 품질 모니터링
    # ----------------------
    def reset_quality_monitor(self, sample_rate: Optional[int] = None):
        """실시간 모니터링 버퍼 초기화"""
        self._rt_sample_rate = int(sample_rate) if sample_rate else self.sample_rate
        self._rt_buffer = np.zeros(0, dtype=np.float32)

    def update_quality_monitor(self, audio_chunk: bytes, sample_rate: Optional[int] = None) -> Dict[str, Any]:
        """
        스트리밍 오디오 청크로 품질 지표를 실시간 계산하여 반환
        Returns: {snr_db, signal_strength, noise_level, quality_grade, reliability_score, remeasurement_required, reasons}
        """
        try:
            if sample_rate:
                self._rt_sample_rate = int(sample_rate)
            if self._rt_buffer is None:
                self.reset_quality_monitor(self._rt_sample_rate)
            
            arr, sr = self._bytes_to_signal(audio_chunk)
            if arr is None or len(arr) == 0:
                return {"snr_db": 0.0, "signal_strength": 0.0, "noise_level": 1.0, "quality_grade": "poor", "reliability_score": 0, "remeasurement_required": True, "reasons": ["no_signal"]}
            
            # 버퍼 업데이트 (최근 윈도우 유지)
            self._rt_buffer = np.concatenate([self._rt_buffer, arr.astype(np.float32)])
            max_len = int(self._rt_max_seconds * sr)
            if len(self._rt_buffer) > max_len:
                self._rt_buffer = self._rt_buffer[-max_len:]
            
            # 현재 버퍼로 품질 계산
            x = self._rt_buffer - float(np.mean(self._rt_buffer))
            x = x / (float(np.max(np.abs(x))) + 1e-12)
            signal_power = float(np.var(x))
            noise_power = float(np.var(np.diff(x)))
            snr_db = 10.0 * np.log10((signal_power + 1e-12) / (noise_power + 1e-12))
            signal_strength = float(np.sqrt(np.mean(x ** 2)))
            noise_level = float(np.sqrt(noise_power))
            quality_grade = self._grade_quality(snr_db, signal_strength, noise_level)
            quality = {"snr_db": snr_db, "signal_strength": signal_strength, "noise_level": noise_level, "quality_grade": quality_grade}
            
            # 신뢰도 및 재측정 판단
            dummy_features = {"hnr": 15.0, "jitter": 0.4, "shimmer": 0.4, "f0": 150.0}
            reliability = self._compute_reliability_score(quality, dummy_features)
            remeasure, reasons = self._should_request_remeasurement(quality)
            
            return {
                "snr_db": round(float(np.clip(snr_db, -10, 60)), 2),
                "signal_strength": round(signal_strength, 4),
                "noise_level": round(noise_level, 4),
                "quality_grade": quality_grade,
                "reliability_score": int(round(reliability)),
                "remeasurement_required": remeasure,
                "reasons": reasons,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"실시간 품질 모니터링 실패: {e}")
            return {"snr_db": 0.0, "signal_strength": 0.0, "noise_level": 1.0, "quality_grade": "unknown", "reliability_score": 0, "remeasurement_required": True, "reasons": ["error"]}
    
    def _calculate_voice_confidence(self, f0: float, jitter: float, shimmer: float, hnr: float) -> float:
        """음성 분석 신뢰도 계산"""
        try:
            # F0 신뢰도 (정상 범위: 80-400 Hz)
            f0_confidence = 1.0
            if f0 < 80 or f0 > 400:
                f0_confidence = 0.5
            
            # Jitter 신뢰도 (낮을수록 좋음)
            jitter_confidence = max(0.1, 1.0 - jitter)
            
            # Shimmer 신뢰도 (낮을수록 좋음)
            shimmer_confidence = max(0.1, 1.0 - shimmer)
            
            # HNR 신뢰도 (높을수록 좋음)
            hnr_confidence = min(1.0, hnr / 30.0)
            
            # 종합 신뢰도
            total_confidence = (
                f0_confidence * 0.3 +
                jitter_confidence * 0.25 +
                shimmer_confidence * 0.25 +
                hnr_confidence * 0.2
            )
            
            return total_confidence
            
        except Exception as e:
            logger.error(f"신뢰도 계산 실패: {e}")
            return 0.5

    def _compute_reliability_score(self, quality: Dict[str, Any], features: Dict[str, Any]) -> float:
        """0-100% 신뢰도 점수 계산 (품질 + 특징 종합)"""
        try:
            snr = float(quality.get("snr_db", 0.0))
            strength = float(quality.get("signal_strength", 0.0))
            noise = float(quality.get("noise_level", 1.0))
            
            # 개별 점수 (0~100)
            snr_score = np.clip((snr - 10) / (30 - 10), 0, 1) * 100  # 10~30dB를 0~100으로 매핑
            strength_score = np.clip((strength - 0.05) / (0.25 - 0.05), 0, 1) * 100
            noise_score = (1.0 - np.clip((noise - 0.05) / (0.20 - 0.05), 0, 1)) * 100
            
            # 특징 기반 보정 (옵션)
            hnr = float(features.get("hnr", 15.0))
            jitter = float(features.get("jitter", 0.5))
            shimmer = float(features.get("shimmer", 0.5))
            f0 = float(features.get("f0", 150.0))
            
            hnr_score = np.clip(hnr / 30.0, 0, 1) * 100
            jitter_score = (1.0 - np.clip(jitter, 0, 1)) * 100
            shimmer_score = (1.0 - np.clip(shimmer, 0, 1)) * 100
            f0_penalty = 0 if 80 <= f0 <= 400 else 15
            
            # 가중 평균
            quality_component = 0.45 * snr_score + 0.30 * strength_score + 0.25 * noise_score
            feature_component = 0.35 * hnr_score + 0.325 * jitter_score + 0.325 * shimmer_score - f0_penalty
            
            reliability = 0.6 * quality_component + 0.4 * feature_component
            return float(np.clip(reliability, 0, 100))
        except Exception as e:
            logger.error(f"신뢰도 점수 계산 실패: {e}")
            return 50.0
    
    def _assess_voice_quality(self, jitter: float, shimmer: float) -> str:
        """음성 품질 평가"""
        try:
            # Jitter 품질
            jitter_quality = "poor"
            for quality, threshold in self.jitter_thresholds.items():
                if jitter <= threshold:
                    jitter_quality = quality
                    break
            
            # Shimmer 품질
            shimmer_quality = "poor"
            for quality, threshold in self.shimmer_thresholds.items():
                if shimmer <= threshold:
                    shimmer_quality = quality
                    break
            
            # 종합 품질 (더 나쁜 쪽 기준)
            quality_scores = {
                'excellent': 4,
                'good': 3,
                'fair': 2,
                'poor': 1
            }
            
            jitter_score = quality_scores.get(jitter_quality, 1)
            shimmer_score = quality_scores.get(shimmer_quality, 1)
            
            overall_score = min(jitter_score, shimmer_score)
            
            # 점수를 품질로 변환
            for quality, score in quality_scores.items():
                if overall_score >= score:
                    return quality
            
            return "poor"
            
        except Exception as e:
            logger.error(f"음성 품질 평가 실패: {e}")
            return "unknown"

    def _should_request_remeasurement(self, quality: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """품질 기준 미달 시 재측정 요청 판단 및 사유 반환"""
        reasons: List[str] = []
        snr = float(quality.get("snr_db", 0.0))
        strength = float(quality.get("signal_strength", 0.0))
        noise = float(quality.get("noise_level", 1.0))
        
        if snr < self.min_snr_db:
            reasons.append("low_snr")
        if strength < self.min_signal_strength:
            reasons.append("weak_signal")
        if noise > self.max_noise_level:
            reasons.append("high_noise")
        
        return (len(reasons) > 0, reasons)

    def generate_quality_report(
        self,
        quality: Dict[str, Any],
        features: Dict[str, Any],
        reliability_score: float,
        remeasurement_required: bool,
        reasons: List[str]
    ) -> Dict[str, Any]:
        """음성 품질 보고서 생성"""
        try:
            recommendations: List[str] = []
            if "low_snr" in reasons:
                recommendations.append("주변 소음을 줄이고 마이크에 더 가까이 말해주세요.")
            if "weak_signal" in reasons:
                recommendations.append("마이크 입력 감도를 높이거나 더 큰 목소리로 말해주세요.")
            if "high_noise" in reasons:
                recommendations.append("조용한 환경에서 재측정해주세요.")
            if not recommendations:
                recommendations.append("음성 품질이 양호합니다.")
            
            return {
                "metrics": {
                    "snr_db": round(float(quality.get("snr_db", 0.0)), 2),
                    "signal_strength": round(float(quality.get("signal_strength", 0.0)), 4),
                    "noise_level": round(float(quality.get("noise_level", 0.0)), 4),
                    "quality_grade": quality.get("quality_grade", "unknown"),
                },
                "features": {
                    "f0": features.get("f0"),
                    "jitter": features.get("jitter"),
                    "shimmer": features.get("shimmer"),
                    "hnr": features.get("hnr"),
                },
                "reliability_score": int(round(reliability_score)),
                "remeasurement_required": remeasurement_required,
                "reasons": reasons,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"품질 보고서 생성 실패: {e}")
            return {
                "metrics": {},
                "features": {},
                "reliability_score": int(round(reliability_score)) if reliability_score is not None else 0,
                "remeasurement_required": remeasurement_required,
                "reasons": reasons,
                "recommendations": ["보고서 생성 중 오류가 발생했습니다. 다시 시도해주세요."],
                "timestamp": datetime.now().isoformat()
            }


class MedicalGradeVoiceAnalyzer(VoiceAnalyzer):
    """기존 코드 호환을 위한 별칭 클래스 (VoiceAnalyzer 기능 사용)"""
    pass
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """오류 시 기본 결과 반환"""
        return {
            "f0": 200.0,
            "jitter": 0.5,
            "shimmer": 0.5,
            "hnr": 15.0,
            "confidence": 0.3,
            "voice_quality": "poor",
            "analysis_method": "fallback",
            "error": "음성 분석 실패",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_voice_health_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """음성 분석 결과를 바탕으로 한 건강 인사이트"""
        try:
            f0 = analysis_result.get("f0", 200)
            jitter = analysis_result.get("jitter", 0.5)
            shimmer = analysis_result.get("shimmer", 0.5)
            hnr = analysis_result.get("hnr", 15.0)
            
            insights = {
                "overall_assessment": "보통",
                "voice_stability": "보통",
                "vocal_fatigue": "보통",
                "recommendations": []
            }
            
            # 전반적 평가
            if jitter < 0.3 and shimmer < 0.3 and hnr > 20:
                insights["overall_assessment"] = "양호"
            elif jitter > 0.6 or shimmer > 0.6 or hnr < 10:
                insights["overall_assessment"] = "주의 필요"
            
            # 음성 안정성
            if jitter < 0.4 and shimmer < 0.4:
                insights["voice_stability"] = "안정적"
            elif jitter > 0.7 or shimmer > 0.7:
                insights["voice_stability"] = "불안정"
            
            # 성대 피로도
            if jitter > 0.6 or shimmer > 0.6:
                insights["vocal_fatigue"] = "피로 징후"
            elif jitter < 0.3 and shimmer < 0.3:
                insights["vocal_fatigue"] = "양호"
            
            # 권장사항
            if jitter > 0.5:
                insights["recommendations"].append("목소리 휴식이 필요합니다")
            if shimmer > 0.5:
                insights["recommendations"].append("성대 보호가 필요합니다")
            if hnr < 15:
                insights["recommendations"].append("음성 품질 개선이 필요합니다")
            
            if not insights["recommendations"]:
                insights["recommendations"].append("현재 음성 상태가 양호합니다")
            
            return insights
            
        except Exception as e:
            logger.error(f"건강 인사이트 생성 실패: {e}")
            return {
                "overall_assessment": "분석 불가",
                "voice_stability": "분석 불가",
                "vocal_fatigue": "분석 불가",
                "recommendations": ["음성 분석에 실패했습니다"]
            } 