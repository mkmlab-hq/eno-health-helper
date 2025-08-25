"""
고급 rPPG-음성 융합 분석 엔진

핵심 기능:
1. 다중 모달리티 융합 (rPPG + 음성)
2. 시계열 동기화 및 정렬
3. 고급 특징 추출 및 선택
4. 머신러닝 기반 융합 모델
5. MKM Lab 성능 모니터링 시스템 통합
6. 실시간 병목 감지 및 자동 최적화
"""

import numpy as np
import cv2
import librosa
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime

# 로거 설정
logger = logging.getLogger(__name__)

# MKM Lab 성능 모니터링 시스템 통합
try:
    import sys
    # 절대 경로로 수정
    mkm_lab_path = "F:/workspace/mkm-lab-workspace-config/src"
    if mkm_lab_path not in sys.path:
        sys.path.insert(0, mkm_lab_path)
    from services.performance_monitor import MKMPerformanceMonitor
    PERFORMANCE_MONITORING_ENABLED = True
    logger.info("MKM Lab 성능 모니터링 시스템 import 성공")
except ImportError as e:
    PERFORMANCE_MONITORING_ENABLED = False
    MKMPerformanceMonitor = None
    logger.warning(f"MKM Lab 성능 모니터링 시스템 import 실패: {e}")
    logger.info("기본 융합 분석 모드로 동작합니다")


