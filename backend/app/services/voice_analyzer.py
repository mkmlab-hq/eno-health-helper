#!/usr/bin/env python3
"""
음성 분석 서비스 - '불사조 엔진' 음성 분석 모듈
"""

import numpy as np
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    """음성 분석기 - 음성 품질 및 건강 지표 분석"""
    
    def __init__(self):
        self.sample_rate = 44100  # 기본 샘플링 레이트
        self.analysis_duration = 5.0  # 분석할 음성 길이 (초)
        
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
        try:
            logger.info(f"🎵 음성 분석 시작: {len(audio_data)} bytes")
            
            # 실제 구현에서는 librosa나 parselmouth를 사용
            # 현재는 시뮬레이션 데이터로 분석
            result = self._analyze_voice_simulation(audio_data)
            
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
                "confidence": round(confidence, 2),
                "voice_quality": voice_quality,
                "analysis_method": "voice_analysis_simulation",
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"음성 분석 시뮬레이션 실패: {e}")
            return self._get_fallback_result()
    
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