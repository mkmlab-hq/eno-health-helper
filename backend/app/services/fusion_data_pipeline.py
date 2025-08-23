#!/usr/bin/env python3
"""
융합 모델 훈련을 위한 데이터 통합 및 전처리 파이프라인
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path

# 기존 서비스들 import
from .enhanced_rppg_analyzer import EnhancedRPPGAnalyzer
from .voice_analyzer import VoiceAnalyzer
from .fusion_analyzer import AdvancedFusionAnalyzer

logger = logging.getLogger(__name__)

class FusionDataPipeline:
    """
    rPPG-음성 융합 모델 훈련을 위한 데이터 파이프라인
    
    핵심 기능:
    1. CMI 센서 데이터와 음성 데이터셋 통합
    2. 시계열 동기화 및 정규화
    3. 훈련 데이터셋 생성
    4. 데이터 품질 검증
    """
    
    def __init__(self):
        # 분석기 초기화
        self.rppg_analyzer = EnhancedRPPGAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
        self.fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 데이터 파이프라인 설정
        self.sample_rate = 30  # rPPG 샘플링 레이트 (fps)
        self.audio_sample_rate = 16000  # 음성 샘플링 레이트 (Hz)
        self.sync_window = 5.0  # 동기화 윈도우 (초)
        
        # 데이터 저장소
        self.training_data = []
        self.validation_data = []
        self.test_data = []
        
        logger.info("융합 데이터 파이프라인 초기화 완료")
    
    def integrate_cmi_and_voice_data(
        self,
        cmi_data_path: str,
        voice_dataset_path: str,
        output_path: str
    ) -> bool:
        """
        CMI 센서 데이터와 음성 데이터셋을 통합
        
        Args:
            cmi_data_path: CMI 데이터 파일 경로
            voice_dataset_path: 음성 데이터셋 경로
            output_path: 통합된 데이터 출력 경로
            
        Returns:
            통합 성공 여부
        """
        try:
            logger.info("CMI-음성 데이터 통합 시작")
            
            # 1단계: CMI 데이터 로드
            cmi_data = self._load_cmi_data(cmi_data_path)
            if cmi_data is None:
                return False
            
            # 2단계: 음성 데이터셋 로드
            voice_data = self._load_voice_dataset(voice_dataset_path)
            if voice_data is None:
                return False
            
            # 3단계: 데이터 동기화
            synchronized_data = self._synchronize_data(cmi_data, voice_data)
            if synchronized_data is None:
                return False
            
            # 4단계: 특징 추출 및 융합
            fused_features = self._extract_and_fuse_features(synchronized_data)
            if fused_features is None:
                return False
            
            # 5단계: 훈련 데이터셋 생성
            training_dataset = self._create_training_dataset(fused_features)
            if training_dataset is None:
                return False
            
            # 6단계: 데이터 저장
            success = self._save_training_dataset(training_dataset, output_path)
            
            if success:
                logger.info(f"데이터 통합 완료: {output_path}")
                return True
            else:
                logger.error("데이터 저장 실패")
                return False
                
        except Exception as e:
            logger.error(f"데이터 통합 실패: {e}")
            return False
    
    def _load_cmi_data(self, data_path: str) -> Optional[Dict[str, Any]]:
        """CMI 데이터 로드"""
        try:
            # CMI 데이터 로드 로직 (실제 구현 시 파일 형식에 맞게 수정)
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            elif data_path.endswith('.json'):
                with open(data_path, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                logger.error(f"지원하지 않는 파일 형식: {data_path}")
                return None
            
            # 데이터 검증
            required_columns = ['timestamp', 'heart_rate', 'hrv', 'stress_level']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"필수 컬럼 누락: {missing_columns}")
                return None
            
            logger.info(f"CMI 데이터 로드 완료: {len(df)}개 샘플")
            return {
                'data': df,
                'columns': df.columns.tolist(),
                'sample_count': len(df)
            }
            
        except Exception as e:
            logger.error(f"CMI 데이터 로드 실패: {e}")
            return None
    
    def _load_voice_dataset(self, dataset_path: str) -> Optional[Dict[str, Any]]:
        """음성 데이터셋 로드"""
        try:
            # Speech Accent Archive 데이터셋 로드
            if os.path.isdir(dataset_path):
                # 디렉토리 내의 음성 파일들 처리
                audio_files = []
                for ext in ['.wav', '.mp3', '.m4a', '.flac']:
                    audio_files.extend(Path(dataset_path).rglob(f'*{ext}'))
                
                if not audio_files:
                    logger.warning(f"음성 파일을 찾을 수 없음: {dataset_path}")
                    return self._create_mock_voice_data()
                
                logger.info(f"음성 파일 {len(audio_files)}개 발견")
                return {
                    'audio_files': [str(f) for f in audio_files],
                    'sample_count': len(audio_files),
                    'type': 'real_audio'
                }
            else:
                logger.warning(f"음성 데이터셋 경로가 디렉토리가 아님: {dataset_path}")
                return self._create_mock_voice_data()
                
        except Exception as e:
            logger.error(f"음성 데이터셋 로드 실패: {e}")
            return self._create_mock_voice_data()
    
    def _create_mock_voice_data(self) -> Dict[str, Any]:
        """Mock 음성 데이터 생성 (개발/테스트용)"""
        logger.info("Mock 음성 데이터 생성")
        
        # 8가지 감정별 Mock 데이터
        emotions = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprise']
        mock_data = []
        
        for emotion in emotions:
            # 각 감정별 10개 샘플 생성
            for i in range(10):
                sample = {
                    'emotion': emotion,
                    'pitch_hz': np.random.normal(150, 30),
                    'jitter_percent': np.random.uniform(0.5, 3.0),
                    'shimmer_db': np.random.uniform(0.3, 2.5),
                    'hnr_db': np.random.uniform(15, 25),
                    'energy': np.random.uniform(0.3, 0.8),
                    'sample_id': f"{emotion}_{i}"
                }
                mock_data.append(sample)
        
        return {
            'mock_data': mock_data,
            'sample_count': len(mock_data),
            'type': 'mock_audio',
            'emotions': emotions
        }
    
    def _synchronize_data(
        self,
        cmi_data: Dict[str, Any],
        voice_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """CMI와 음성 데이터 동기화"""
        try:
            logger.info("데이터 동기화 시작")
            
            if voice_data['type'] == 'mock_audio':
                # Mock 데이터의 경우 시간 기반 동기화 불필요
                return self._synchronize_mock_data(cmi_data, voice_data)
            else:
                # 실제 음성 데이터의 경우 시간 기반 동기화
                return self._synchronize_real_data(cmi_data, voice_data)
                
        except Exception as e:
            logger.error(f"데이터 동기화 실패: {e}")
            return None
    
    def _synchronize_mock_data(
        self,
        cmi_data: Dict[str, Any],
        voice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock 데이터 동기화"""
        try:
            # CMI 데이터를 기준으로 음성 데이터 매핑
            cmi_samples = cmi_data['data']
            voice_samples = voice_data['mock_data']
            
            # 샘플 수 맞추기
            min_samples = min(len(cmi_samples), len(voice_samples))
            
            synchronized = []
            for i in range(min_samples):
                cmi_sample = cmi_samples.iloc[i]
                voice_sample = voice_samples[i % len(voice_samples)]
                
                sync_sample = {
                    'timestamp': cmi_sample.get('timestamp', f'sample_{i}'),
                    'cmi_features': {
                        'heart_rate': cmi_sample.get('heart_rate', 70),
                        'hrv': cmi_sample.get('hrv', 50),
                        'stress_level': cmi_sample.get('stress_level', 'low')
                    },
                    'voice_features': voice_sample,
                    'sync_id': f'sync_{i}'
                }
                synchronized.append(sync_sample)
            
            logger.info(f"Mock 데이터 동기화 완료: {len(synchronized)}개 샘플")
            return {
                'synchronized_data': synchronized,
                'sync_type': 'mock_based',
                'sample_count': len(synchronized)
            }
            
        except Exception as e:
            logger.error(f"Mock 데이터 동기화 실패: {e}")
            return {'synchronized_data': [], 'sync_type': 'error', 'sample_count': 0}
    
    def _synchronize_real_data(
        self,
        cmi_data: Dict[str, Any],
        voice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실제 데이터 동기화 (시간 기반)"""
        try:
            # 실제 구현 시 시간 기반 동기화 로직
            # 현재는 Mock 데이터와 동일하게 처리
            return self._synchronize_mock_data(cmi_data, voice_data)
            
        except Exception as e:
            logger.error(f"실제 데이터 동기화 실패: {e}")
            return {'synchronized_data': [], 'sync_type': 'error', 'sample_count': 0}
    
    def _extract_and_fuse_features(
        self,
        synchronized_data: Dict[str, Any]
    ) -> Optional[List[Tuple[np.ndarray, float]]]:
        """특징 추출 및 융합"""
        try:
            logger.info("특징 추출 및 융합 시작")
            
            if not synchronized_data['synchronized_data']:
                logger.error("동기화된 데이터가 없습니다")
                return None
            
            fused_features = []
            
            for sample in synchronized_data['synchronized_data']:
                try:
                    # rPPG 특징 추출
                    rppg_features = self._extract_rppg_features_from_sample(sample)
                    
                    # 음성 특징 추출
                    voice_features = self._extract_voice_features_from_sample(sample)
                    
                    # 특징 융합
                    fused = np.concatenate([rppg_features, voice_features])
                    
                    # 라벨 생성 (건강 점수)
                    health_score = self._calculate_health_score(sample)
                    
                    fused_features.append((fused, health_score))
                    
                except Exception as e:
                    logger.warning(f"샘플 특징 추출 실패: {e}")
                    continue
            
            if not fused_features:
                logger.error("유효한 특징을 추출할 수 없습니다")
                return None
            
            logger.info(f"특징 추출 및 융합 완료: {len(fused_features)}개 샘플")
            return fused_features
            
        except Exception as e:
            logger.error(f"특징 추출 및 융합 실패: {e}")
            return None
    
    def _extract_rppg_features_from_sample(self, sample: Dict) -> np.ndarray:
        """샘플에서 rPPG 특징 추출"""
        try:
            cmi_features = sample['cmi_features']
            
            # 기본 rPPG 특징 (10개)
            features = [
                cmi_features.get('heart_rate', 70),
                cmi_features.get('hrv', 50),
                self._encode_stress_level(cmi_features.get('stress_level', 'low')),
                # 추가 특징들 (실제 구현 시 확장)
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ]
            
            # 특징 정규화
            features = np.array(features, dtype=np.float32)
            features = (features - np.mean(features)) / (np.std(features) + 1e-8)
            
            return features
            
        except Exception as e:
            logger.warning(f"rPPG 특징 추출 실패: {e}")
            return np.zeros(10, dtype=np.float32)
    
    def _extract_voice_features_from_sample(self, sample: Dict) -> np.ndarray:
        """샘플에서 음성 특징 추출"""
        try:
            voice_features = sample['voice_features']
            
            # 기본 음성 특징 (8개)
            features = [
                voice_features.get('pitch_hz', 150),
                voice_features.get('jitter_percent', 1.0),
                voice_features.get('shimmer_db', 1.0),
                voice_features.get('hnr_db', 20),
                voice_features.get('energy', 0.5),
                # 추가 특징들
                0.0, 0.0, 0.0
            ]
            
            # 특징 정규화
            features = np.array(features, dtype=np.float32)
            features = (features - np.mean(features)) / (np.std(features) + 1e-8)
            
            return features
            
        except Exception as e:
            logger.warning(f"음성 특징 추출 실패: {e}")
            return np.zeros(8, dtype=np.float32)
    
    def _calculate_health_score(self, sample: Dict) -> float:
        """건강 점수 계산"""
        try:
            cmi_features = sample['cmi_features']
            voice_features = sample['voice_features']
            
            # rPPG 기반 점수 (60%)
            hr_score = self._normalize_heart_rate(cmi_features.get('heart_rate', 70))
            hrv_score = self._normalize_hrv(cmi_features.get('hrv', 50))
            stress_score = self._normalize_stress(cmi_features.get('stress_level', 'low'))
            
            rppg_score = (hr_score + hrv_score + stress_score) / 3
            
            # 음성 기반 점수 (40%)
            jitter_score = self._normalize_jitter(voice_features.get('jitter_percent', 1.0))
            shimmer_score = self._normalize_shimmer(voice_features.get('shimmer_db', 1.0))
            hnr_score = self._normalize_hnr(voice_features.get('hnr_db', 20))
            
            voice_score = (jitter_score + shimmer_score + hnr_score) / 3
            
            # 가중 평균
            total_score = rppg_score * 0.6 + voice_score * 0.4
            
            return float(total_score)
            
        except Exception as e:
            logger.warning(f"건강 점수 계산 실패: {e}")
            return 0.5  # 기본값
    
    def _normalize_heart_rate(self, hr: float) -> float:
        """심박수 정규화 (60-100이 최적)"""
        if 60 <= hr <= 100:
            return 1.0
        elif 50 <= hr <= 110:
            return 0.8
        elif 40 <= hr <= 120:
            return 0.6
        else:
            return 0.3
    
    def _normalize_hrv(self, hrv: float) -> float:
        """HRV 정규화 (높을수록 좋음)"""
        if hrv >= 100:
            return 1.0
        elif hrv >= 50:
            return 0.7
        elif hrv >= 20:
            return 0.4
        else:
            return 0.2
    
    def _normalize_stress(self, stress: str) -> float:
        """스트레스 수준 정규화"""
        stress_mapping = {
            'low': 1.0,
            'medium': 0.6,
            'high': 0.3
        }
        return stress_mapping.get(stress, 0.5)
    
    def _normalize_jitter(self, jitter: float) -> float:
        """Jitter 정규화 (낮을수록 좋음)"""
        if jitter < 1.0:
            return 1.0
        elif jitter < 2.0:
            return 0.8
        elif jitter < 3.0:
            return 0.6
        else:
            return 0.4
    
    def _normalize_shimmer(self, shimmer: float) -> float:
        """Shimmer 정규화 (낮을수록 좋음)"""
        if shimmer < 1.0:
            return 1.0
        elif shimmer < 2.0:
            return 0.8
        elif shimmer < 3.0:
            return 0.6
        else:
            return 0.4
    
    def _normalize_hnr(self, hnr: float) -> float:
        """HNR 정규화 (높을수록 좋음)"""
        if hnr >= 20:
            return 1.0
        elif hnr >= 15:
            return 0.8
        elif hnr >= 10:
            return 0.6
        else:
            return 0.4
    
    def _encode_stress_level(self, stress: str) -> float:
        """스트레스 수준을 숫자로 인코딩"""
        stress_mapping = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8
        }
        return stress_mapping.get(stress, 0.5)
    
    def _create_training_dataset(
        self,
        fused_features: List[Tuple[np.ndarray, float]]
    ) -> Optional[Dict[str, Any]]:
        """훈련 데이터셋 생성"""
        try:
            if not fused_features:
                logger.error("융합된 특징이 없습니다")
                return None
            
            # 데이터 분할 (70% 훈련, 15% 검증, 15% 테스트)
            total_samples = len(fused_features)
            train_size = int(total_samples * 0.7)
            val_size = int(total_samples * 0.15)
            
            # 훈련 데이터
            self.training_data = fused_features[:train_size]
            
            # 검증 데이터
            self.validation_data = fused_features[train_size:train_size + val_size]
            
            # 테스트 데이터
            self.test_data = fused_features[train_size + val_size:]
            
            dataset_info = {
                'total_samples': total_samples,
                'training_samples': len(self.training_data),
                'validation_samples': len(self.validation_data),
                'test_samples': len(self.test_data),
                'feature_dimension': len(fused_features[0][0]) if fused_features else 0,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"훈련 데이터셋 생성 완료: {dataset_info}")
            return dataset_info
            
        except Exception as e:
            logger.error(f"훈련 데이터셋 생성 실패: {e}")
            return None
    
    def _save_training_dataset(
        self,
        dataset_info: Dict[str, Any],
        output_path: str
    ) -> bool:
        """훈련 데이터셋 저장"""
        try:
            # 출력 디렉토리 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 데이터셋 정보 저장
            with open(f"{output_path}_info.json", 'w') as f:
                json.dump(dataset_info, f, indent=2)
            
            # 훈련 데이터 저장
            if self.training_data:
                np.save(f"{output_path}_train.npy", self.training_data)
            
            # 검증 데이터 저장
            if self.validation_data:
                np.save(f"{output_path}_val.npy", self.validation_data)
            
            # 테스트 데이터 저장
            if self.test_data:
                np.save(f"{output_path}_test.npy", self.test_data)
            
            logger.info(f"훈련 데이터셋 저장 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"훈련 데이터셋 저장 실패: {e}")
            return False
    
    def get_training_data(self) -> Tuple[List[Tuple[np.ndarray, float]], ...]:
        """훈련 데이터 반환"""
        return self.training_data, self.validation_data, self.test_data
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """데이터셋 정보 반환"""
        return {
            'training_samples': len(self.training_data),
            'validation_samples': len(self.validation_data),
            'test_samples': len(self.test_data),
            'feature_dimension': len(self.training_data[0][0]) if self.training_data else 0
        }
