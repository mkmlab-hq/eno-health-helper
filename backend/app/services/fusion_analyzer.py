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
		
		# 동기화 설정
		self.sync_tolerance_ms = 120  # rPPG-음성 타임스탬프 허용 오차
		
		# 이상치 제거 설정
		self.outlier_z_threshold = 3.0
		self.robust_percentile_low = 2.5
		self.robust_percentile_high = 97.5
		
		# 성능 메트릭 저장
		self.performance_history = []
		
		# 모델 초기화
		self._initialize_fusion_model()
		
		logger.info("고급 rPPG-음성 융합 분석 엔진 초기화 완료")
	
	def _initialize_fusion_model(self):
		"""융합 머신러닝 모델 초기화"""
		try:
			self.fusion_model = RandomForestRegressor(
				n_estimators=300,
				max_depth=12,
				random_state=42,
				n_jobs=-1,
				min_samples_leaf=2
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
		rPPG-음성 융합 분석 메인 파이프라인
		
		Args:
			rppg_data: rPPG 분석 결과
			voice_data: 음성 분석 결과
			video_frames: 원본 비디오 프레임 (선택적)
			audio_signal: 원본 오디오 신호 (선택적)
			
		Returns:
			융합 분석 결과
		"""
		import asyncio
		try:
			logger.info("rPPG-음성 융합 분석 시작")
			# 0단계: 시간 동기화 검증 및 정렬
			sync_info = await asyncio.to_thread(self._synchronize_modalities, rppg_data, voice_data)
			# 1단계: 데이터 품질 검증
			data_quality = await asyncio.to_thread(self._validate_data_quality, rppg_data, voice_data)
			# 2단계: 특징 추출 및 정규화
			rppg_features = await asyncio.to_thread(self._extract_rppg_features, rppg_data, video_frames)
			voice_features = await asyncio.to_thread(self._extract_voice_features, voice_data, audio_signal)
			# 2.5단계: 이상치 탐지 및 제거(클리핑/로버스트 스케일링)
			rppg_features, voice_features, outlier_stats = await asyncio.to_thread(
				self._filter_outliers, rppg_features, voice_features
			)
			# 3단계: 동적 신뢰도 가중치 계산
			dynamic_weights = await asyncio.to_thread(
				self._compute_dynamic_weights, rppg_data, voice_data, rppg_features, voice_features, data_quality, sync_info
			)
			# 3.5단계: 특징 융합
			fused_features = await asyncio.to_thread(
				self._fuse_features, rppg_features, voice_features, dynamic_weights
			)
			# 4단계: 고급 융합 분석
			fusion_results = await asyncio.to_thread(self._perform_advanced_fusion, fused_features)
			# 4.5단계: 불확실성 추정
			uncertainty = await asyncio.to_thread(self._estimate_uncertainty, fused_features)
			# 5단계: 결과 통합 및 검증
			final_results = await asyncio.to_thread(
				self._integrate_results, rppg_data, voice_data, fusion_results, data_quality, dynamic_weights, sync_info, outlier_stats, uncertainty
			)
			# 6단계: 성능 메트릭 업데이트
			await asyncio.to_thread(self._update_performance_metrics, final_results)
			logger.info("rPPG-음성 융합 분석 완료")
			return final_results
		except Exception as e:
			logger.error(f"융합 분석 실패: {e}")
			return self._get_error_result(str(e))
	
	def _synchronize_modalities(self, rppg_data: Dict[str, Any], voice_data: Dict[str, Any]) -> Dict[str, Any]:
		"""rPPG와 음성 데이터의 타임스탬프 동기화 상태 평가 및 정렬 정보 생성"""
		try:
			rppg_ts = self._extract_timestamp(rppg_data)
			voice_ts = self._extract_timestamp(voice_data)
			time_diff_ms = None
			sync_ok = False
			if rppg_ts and voice_ts:
				time_diff_ms = abs((rppg_ts - voice_ts).total_seconds() * 1000.0)
				sync_ok = time_diff_ms <= self.sync_tolerance_ms
			return {
				"rppg_timestamp": rppg_ts.isoformat() if rppg_ts else None,
				"voice_timestamp": voice_ts.isoformat() if voice_ts else None,
				"time_diff_ms": time_diff_ms,
				"sync_ok": sync_ok
			}
		except Exception as e:
			logger.warning(f"동기화 정보 계산 중 오류: {e}")
			return {"rppg_timestamp": None, "voice_timestamp": None, "time_diff_ms": None, "sync_ok": False}
	
	def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
		try:
			if not data:
				return None
			ts_str = data.get("timestamp") or data.get("analysis_timestamp")
			if not ts_str:
				return None
			return datetime.fromisoformat(ts_str)
		except Exception:
			return None
	
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
			if voice_data and ('jitter_percent' in voice_data or 'jitter' in voice_data):
				jitter = voice_data.get('jitter_percent', voice_data.get('jitter', 0.0))
				if jitter < 2.0:  # 우수한 음성 품질
					quality_metrics['voice_quality'] = 1.0
				elif jitter < 5.0:  # 보통 품질
					quality_metrics['voice_quality'] = 0.7
				else:
					quality_metrics['voice_quality'] = 0.4
			
			# 전체 품질 점수 (초기 가중치 기반)
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
			# 기본 음성 특징 (voice_analyzer와 키 호환)
			if 'pitch_hz' in voice_data or 'f0' in voice_data:
				features.append(voice_data.get('pitch_hz', voice_data.get('f0', 0.0)))
			if 'jitter_percent' in voice_data or 'jitter' in voice_data:
				features.append(voice_data.get('jitter_percent', voice_data.get('jitter', 0.0)))
			if 'shimmer_db' in voice_data or 'shimmer' in voice_data:
				features.append(voice_data.get('shimmer_db', voice_data.get('shimmer', 0.0)))
			if 'hnr_db' in voice_data or 'hnr' in voice_data:
				features.append(voice_data.get('hnr_db', voice_data.get('hnr', 0.0)))
			
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
	
	def _filter_outliers(self, rppg_features: np.ndarray, voice_features: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
		"""로버스트한 이상치 제거/클리핑으로 특징 안정화"""
		try:
			stats = {}
			def _clip_robust(x: np.ndarray, prefix: str) -> np.ndarray:
				if x.size == 0:
					return x
				low = np.percentile(x, self.robust_percentile_low)
				high = np.percentile(x, self.robust_percentile_high)
				stats[f"{prefix}_low"] = float(low)
				stats[f"{prefix}_high"] = float(high)
				return np.clip(x, low, high)
			rppg_clipped = _clip_robust(rppg_features, "rppg")
			voice_clipped = _clip_robust(voice_features, "voice")
			return rppg_clipped.astype(np.float32), voice_clipped.astype(np.float32), stats
		except Exception as e:
			logger.warning(f"이상치 필터링 실패: {e}")
			return rppg_features, voice_features, {"error": str(e)}
	
	def _compute_dynamic_weights(
		self,
		rppg_data: Dict[str, Any],
		voice_data: Dict[str, Any],
		rppg_features: np.ndarray,
		voice_features: np.ndarray,
		quality: Dict[str, Any],
		sync_info: Dict[str, Any]
	) -> Dict[str, float]:
		"""모달리티 신뢰도와 동기화 상태를 반영한 동적 가중치 계산"""
		try:
			# 기본 신뢰도는 품질 메트릭에서 시작
			rppg_conf = float(quality.get('rppg_quality', 0.5))
			voice_conf = float(quality.get('voice_quality', 0.5))
			# 추가 신뢰도: 내부 일관성(표준편차 기반)과 값의 유효성
			rppg_stability = 1.0 / (np.std(rppg_features) + 1e-6)
			voice_stability = 1.0 / (np.std(voice_features) + 1e-6)
			rppg_conf *= min(1.5, max(0.5, rppg_stability))
			voice_conf *= min(1.5, max(0.5, voice_stability))
			# 동기화 패널티
			if not sync_info.get('sync_ok', True):
				# 시간 차이가 크면 음성의 가중을 더 낮추는 예
				voice_conf *= 0.8
				rppg_conf *= 0.9
			# 정규화
			total = rppg_conf + voice_conf + 1e-8
			return {
				"rppg_weight": float(rppg_conf / total),
				"voice_weight": float(voice_conf / total)
			}
		except Exception as e:
			logger.warning(f"동적 가중치 계산 실패: {e}")
			# 실패 시 기본 가중치 복원
			return {"rppg_weight": self.rppg_weight, "voice_weight": self.voice_weight}
	
	def _fuse_features(self, rppg_features: np.ndarray, voice_features: np.ndarray, dynamic_weights: Optional[Dict[str, float]] = None) -> np.ndarray:
		"""rPPG와 음성 특징을 융합"""
		try:
			# 특징 차원 맞추기
			if len(rppg_features) < 10:
				rppg_features = np.pad(rppg_features, (0, 10 - len(rppg_features)), 'constant')
			if len(voice_features) < 8:
				voice_features = np.pad(voice_features, (0, 8 - len(voice_features)), 'constant')
			
			# 가중치 선택
			w = dynamic_weights or {"rppg_weight": self.rppg_weight, "voice_weight": self.voice_weight}
			wr = float(w.get("rppg_weight", self.rppg_weight))
			wv = float(w.get("voice_weight", self.voice_weight))
			
			# 가중치 기반 융합
			fused = np.concatenate([
				rppg_features * wr,
				voice_features * wv
			])
			
			# 정규화
			if len(fused) > 0:
				fused = (fused - np.mean(fused)) / (np.std(fused) + 1e-8)
			
			return fused.astype(np.float32)
			
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
			prediction = float(self.fusion_model.predict(features_2d)[0])
			
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
	
	def _estimate_uncertainty(self, fused_features: np.ndarray) -> Dict[str, Any]:
		"""랜덤 포레스트 앙상블 분산 기반 불확실성 추정 및 피처 불확실성 요약"""
		try:
			if self.fusion_model is None or not hasattr(self.fusion_model, 'estimators_'):
				return {"prediction_variance": None, "aleatoric_proxy": None}
			features_2d = fused_features.reshape(1, -1)
			# 트리별 예측 분산
			per_tree_preds = np.array([est.predict(features_2d)[0] for est in self.fusion_model.estimators_], dtype=np.float32)
			pred_var = float(np.var(per_tree_preds))
			# 단순 대리치로 입력 표준편차를 사용 (feature noise proxy)
			aleatoric_proxy = float(np.std(fused_features))
			return {"prediction_variance": pred_var, "aleatoric_proxy": aleatoric_proxy}
		except Exception as e:
			logger.warning(f"불확실성 추정 실패: {e}")
			return {"prediction_variance": None, "aleatoric_proxy": None, "error": str(e)}
	
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
				"processing_time": results.get("processing_time_ms", 0.0),
				"sync_ok": results.get("synchronization", {}).get("sync_ok", None),
				"prediction_variance": results.get("uncertainty", {}).get("prediction_variance", None)
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
			if voice_data and ('jitter_percent' in voice_data or 'jitter' in voice_data):
				jitter = voice_data.get('jitter_percent', voice_data.get('jitter', 10.0))
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
	
	def _integrate_results(
		self,
		rppg_data: Dict[str, Any],
		voice_data: Dict[str, Any],
		fusion_results: Dict[str, Any],
		data_quality: Dict[str, Any],
		dynamic_weights: Dict[str, float],
		sync_info: Dict[str, Any],
		outlier_stats: Dict[str, Any],
		uncertainty: Dict[str, Any]
	) -> Dict[str, Any]:
		"""최종 결과 통합 및 메타데이터 포함"""
		try:
			fusion_score = float(fusion_results.get("fusion_score", 0.5))
			overall_health_score = float(
				fusion_score
			)
			result = {
				"overall_health_score": overall_health_score,
				"fusion": fusion_results,
				"data_quality": data_quality,
				"weights": dynamic_weights,
				"synchronization": sync_info,
				"outlier_filtering": outlier_stats,
				"uncertainty": uncertainty,
				"summary": self._generate_summary(fusion_results, data_quality),
				"timestamp": datetime.utcnow().isoformat(),
				"processing_time_ms": 0.0
			}
			return result
		except Exception as e:
			logger.warning(f"결과 통합 실패: {e}")
			return self._get_error_result(str(e))
	
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
			
			scores = [m.get("overall_score", 0.0) for m in self.performance_history]
			qualities = [m.get("data_quality", 0.0) for m in self.performance_history]
			variances = [m.get("prediction_variance") for m in self.performance_history if m.get("prediction_variance") is not None]
			
			return {
				"total_analyses": len(self.performance_history),
				"average_score": float(np.mean(scores)) if scores else None,
				"average_quality": float(np.mean(qualities)) if qualities else None,
				"score_std": float(np.std(scores)) if scores else None,
				"quality_std": float(np.std(qualities)) if qualities else None,
				"avg_prediction_variance": float(np.mean(variances)) if variances else None,
				"recent_trend": "stable"  # 실제 구현 시 트렌드 분석
			}
			
		except Exception as e:
			logger.error(f"성능 요약 생성 중 오류: {e}")
			return {"error": str(e)} 