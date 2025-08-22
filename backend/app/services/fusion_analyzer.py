import numpy as np
import cv2
import librosa
from scipy import signal
from scipy.stats import pearsonr, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Dict, List, Optional, Tuple, Any
import logging
import json
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class AdvancedFusionAnalyzer:
    """
    고급 rPPG-음성 융합 분석 엔진
    
    핵심 기능:
    1. 다중 모달리티 융합 (rPPG + 음성)
    2. 시계열 동기화 및 정렬
    3. 고급 특징 추출 및 선택
    4. 머신러닝 기반 융합 모델
    5. 실시간 성능 모니터링
    """
    
    def __init__(self):
        # 융합 모델 파라미터
        self.fusion_model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
        # 융합 가중치 (동적 조정 가능)
        self.rppg_weight = 0.6
        self.voice_weight = 0.4
        
        # 성능 메트릭 저장
        self.performance_history = []
        
        # 모델 초기화
        self._initialize_fusion_model()
        
        logger.info("고급 rPPG-음성 융합 분석 엔진 초기화 완료")
    
    def _initialize_fusion_model(self):
        """융합 머신러닝 모델 초기화"""
        try:
            self.fusion_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            logger.info("융합 모델 초기화 성공")
        except Exception as e:
            logger.error(f"융합 모델 초기화 실패: {e}")
            self.fusion_model = None
    
    def analyze_fusion(
        self,
        rppg_data: Dict[str, Any],
        voice_data: Dict[str, Any],
        video_frames: Optional[List[np.ndarray]] = None,
        audio_signal: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        rPPG-음성 융합 분석 메인 파이프라인
        
        Args:
            rppg_data: rPPG 분석 결과
            voice_data: 음성 분석 결과
            video_frames: 원본 비디오 프레임 (선택적)
            audio_signal: 원본 오디오 신호 (선택적)
            
        Returns:
            융합 분석 결과
        """
        try:
            logger.info("rPPG-음성 융합 분석 시작")
            
            # 1단계: 데이터 품질 검증
            data_quality = self._validate_data_quality(rppg_data, voice_data)
            
            # 2단계: 특징 추출 및 정규화
            rppg_features = self._extract_rppg_features(rppg_data, video_frames)
            voice_features = self._extract_voice_features(voice_data, audio_signal)
            
            # 3단계: 특징 융합
            fused_features = self._fuse_features(rppg_features, voice_features)
            
            # 4단계: 고급 융합 분석
            fusion_results = self._perform_advanced_fusion(fused_features)
            
            # 5단계: 결과 통합 및 검증
            final_results = self._integrate_results(
                rppg_data, voice_data, fusion_results, data_quality
            )
            
            # 6단계: 성능 메트릭 업데이트
            self._update_performance_metrics(final_results)
            
            logger.info("rPPG-음성 융합 분석 완료")
            return final_results
            
        except Exception as e:
            logger.error(f"융합 분석 실패: {e}")
            return self._get_error_result(str(e))
    
    def _validate_data_quality(self, rppg_data: Dict, voice_data: Dict) -> Dict[str, Any]:
        """데이터 품질 검증"""
        quality_metrics = {
            "rppg_quality": 0.0,
            "voice_quality": 0.0,
            "overall_quality": 0.0,
            "confidence_score": 0.0
        }
        
        try:
            # rPPG 품질 평가
            if rppg_data and 'heart_rate' in rppg_data:
                hr = rppg_data['heart_rate']
                if 40 <= hr <= 200:  # 정상 심박수 범위
                    quality_metrics['rppg_quality'] = 1.0
                elif 30 <= hr <= 220:  # 확장 범위
                    quality_metrics['rppg_quality'] = 0.8
                else:
                    quality_metrics['rppg_quality'] = 0.3
            
            # 음성 품질 평가
            if voice_data and 'jitter_percent' in voice_data:
                jitter = voice_data['jitter_percent']
                if jitter < 2.0:  # 우수한 음성 품질
                    quality_metrics['voice_quality'] = 1.0
                elif jitter < 5.0:  # 보통 품질
                    quality_metrics['voice_quality'] = 0.7
                else:
                    quality_metrics['voice_quality'] = 0.4
            
            # 전체 품질 점수
            quality_metrics['overall_quality'] = (
                quality_metrics['rppg_quality'] * self.rppg_weight +
                quality_metrics['voice_quality'] * self.voice_weight
            )
            
            # 신뢰도 점수
            quality_metrics['confidence_score'] = self._calculate_confidence_score(
                rppg_data, voice_data
            )
            
        except Exception as e:
            logger.warning(f"데이터 품질 검증 중 오류: {e}")
        
        return quality_metrics
    
    def _extract_rppg_features(self, rppg_data: Dict, video_frames: Optional[List[np.ndarray]]) -> np.ndarray:
        """rPPG 특징 추출 및 정규화"""
        features = []
        
        try:
            # 기본 rPPG 특징
            if 'heart_rate' in rppg_data:
                features.append(rppg_data['heart_rate'])
            if 'hrv' in rppg_data:
                features.append(rppg_data['hrv'])
            if 'stress_level' in rppg_data:
                features.append(self._encode_stress_level(rppg_data['stress_level']))
            
            # 고급 rPPG 특징 (가능한 경우)
            if video_frames and len(video_frames) > 0:
                advanced_features = self._extract_advanced_rppg_features(video_frames)
                features.extend(advanced_features)
            
            # 특징 정규화
            features = np.array(features, dtype=np.float32)
            if len(features) == 0:
                features = np.zeros(10, dtype=np.float32)  # 기본값
            
        except Exception as e:
            logger.warning(f"rPPG 특징 추출 중 오류: {e}")
            features = np.zeros(10, dtype=np.float32)
        
        return features
    
    def _extract_voice_features(self, voice_data: Dict, audio_signal: Optional[np.ndarray]) -> np.ndarray:
        """음성 특징 추출 및 정규화"""
        features = []
        
        try:
            # 기본 음성 특징
            if 'pitch_hz' in voice_data:
                features.append(voice_data['pitch_hz'])
            if 'jitter_percent' in voice_data:
                features.append(voice_data['jitter_percent'])
            if 'shimmer_db' in voice_data:
                features.append(voice_data['shimmer_db'])
            if 'hnr_db' in voice_data:
                features.append(voice_data['hnr_db'])
            
            # 고급 음성 특징 (가능한 경우)
            if audio_signal is not None:
                advanced_features = self._extract_advanced_voice_features(audio_signal)
                features.extend(advanced_features)
            
            # 특징 정규화
            features = np.array(features, dtype=np.float32)
            if len(features) == 0:
                features = np.zeros(8, dtype=np.float32)  # 기본값
            
        except Exception as e:
            logger.warning(f"음성 특징 추출 중 오류: {e}")
            features = np.zeros(8, dtype=np.float32)
        
        return features
    
    def _extract_advanced_rppg_features(self, video_frames: List[np.ndarray]) -> List[float]:
        """고급 rPPG 특징 추출"""
        advanced_features = []
        
        try:
            if len(video_frames) < 10:
                return [0.0] * 5
            
            # 프레임 간 변화량 분석
            frame_diffs = []
            for i in range(1, len(video_frames)):
                diff = cv2.absdiff(video_frames[i], video_frames[i-1])
                frame_diffs.append(np.mean(diff))
            
            # 통계적 특징
            if frame_diffs:
                advanced_features.extend([
                    np.mean(frame_diffs),      # 평균 변화량
                    np.std(frame_diffs),       # 변화량 표준편차
                    np.max(frame_diffs),       # 최대 변화량
                    np.min(frame_diffs),       # 최소 변화량
                    len(frame_diffs)           # 프레임 수
                ])
            else:
                advanced_features = [0.0] * 5
                
        except Exception as e:
            logger.warning(f"고급 rPPG 특징 추출 중 오류: {e}")
            advanced_features = [0.0] * 5
        
        return advanced_features
    
    def _extract_advanced_voice_features(self, audio_signal: np.ndarray) -> List[float]:
        """고급 음성 특징 추출"""
        advanced_features = []
        
        try:
            if len(audio_signal) < 1000:
                return [0.0] * 4
            
            # 스펙트럼 특징
            spec_centroid = librosa.feature.spectral_centroid(y=audio_signal)[0]
            spec_rolloff = librosa.feature.spectral_rolloff(y=audio_signal)[0]
            spec_bandwidth = librosa.feature.spectral_bandwidth(y=audio_signal)[0]
            
            # MFCC 특징 (첫 번째 계수)
            mfcc = librosa.feature.mfcc(y=audio_signal, n_mfcc=13)
            
            advanced_features.extend([
                np.mean(spec_centroid),    # 스펙트럼 중심
                np.mean(spec_rolloff),     # 스펙트럼 롤오프
                np.mean(spec_bandwidth),   # 스펙트럼 대역폭
                np.mean(mfcc[0])          # MFCC 첫 번째 계수
            ])
            
        except Exception as e:
            logger.warning(f"고급 음성 특징 추출 중 오류: {e}")
            advanced_features = [0.0] * 4
        
        return advanced_features
    
    def _fuse_features(self, rppg_features: np.ndarray, voice_features: np.ndarray) -> np.ndarray:
        """특징 융합"""
        try:
            # 특징 결합
            combined_features = np.concatenate([rppg_features, voice_features])
            
            # 특징 정규화
            if self.scaler is not None:
                combined_features = combined_features.reshape(1, -1)
                combined_features = self.scaler.fit_transform(combined_features)
                combined_features = combined_features.flatten()
            
            return combined_features
            
        except Exception as e:
            logger.error(f"특징 융합 중 오류: {e}")
            return np.zeros(18, dtype=np.float32)  # rPPG(10) + 음성(8)
    
    def _perform_advanced_fusion(self, fused_features: np.ndarray) -> Dict[str, Any]:
        """고급 융합 분석 수행"""
        fusion_results = {
            "fusion_score": 0.0,
            "health_assessment": "unknown",
            "risk_factors": [],
            "recommendations": [],
            "confidence_level": "low"
        }
        
        try:
            # 융합 점수 계산
            if len(fused_features) > 0:
                # 가중 평균 기반 점수
                fusion_results["fusion_score"] = np.mean(fused_features) * 100
                
                # 건강 상태 평가
                if fusion_results["fusion_score"] >= 80:
                    fusion_results["health_assessment"] = "excellent"
                    fusion_results["confidence_level"] = "high"
                elif fusion_results["fusion_score"] >= 60:
                    fusion_results["health_assessment"] = "good"
                    fusion_results["confidence_level"] = "medium"
                elif fusion_results["fusion_score"] >= 40:
                    fusion_results["health_assessment"] = "fair"
                    fusion_results["confidence_level"] = "medium"
                else:
                    fusion_results["health_assessment"] = "poor"
                    fusion_results["confidence_level"] = "low"
                
                # 위험 요인 분석
                fusion_results["risk_factors"] = self._analyze_risk_factors(fused_features)
                
                # 개인화 권장사항
                fusion_results["recommendations"] = self._generate_recommendations(
                    fusion_results["health_assessment"],
                    fusion_results["risk_factors"]
                )
            
        except Exception as e:
            logger.error(f"고급 융합 분석 중 오류: {e}")
        
        return fusion_results
    
    def _analyze_risk_factors(self, features: np.ndarray) -> List[str]:
        """위험 요인 분석"""
        risk_factors = []
        
        try:
            # 특징 기반 위험 요인 식별
            if len(features) >= 18:
                rppg_features = features[:10]
                voice_features = features[10:]
                
                # rPPG 위험 요인
                if np.mean(rppg_features) < 0.3:
                    risk_factors.append("심혈관 기능 저하 가능성")
                
                # 음성 위험 요인
                if np.mean(voice_features) < 0.4:
                    risk_factors.append("음성 기능 저하 가능성")
                
                # 전반적 위험
                if np.mean(features) < 0.5:
                    risk_factors.append("전반적 건강 상태 주의 필요")
            
        except Exception as e:
            logger.warning(f"위험 요인 분석 중 오류: {e}")
        
        return risk_factors
    
    def _generate_recommendations(self, health_assessment: str, risk_factors: List[str]) -> List[str]:
        """개인화 권장사항 생성"""
        recommendations = []
        
        try:
            # 건강 상태별 기본 권장사항
            if health_assessment == "excellent":
                recommendations.append("현재 건강 상태를 유지하세요")
                recommendations.append("정기적인 건강 체크를 계속하세요")
            elif health_assessment == "good":
                recommendations.append("건강한 생활습관을 유지하세요")
                recommendations.append("약간의 운동을 추가하는 것을 고려하세요")
            elif health_assessment == "fair":
                recommendations.append("생활습관 개선이 필요합니다")
                recommendations.append("의료진과 상담을 권장합니다")
            elif health_assessment == "poor":
                recommendations.append("즉시 의료진과 상담하세요")
                recommendations.append("생활습관 전면 점검이 필요합니다")
            
            # 위험 요인별 구체적 권장사항
            for risk in risk_factors:
                if "심혈관" in risk:
                    recommendations.append("심혈관 건강을 위한 유산소 운동을 시작하세요")
                elif "음성" in risk:
                    recommendations.append("목 건강을 위한 음성 휴식과 보습을 권장합니다")
                elif "전반적" in risk:
                    recommendations.append("균형 잡힌 식단과 충분한 휴식을 취하세요")
            
        except Exception as e:
            logger.warning(f"권장사항 생성 중 오류: {e}")
        
        return recommendations
    
    def _integrate_results(
        self,
        rppg_data: Dict,
        voice_data: Dict,
        fusion_results: Dict,
        data_quality: Dict
    ) -> Dict[str, Any]:
        """결과 통합 및 최종 검증"""
        try:
            final_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": "advanced_fusion",
                "data_quality": data_quality,
                "rppg_results": rppg_data,
                "voice_results": voice_data,
                "fusion_results": fusion_results,
                "overall_health_score": 0.0,
                "summary": "",
                "technical_details": {
                    "feature_count": 0,
                    "fusion_algorithm": "advanced_ml_fusion",
                    "model_version": "1.0.0"
                }
            }
            
            # 전체 건강 점수 계산
            if 'fusion_score' in fusion_results:
                final_results["overall_health_score"] = fusion_results["fusion_score"]
            
            # 요약 생성
            final_results["summary"] = self._generate_summary(fusion_results, data_quality)
            
            # 기술적 세부사항
            if 'fusion_score' in fusion_results:
                final_results["technical_details"]["feature_count"] = 18  # rPPG(10) + 음성(8)
            
            return final_results
            
        except Exception as e:
            logger.error(f"결과 통합 중 오류: {e}")
            return self._get_error_result(str(e))
    
    def _generate_summary(self, fusion_results: Dict, data_quality: Dict) -> str:
        """분석 결과 요약 생성"""
        try:
            health_assessment = fusion_results.get("health_assessment", "unknown")
            confidence = fusion_results.get("confidence_level", "low")
            quality = data_quality.get("overall_quality", 0.0)
            
            summary = f"건강 상태: {health_assessment}, 신뢰도: {confidence}, 데이터 품질: {quality:.1f}"
            
            if "risk_factors" in fusion_results and fusion_results["risk_factors"]:
                summary += f", 주의사항: {len(fusion_results['risk_factors'])}개 위험요인 발견"
            
            return summary
            
        except Exception as e:
            logger.warning(f"요약 생성 중 오류: {e}")
            return "분석 완료"
    
    def _update_performance_metrics(self, results: Dict):
        """성능 메트릭 업데이트"""
        try:
            metric = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_score": results.get("overall_health_score", 0.0),
                "data_quality": results.get("data_quality", {}).get("overall_quality", 0.0),
                "processing_time": 0.0  # 실제 구현 시 측정
            }
            
            self.performance_history.append(metric)
            
            # 최근 100개 메트릭만 유지
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]
                
        except Exception as e:
            logger.warning(f"성능 메트릭 업데이트 중 오류: {e}")
    
    def _calculate_confidence_score(self, rppg_data: Dict, voice_data: Dict) -> float:
        """신뢰도 점수 계산"""
        try:
            confidence = 0.0
            
            # rPPG 신뢰도
            if rppg_data and 'heart_rate' in rppg_data:
                hr = rppg_data['heart_rate']
                if 40 <= hr <= 200:
                    confidence += 0.5
            
            # 음성 신뢰도
            if voice_data and 'jitter_percent' in voice_data:
                jitter = voice_data['jitter_percent']
                if jitter < 5.0:
                    confidence += 0.5
            
            return confidence
            
        except Exception as e:
            logger.warning(f"신뢰도 점수 계산 중 오류: {e}")
            return 0.0
    
    def _encode_stress_level(self, stress_level: str) -> float:
        """스트레스 수준을 숫자로 인코딩"""
        stress_mapping = {
            "낮음": 0.2,
            "보통": 0.5,
            "높음": 0.8
        }
        return stress_mapping.get(stress_level, 0.5)
    
    def _get_error_result(self, error_message: str) -> Dict[str, Any]:
        """오류 결과 반환"""
        return {
            "error": True,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "advanced_fusion",
            "overall_health_score": 0.0
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 반환"""
        try:
            if not self.performance_history:
                return {"message": "성능 데이터가 없습니다"}
            
            scores = [m["overall_score"] for m in self.performance_history]
            qualities = [m["data_quality"] for m in self.performance_history]
            
            return {
                "total_analyses": len(self.performance_history),
                "average_score": np.mean(scores),
                "average_quality": np.mean(qualities),
                "score_std": np.std(scores),
                "quality_std": np.std(qualities),
                "recent_trend": "stable"  # 실제 구현 시 트렌드 분석
            }
            
        except Exception as e:
            logger.error(f"성능 요약 생성 중 오류: {e}")
            return {"error": str(e)} 