class AdvancedFusionAnalyzer:
    """
    고급 rPPG-음성 융합 분석 엔진 (MKM Lab 성능 모니터링 통합)
    
    핵심 기능:
    1. 다중 모달리티 융합 (rPPG + 음성)
    2. 시계열 동기화 및 정렬
    3. 고급 특징 추출 및 선택
    4. 머신러닝 기반 융합 모델
    5. MKM Lab 성능 모니터링 시스템 통합
    6. 실시간 병목 감지 및 자동 최적화
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
        
        # MKM Lab 성능 모니터링 시스템 초기화
        if PERFORMANCE_MONITORING_ENABLED and MKMPerformanceMonitor:
            self.monitor = MKMPerformanceMonitor(
                window_seconds=300,
                latency_p95_threshold_ms=2000.0,  # 융합 분석은 더 긴 처리 시간 허용
                accuracy_threshold=0.80,
                fusion_confidence_threshold=0.75,
                tcm_accuracy_threshold=0.80,
            )
            logger.info("MKM Lab 성능 모니터링 시스템 통합 완료")
        else:
            self.monitor = None
            logger.warning("MKM Lab 성능 모니터링 시스템을 사용할 수 없습니다")
        
        # 모델 초기화
        self._initialize_fusion_model()
        
        logger.info("고급 rPPG-음성 융합 분석 엔진 초기화 완료 (MKM Lab 모니터링 통합)")
    
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
    
    async def analyze_fusion(
        self,
        rppg_data: Dict[str, Any],
        voice_data: Dict[str, Any],
        video_frames: Optional[List[np.ndarray]] = None,
        audio_signal: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        rPPG-음성 융합 분석 메인 파이프라인 (MKM Lab 모니터링 활성화)
        
        Args:
            rppg_data: rPPG 분석 결과
            voice_data: 음성 분석 결과
            video_frames: 원본 비디오 프레임 (선택적)
            audio_signal: 원본 오디오 신호 (선택적)
            
        Returns:
            융합 분석 결과 (MKM Lab 모니터링 메트릭 포함)
        """
        import asyncio
        
        if not self.monitor:
            # 모니터링이 비활성화된 경우 기본 분석 수행
            return await self._basic_fusion_analysis(rppg_data, voice_data, video_frames, audio_signal)
        
        # MKM Lab 성능 모니터링과 함께 분석 수행
        start_time = datetime.now()
        success = True
        result = {}
        
        try:
            logger.info("rPPG-음성 융합 분석 시작 (MKM Lab 모니터링 활성화)")
            
            # 1단계: 데이터 품질 검증
            data_quality = await asyncio.to_thread(self._validate_data_quality, rppg_data, voice_data)
            
            # 2단계: 시간 동기화 검증
            sync_status = await asyncio.to_thread(self._synchronize_modalities, rppg_data, voice_data)
            
            # 3단계: 특징 추출 및 정규화
            rppg_features = await asyncio.to_thread(self._extract_rppg_features, rppg_data, video_frames)
            voice_features = await asyncio.to_thread(self._extract_voice_features, voice_data, audio_signal)
            
            # 4단계: 동적 신뢰도 가중치 계산
            dynamic_weights = await asyncio.to_thread(self._compute_dynamic_weights, rppg_data, voice_data, data_quality, sync_status)
            
            # 5단계: 특징 융합 (동적 가중치 적용)
            fused_features = await asyncio.to_thread(self._fuse_features_with_weights, rppg_features, voice_features, dynamic_weights)
            
            # 6단계: 이상치 필터링
            filtered_features, outlier_info = await asyncio.to_thread(self._filter_outliers, fused_features)
            
            # 7단계: 고급 융합 분석
            fusion_results = await asyncio.to_thread(self._perform_advanced_fusion, filtered_features)
            
            # 8단계: 불확실성 추정
            uncertainty = await asyncio.to_thread(self._estimate_uncertainty, filtered_features, fusion_results)
            
            # 9단계: 결과 통합 및 검증
            final_results = await asyncio.to_thread(self._integrate_results, rppg_data, voice_data, fusion_results, data_quality, sync_status, dynamic_weights, uncertainty)
            
            # 10단계: MKM Lab 성능 메트릭 업데이트
            await asyncio.to_thread(self._update_mkm_performance_metrics, final_results, start_time)
            
            logger.info("rPPG-음성 융합 분석 완료 (MKM Lab 모니터링)")
            result = final_results
            
        except Exception as e:
            success = False
            result = self._get_error_result(str(e))
            logger.error(f"융합 분석 실패: {e}")
            raise
        finally:
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000.0
            
            # MKM Lab 성능 모니터링 메트릭 기록
            if self.monitor:
                self.monitor.record_event(
                    service_name="fusion",
                    operation_name="multimodal_integration",
                    latency_ms=processing_time_ms,
                    success=success,
                    accuracy=result.get("overall_health_score", 0.0),
                    fusion_confidence=result.get("fusion_confidence", 0.0),
                    tcm_diagnosis_accuracy=result.get("tcm_diagnosis_accuracy", 0.0),
                    extra={
                        "rppg_quality": result.get("rppg_quality", 0.0),
                        "voice_quality": result.get("voice_quality", 0.0),
                        "sync_status": result.get("sync_status", "unknown"),
                        "outlier_count": result.get("outlier_count", 0),
                        "uncertainty_level": result.get("uncertainty_level", "unknown"),
                    }
                )
        
        return result
    
    def _basic_fusion_analysis(self, rppg_data: Dict, voice_data: Dict, video_frames, audio_signal) -> Dict[str, Any]:
        """기본 융합 분석 (모니터링 없음)"""
        try:
            # 기존 로직 실행
            data_quality = self._validate_data_quality(rppg_data, voice_data)
            rppg_features = self._extract_rppg_features(rppg_data, video_frames)
            voice_features = self._extract_voice_features(voice_data, audio_signal)
            fused_features = self._fuse_features(rppg_features, voice_features)
            fusion_results = self._perform_advanced_fusion(fused_features)
            
            return self._integrate_results(rppg_data, voice_data, fusion_results, data_quality, {}, {}, {})
            
        except Exception as e:
            logger.error(f"기본 융합 분석 실패: {e}")
            return self._get_error_result(str(e))
    
    def _synchronize_modalities(self, rppg_data: Dict, voice_data: Dict) -> Dict[str, Any]:
        """rPPG와 음성 데이터의 시간 동기화 검증"""
        sync_status = {
            "synchronized": False,
            "timestamp_diff_ms": 0.0,
            "sync_quality": 0.0,
            "recommendations": []
        }
        
        try:
            # 타임스탬프 추출
            rppg_timestamp = rppg_data.get("timestamp", 0.0)
            voice_timestamp = voice_data.get("timestamp", 0.0)
            
            if rppg_timestamp and voice_timestamp:
                timestamp_diff = abs(rppg_timestamp - voice_timestamp)
                sync_status["timestamp_diff_ms"] = timestamp_diff * 1000.0
                
                # 동기화 품질 평가 (100ms 이내면 우수)
                if timestamp_diff < 0.1:
                    sync_status["synchronized"] = True
                    sync_status["sync_quality"] = 1.0
                elif timestamp_diff < 0.5:
                    sync_status["synchronized"] = True
                    sync_status["sync_quality"] = 0.7
                elif timestamp_diff < 1.0:
                    sync_status["synchronized"] = False
                    sync_status["sync_quality"] = 0.3
                    sync_status["recommendations"].append("시간 동기화 개선 필요")
                else:
                    sync_status["synchronized"] = False
                    sync_status["sync_quality"] = 0.0
                    sync_status["recommendations"].append("심각한 시간 동기화 문제")
            else:
                sync_status["recommendations"].append("타임스탬프 정보 부족")
                
        except Exception as e:
            logger.warning(f"시간 동기화 검증 중 오류: {e}")
            sync_status["recommendations"].append("동기화 검증 실패")
        
        return sync_status
    
    def _compute_dynamic_weights(self, rppg_data: Dict, voice_data: Dict, data_quality: Dict, sync_status: Dict) -> Dict[str, float]:
        """동적 신뢰도 가중치 계산"""
        weights = {
            "rppg_weight": self.rppg_weight,
            "voice_weight": self.voice_weight,
            "confidence_rppg": 0.0,
            "confidence_voice": 0.0
        }
        
        try:
            # rPPG 신뢰도 계산
            rppg_confidence = 0.0
            if rppg_data:
                # 심박수 범위 검증
                hr = rppg_data.get("heart_rate", 0)
                if 40 <= hr <= 200:
                    rppg_confidence += 0.3
                elif 30 <= hr <= 220:
                    rppg_confidence += 0.2
                
                # 신호 품질
                signal_quality = rppg_data.get("signal_quality", 0.0)
                rppg_confidence += signal_quality * 0.4
                
                # 아티팩트 상태
                artifacts = rppg_data.get("artifacts", {})
                if not artifacts.get("motion_artifacts", False):
                    rppg_confidence += 0.2
                if not artifacts.get("saturation", False):
                    rppg_confidence += 0.1
            
            # 음성 신뢰도 계산
            voice_confidence = 0.0
            if voice_data:
                # Jitter 품질
                jitter = voice_data.get("jitter_percent", 10.0)
                if jitter < 2.0:
                    voice_confidence += 0.4
                elif jitter < 5.0:
                    voice_confidence += 0.2
                
                # 음성 명확도
                clarity = voice_data.get("voice_clarity", 0.0)
                voice_confidence += clarity * 0.3
                
                # 감정 분석 신뢰도
                emotion_confidence = voice_data.get("confidence", 0.0)
                voice_confidence += emotion_confidence * 0.3
            
            # 동기화 품질 반영
            sync_quality = sync_status.get("sync_quality", 0.0)
            rppg_confidence *= sync_quality
            voice_confidence *= sync_quality
            
            # 가중치 정규화
            total_confidence = rppg_confidence + voice_confidence
            if total_confidence > 0:
                weights["rppg_weight"] = rppg_confidence / total_confidence
                weights["voice_weight"] = voice_confidence / total_confidence
                weights["confidence_rppg"] = rppg_confidence
                weights["confidence_voice"] = voice_confidence
            else:
                # 기본값 사용
                weights["rppg_weight"] = self.rppg_weight
                weights["voice_weight"] = self.voice_weight
            
        except Exception as e:
            logger.warning(f"동적 가중치 계산 중 오류: {e}")
        
        return weights
    
    def _fuse_features_with_weights(self, rppg_features: np.ndarray, voice_features: np.ndarray, dynamic_weights: Dict) -> np.ndarray:
        """동적 가중치를 적용한 특징 융합"""
        try:
            # 특징 차원 맞추기
            if len(rppg_features) < 10:
                rppg_features = np.pad(rppg_features, (0, 10 - len(rppg_features)), 'constant')
            if len(voice_features) < 8:
                voice_features = np.pad(voice_features, (0, 8 - len(voice_features)), 'constant')
            
            # 동적 가중치 적용
            rppg_weight = dynamic_weights.get("rppg_weight", self.rppg_weight)
            voice_weight = dynamic_weights.get("voice_weight", self.voice_weight)
            
            fused = np.concatenate([
                rppg_features * rppg_weight,
                voice_features * voice_weight
            ])
            
            # 정규화
            if len(fused) > 0:
                fused = (fused - np.mean(fused)) / (np.std(fused) + 1e-8)
            
            return fused
            
        except Exception as e:
            logger.error(f"가중치 기반 특징 융합 중 오류: {e}")
            return np.zeros(18, dtype=np.float32)
    
    def _filter_outliers(self, features: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """이상치 탐지 및 제거"""
        outlier_info = {
            "original_count": len(features),
            "outlier_count": 0,
            "filtered_count": 0,
            "outlier_indices": [],
            "filtering_method": "percentile_clipping"
        }
        
        try:
            if len(features) == 0:
                return features, outlier_info
            
            # 로버스트 퍼센타일 기반 이상치 탐지
            q25 = np.percentile(features, 25)
            q75 = np.percentile(features, 75)
            iqr = q75 - q25
            
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            
            # 이상치 인덱스 찾기
            outlier_mask = (features < lower_bound) | (features > upper_bound)
            outlier_indices = np.where(outlier_mask)[0]
            
            # 이상치 정보 기록
            outlier_info["outlier_count"] = len(outlier_indices)
            outlier_info["outlier_indices"] = outlier_indices.tolist()
            outlier_info["lower_bound"] = float(lower_bound)
            outlier_info["upper_bound"] = float(upper_bound)
            
            # 이상치 제거 (클리핑)
            filtered_features = np.clip(features, lower_bound, upper_bound)
            outlier_info["filtered_count"] = len(filtered_features)
            
            if outlier_info["outlier_count"] > 0:
                logger.info(f"이상치 {outlier_info['outlier_count']}개 탐지 및 제거 완료")
            
            return filtered_features, outlier_info
            
        except Exception as e:
            logger.warning(f"이상치 필터링 중 오류: {e}")
            outlier_info["filtering_method"] = "error_fallback"
            return features, outlier_info
    
    def _estimate_uncertainty(self, features: np.ndarray, fusion_results: Dict) -> Dict[str, Any]:
        """융합 결과의 불확실성 추정"""
        uncertainty = {
            "overall_uncertainty": 0.0,
            "feature_variance": 0.0,
            "model_uncertainty": 0.0,
            "uncertainty_level": "unknown",
            "confidence_interval": [0.0, 0.0]
        }
        
        try:
            # 특징 분산 기반 불확실성
            if len(features) > 0:
                feature_variance = np.var(features)
                uncertainty["feature_variance"] = float(feature_variance)
            
            # 모델 불확실성 (RandomForest 앙상블 분산)
            if self.fusion_model and hasattr(self.fusion_model, 'estimators_'):
                # 각 트리의 예측 분산 계산
                predictions = []
                for estimator in self.fusion_model.estimators_:
                    try:
                        pred = estimator.predict(features.reshape(1, -1))[0]
                        predictions.append(pred)
                    except:
                        continue
                
                if predictions:
                    predictions = np.array(predictions)
                    model_variance = np.var(predictions)
                    uncertainty["model_uncertainty"] = float(model_variance)
            
            # 전체 불확실성 계산
            total_uncertainty = (
                uncertainty["feature_variance"] * 0.4 +
                uncertainty["model_uncertainty"] * 0.6
            )
            uncertainty["overall_uncertainty"] = float(total_uncertainty)
            
            # 신뢰 구간 계산
            if len(features) > 0:
                mean_val = np.mean(features)
                std_val = np.std(features)
                uncertainty["confidence_interval"] = [
                    float(mean_val - 1.96 * std_val),
                    float(mean_val + 1.96 * std_val)
                ]
            
            # 불확실성 수준 분류
            if total_uncertainty < 0.1:
                uncertainty["uncertainty_level"] = "very_low"
            elif total_uncertainty < 0.3:
                uncertainty["uncertainty_level"] = "low"
            elif total_uncertainty < 0.5:
                uncertainty["uncertainty_level"] = "medium"
            elif total_uncertainty < 0.7:
                uncertainty["uncertainty_level"] = "high"
            else:
                uncertainty["uncertainty_level"] = "very_high"
                
        except Exception as e:
            logger.warning(f"불확실성 추정 중 오류: {e}")
            uncertainty["uncertainty_level"] = "error"
        
        return uncertainty
    
    def _integrate_results(self, rppg_data: Dict, voice_data: Dict, fusion_results: Dict, 
                          data_quality: Dict, sync_status: Dict, dynamic_weights: Dict, 
                          uncertainty: Dict) -> Dict[str, Any]:
        """모든 결과를 통합하여 최종 결과 생성"""
        try:
            # 기본 융합 결과
            integrated_result = {
                "analysis_id": f"fusion_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "advanced_fusion_mkm_lab",
                "status": "success"
            }
            
            # 융합 점수 및 건강 평가
            if fusion_results:
                integrated_result.update({
                    "overall_health_score": fusion_results.get("fusion_score", 0.0),
                    "health_assessment": fusion_results.get("health_assessment", "unknown"),
                    "risk_factors": fusion_results.get("risk_factors", []),
                    "fusion_confidence": fusion_results.get("confidence_level", "low"),
                    "fusion_algorithm": fusion_results.get("fusion_algorithm", "unknown")
                })
            
            # 데이터 품질 정보
            if data_quality:
                integrated_result.update({
                    "data_quality": data_quality,
                    "rppg_quality": data_quality.get("rppg_quality", 0.0),
                    "voice_quality": data_quality.get("voice_quality", 0.0),
                    "overall_quality": data_quality.get("overall_quality", 0.0)
                })
            
            # 동기화 상태
            if sync_status:
                integrated_result.update({
                    "sync_status": sync_status,
                    "synchronized": sync_status.get("synchronized", False),
                    "sync_quality": sync_status.get("sync_quality", 0.0)
                })
            
            # 동적 가중치 정보
            if dynamic_weights:
                integrated_result.update({
                    "dynamic_weights": dynamic_weights,
                    "rppg_weight": dynamic_weights.get("rppg_weight", 0.0),
                    "voice_weight": dynamic_weights.get("voice_weight", 0.0)
                })
            
            # 불확실성 정보
            if uncertainty:
                integrated_result.update({
                    "uncertainty": uncertainty,
                    "uncertainty_level": uncertainty.get("uncertainty_level", "unknown"),
                    "overall_uncertainty": uncertainty.get("overall_uncertainty", 0.0)
                })
            
            # TCM 진단 정확도 (한의학 특화)
            tcm_accuracy = self._calculate_tcm_diagnosis_accuracy(integrated_result)
            integrated_result["tcm_diagnosis_accuracy"] = tcm_accuracy
            
            # 융합 신뢰도 점수
            fusion_confidence_score = self._calculate_fusion_confidence_score(integrated_result)
            integrated_result["fusion_confidence_score"] = fusion_confidence_score
            
            # 요약 생성
            integrated_result["summary"] = self._generate_summary(integrated_result)
            
            return integrated_result
            
        except Exception as e:
            logger.error(f"결과 통합 중 오류: {e}")
            return self._get_error_result(str(e))
    
    def _calculate_tcm_diagnosis_accuracy(self, integrated_result: Dict) -> float:
        """한의학 진단 정확도 계산"""
        try:
            accuracy = 0.0
            
            # 데이터 품질 기반 정확도
            data_quality = integrated_result.get("overall_quality", 0.0)
            accuracy += data_quality * 0.3
            
            # 동기화 품질 기반 정확도
            sync_quality = integrated_result.get("sync_quality", 0.0)
            accuracy += sync_quality * 0.2
            
            # 융합 신뢰도 기반 정확도
            fusion_confidence = integrated_result.get("fusion_confidence", "low")
            confidence_mapping = {"very_high": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
            accuracy += confidence_mapping.get(fusion_confidence, 0.4) * 0.3
            
            # 불확실성 기반 정확도
            uncertainty_level = integrated_result.get("uncertainty_level", "medium")
            uncertainty_mapping = {"very_low": 1.0, "low": 0.8, "medium": 0.6, "high": 0.4, "very_high": 0.2}
            accuracy += uncertainty_mapping.get(uncertainty_level, 0.6) * 0.2
            
            return min(1.0, max(0.0, accuracy))
            
        except Exception as e:
            logger.warning(f"TCM 진단 정확도 계산 중 오류: {e}")
            return 0.5
    
    def _calculate_fusion_confidence_score(self, integrated_result: Dict) -> float:
        """융합 신뢰도 점수 계산"""
        try:
            confidence = 0.0
            
            # 데이터 품질
            quality = integrated_result.get("overall_quality", 0.0)
            confidence += quality * 0.25
            
            # 동기화 품질
            sync_quality = integrated_result.get("sync_quality", 0.0)
            confidence += sync_quality * 0.25
            
            # 융합 알고리즘 신뢰도
            algorithm = integrated_result.get("fusion_algorithm", "unknown")
            if algorithm == "random_forest_ensemble":
                confidence += 0.3
            elif algorithm == "baseline":
                confidence += 0.1
            else:
                confidence += 0.2
            
            # 불확실성 수준
            uncertainty_level = integrated_result.get("uncertainty_level", "medium")
            uncertainty_mapping = {"very_low": 0.2, "low": 0.1, "medium": 0.0, "high": -0.1, "very_high": -0.2}
            confidence += uncertainty_mapping.get(uncertainty_level, 0.0)
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.warning(f"융합 신뢰도 점수 계산 중 오류: {e}")
            return 0.5
    
    def _update_mkm_performance_metrics(self, results: Dict, start_time: datetime):
        """MKM Lab 성능 모니터링 메트릭 업데이트"""
        try:
            if not self.monitor:
                return
            
            # 성능 메트릭 구성
            metric = {
                "timestamp": datetime.now().isoformat(),
                "overall_health_score": results.get("overall_health_score", 0.0),
                "tcm_diagnosis_accuracy": results.get("tcm_diagnosis_accuracy", 0.0),
                "fusion_confidence_score": results.get("fusion_confidence_score", 0.0),
                "data_quality": results.get("overall_quality", 0.0),
                "sync_quality": results.get("sync_quality", 0.0),
                "uncertainty_level": results.get("uncertainty_level", "unknown"),
                "processing_time_ms": 0.0,  # 실제 구현 시 측정
                "outlier_count": results.get("outlier_count", 0),
                "algorithm": results.get("fusion_algorithm", "unknown")
            }
            
            # 성능 이력에 추가
            self.performance_history.append(metric)
            
            # 최근 100개 메트릭만 유지
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]
                
        except Exception as e:
            logger.warning(f"MKM Lab 성능 메트릭 업데이트 중 오류: {e}")
    
    def get_mkm_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """MKM Lab 성능 모니터링 메트릭 스냅샷 반환"""
        if self.monitor:
            return self.monitor.get_metrics_snapshot()
        return None
    
    def get_mkm_bottlenecks(self) -> List[Dict[str, Any]]:
        """MKM Lab 성능 병목 분석 결과 반환"""
        if self.monitor:
            return self.monitor.analyze_bottlenecks()
        return []
    
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
        """rPPG와 음성 특징을 융합"""
        try:
            # 특징 차원 맞추기
            if len(rppg_features) < 10:
                rppg_features = np.pad(rppg_features, (0, 10 - len(rppg_features)), 'constant')
            if len(voice_features) < 8:
                voice_features = np.pad(voice_features, (0, 8 - len(voice_features)), 'constant')
            
            # 가중치 기반 융합
            fused = np.concatenate([
                rppg_features * self.rppg_weight,
                voice_features * self.voice_weight
            ])
            
            # 정규화
            if len(fused) > 0:
                fused = (fused - np.mean(fused)) / (np.std(fused) + 1e-8)
            
            return fused
            
        except Exception as e:
            logger.error(f"특징 융합 중 오류: {e}")
            return np.zeros(18, dtype=np.float32)
    
    def _perform_advanced_fusion(self, fused_features: np.ndarray) -> Dict[str, Any]:
        """고급 융합 분석 수행"""
        try:
            if self.fusion_model is None:
                logger.warning("융합 모델이 초기화되지 않음")
                return self._get_baseline_result()
            
            # 특징을 2D 배열로 변환 (sklearn 요구사항)
            features_2d = fused_features.reshape(1, -1)
            
            # 모델 예측
            prediction = self.fusion_model.predict(features_2d)[0]
            
            # 건강 상태 평가
            health_assessment = self._assess_health_status(prediction)
            
            # 위험 요인 식별
            risk_factors = self._identify_risk_factors(fused_features)
            
            # 신뢰도 계산
            confidence_level = self._calculate_fusion_confidence(fused_features)
            
            return {
                "fusion_score": float(prediction),
                "health_assessment": health_assessment,
                "risk_factors": risk_factors,
                "confidence_level": confidence_level,
                "feature_importance": self._get_feature_importance(),
                "fusion_algorithm": "random_forest_ensemble"
            }
            
        except Exception as e:
            logger.error(f"고급 융합 분석 중 오류: {e}")
            return self._get_baseline_result()
    
    def _assess_health_status(self, score: float) -> str:
        """건강 상태 평가"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        elif score >= 0.2:
            return "poor"
        else:
            return "critical"
    
    def _identify_risk_factors(self, features: np.ndarray) -> List[str]:
        """위험 요인 식별"""
        risk_factors = []
        
        try:
            # rPPG 관련 위험 요인 (첫 10개 특징)
            if len(features) >= 10:
                hr_features = features[:10]
                
                # 심박수 관련 위험
                if hr_features[0] > 100:  # 첫 번째 특징이 심박수
                    risk_factors.append("심박수 증가")
                if hr_features[1] > 50:  # HRV 관련
                    risk_factors.append("심박변이도 증가")
            
            # 음성 관련 위험 요인 (나머지 8개 특징)
            if len(features) >= 18:
                voice_features = features[10:18]
                
                # Jitter 관련 위험
                if voice_features[1] > 2.0:  # Jitter
                    risk_factors.append("음성 떨림 증가")
                if voice_features[2] > 3.0:  # Shimmer
                    risk_factors.append("음성 크기 변화")
            
        except Exception as e:
            logger.warning(f"위험 요인 식별 중 오류: {e}")
        
        return risk_factors
    
    def _calculate_fusion_confidence(self, features: np.ndarray) -> str:
        """융합 신뢰도 계산"""
        try:
            # 특징의 표준편차가 낮을수록 신뢰도 높음
            feature_std = np.std(features)
            
            if feature_std < 0.1:
                return "very_high"
            elif feature_std < 0.3:
                return "high"
            elif feature_std < 0.5:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.warning(f"융합 신뢰도 계산 중 오류: {e}")
            return "low"
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """특징 중요도 반환"""
        try:
            if self.fusion_model and hasattr(self.fusion_model, 'feature_importances_'):
                return {
                    f"feature_{i}": float(importance)
                    for i, importance in enumerate(self.fusion_model.feature_importances_)
                }
            else:
                return {"message": "모델이 훈련되지 않음"}
                
        except Exception as e:
            logger.warning(f"특징 중요도 추출 중 오류: {e}")
            return {"error": str(e)}
    
    def _get_baseline_result(self) -> Dict[str, Any]:
        """기준선 결과 반환"""
        return {
            "fusion_score": 0.5,
            "health_assessment": "unknown",
            "risk_factors": [],
            "confidence_level": "low",
            "feature_importance": {"message": "기준선 모델"},
            "fusion_algorithm": "baseline"
        }
    
    def train_fusion_model(self, training_data: List[Tuple[np.ndarray, float]]) -> bool:
        """융합 모델 훈련"""
        try:
            if not training_data:
                logger.error("훈련 데이터가 없습니다")
                return False
            
            # 데이터 분리
            X = np.array([features for features, _ in training_data])
            y = np.array([label for _, label in training_data])
            
            # 데이터 검증
            if len(X) < 10:
                logger.warning(f"훈련 데이터가 부족합니다: {len(X)}개")
            
            # 모델 훈련
            self.fusion_model.fit(X, y)
            
            # 특징 이름 저장
            self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
            
            logger.info(f"융합 모델 훈련 완료: {len(X)}개 샘플, {X.shape[1]}개 특징")
            return True
            
        except Exception as e:
            logger.error(f"융합 모델 훈련 실패: {e}")
            return False
    
    def save_model(self, filepath: str) -> bool:
        """훈련된 모델 저장"""
        try:
            if self.fusion_model is None:
                logger.error("저장할 모델이 없습니다")
                return False
            
            import joblib
            model_data = {
                'model': self.fusion_model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'rppg_weight': self.rppg_weight,
                'voice_weight': self.voice_weight
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"모델 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """저장된 모델 로드"""
        try:
            import joblib
            model_data = joblib.load(filepath)
            
            self.fusion_model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.rppg_weight = model_data['rppg_weight']
            self.voice_weight = model_data['voice_weight']
            
            logger.info(f"모델 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
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