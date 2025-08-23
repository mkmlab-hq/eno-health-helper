#!/usr/bin/env python3
"""
실제 CMI 데이터와 음성 데이터를 사용한 융합 파이프라인
"""

import numpy as np
import pandas as pd
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import json
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealDataFusionPipeline:
    """실제 데이터를 사용한 융합 파이프라인"""
    
    def __init__(self):
        self.cmi_data_path = "../../kmedi-guardian-seoul-2025/output/analysis/full_scale_clustered_data.parquet"
        self.voice_data_path = None  # 음성 데이터 경로 확인 필요
        self.output_path = "./real_data_fusion_output"
        self.models_path = "./real_data_fusion_output/trained_models"
        self.results_path = "./real_data_fusion_output/training_results"
        
        # 디렉토리 생성
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.results_path, exist_ok=True)
        
        logger.info("실제 데이터 융합 파이프라인 초기화 완료")
    
    def load_cmi_data(self) -> Optional[pd.DataFrame]:
        """실제 CMI 데이터 로드"""
        try:
            logger.info("📊 실제 CMI 데이터 로드 시작")
            
            if not os.path.exists(self.cmi_data_path):
                logger.error(f"CMI 데이터 파일을 찾을 수 없습니다: {self.cmi_data_path}")
                return None
            
            # Parquet 파일 로드
            cmi_data = pd.read_parquet(self.cmi_data_path)
            
            logger.info(f"CMI 데이터 로드 완료: {cmi_data.shape}")
            logger.info(f"컬럼: {list(cmi_data.columns)}")
            
            # 데이터 샘플 확인
            logger.info(f"데이터 샘플:\n{cmi_data.head()}")
            
            return cmi_data
            
        except Exception as e:
            logger.error(f"CMI 데이터 로드 실패: {e}")
            return None
    
    def analyze_cmi_data_structure(self, cmi_data: pd.DataFrame) -> Dict[str, Any]:
        """CMI 데이터 구조 분석"""
        try:
            logger.info("🔍 CMI 데이터 구조 분석 시작")
            
            analysis = {
                'shape': cmi_data.shape,
                'columns': list(cmi_data.columns),
                'dtypes': cmi_data.dtypes.to_dict(),
                'missing_values': cmi_data.isnull().sum().to_dict(),
                'numeric_columns': [],
                'categorical_columns': [],
                'cluster_column': None,
                'sample_data': {}
            }
            
            # 클러스터 컬럼 찾기
            for col in cmi_data.columns:
                if 'cluster' in col.lower() or 'label' in col.lower():
                    analysis['cluster_column'] = col
                    break
            
            # 수치형/범주형 컬럼 분류
            for col in cmi_data.columns:
                if cmi_data[col].dtype in ['int64', 'float64']:
                    analysis['numeric_columns'].append(col)
                else:
                    analysis['categorical_columns'].append(col)
            
            # 샘플 데이터 (처음 3개 행)
            for col in analysis['numeric_columns'][:5]:  # 처음 5개 수치형 컬럼만
                analysis['sample_data'][col] = cmi_data[col].head(3).tolist()
            
            logger.info(f"CMI 데이터 구조 분석 완료:")
            logger.info(f"  - 전체 크기: {analysis['shape']}")
            logger.info(f"  - 클러스터 컬럼: {analysis['cluster_column']}")
            logger.info(f"  - 수치형 컬럼: {len(analysis['numeric_columns'])}개")
            logger.info(f"  - 범주형 컬럼: {len(analysis['categorical_columns'])}개")
            
            return analysis
            
        except Exception as e:
            logger.error(f"CMI 데이터 구조 분석 실패: {e}")
            return {}
    
    def prepare_cmi_features(self, cmi_data: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[np.ndarray]:
        """CMI 데이터에서 특징 추출"""
        try:
            logger.info("🔧 CMI 특징 추출 시작")
            
            # 수치형 컬럼만 선택 (클러스터 컬럼 제외)
            feature_columns = [col for col in analysis['numeric_columns'] 
                             if col != analysis['cluster_column']]
            
            if not feature_columns:
                logger.error("사용 가능한 수치형 특징이 없습니다")
                return None
            
            # 특징 데이터 추출
            features = cmi_data[feature_columns].values
            
            # 결측값 처리 (평균값으로 대체)
            features = np.nan_to_num(features, nan=np.nanmean(features))
            
            logger.info(f"CMI 특징 추출 완료: {features.shape}")
            logger.info(f"사용된 특징: {feature_columns}")
            
            return features
            
        except Exception as e:
            logger.error(f"CMI 특징 추출 실패: {e}")
            return None
    
    def create_voice_features_simulation(self, num_samples: int) -> np.ndarray:
        """음성 특징 시뮬레이션 (실제 음성 데이터가 없는 경우)"""
        try:
            logger.info("🎵 음성 특징 시뮬레이션 시작")
            
            # 실제 음성 데이터가 없으므로 CMI 데이터와 동일한 샘플 수로 시뮬레이션
            # 이는 임시 해결책이며, 실제 음성 데이터가 확보되면 교체해야 함
            
            np.random.seed(42)  # 재현 가능성을 위한 시드 설정
            
            # 음성 특징 (8개 차원)
            voice_features = np.random.normal(0, 1, (num_samples, 8))
            
            # 특징별 의미있는 범위 설정
            voice_features[:, 0] = 150 + np.random.normal(0, 20, num_samples)  # pitch_hz
            voice_features[:, 1] = np.abs(np.random.normal(1.0, 0.3, num_samples))  # jitter_percent
            voice_features[:, 2] = np.abs(np.random.normal(1.0, 0.2, num_samples))  # shimmer_db
            voice_features[:, 3] = 20 + np.random.normal(0, 5, num_samples)  # hnr_db
            voice_features[:, 4] = np.clip(np.random.normal(0.5, 0.2, num_samples), 0.1, 1.0)  # energy
            voice_features[:, 5] = 1.0 + np.random.normal(0, 0.2, num_samples)  # speaking_rate
            voice_features[:, 6] = np.clip(np.random.normal(0.8, 0.2, num_samples), 0.6, 1.0)  # emotion_intensity
            voice_features[:, 7] = np.clip(np.random.normal(0.7, 0.2, num_samples), 0.3, 1.0)  # voice_quality
            
            logger.info(f"음성 특징 시뮬레이션 완료: {voice_features.shape}")
            logger.warning("⚠️ 이는 임시 해결책입니다. 실제 음성 데이터 확보 시 교체 필요")
            
            return voice_features
            
        except Exception as e:
            logger.error(f"음성 특징 시뮬레이션 실패: {e}")
            return None
    
    def fuse_features(self, cmi_features: np.ndarray, voice_features: np.ndarray) -> Optional[np.ndarray]:
        """CMI와 음성 특징 융합"""
        try:
            logger.info("🎯 특징 융합 시작")
            
            if cmi_features.shape[0] != voice_features.shape[0]:
                logger.error(f"샘플 수가 일치하지 않습니다: CMI {cmi_features.shape[0]} vs 음성 {voice_features.shape[0]}")
                return None
            
            # 특징 융합 (수평 연결)
            fused_features = np.hstack([cmi_features, voice_features])
            
            logger.info(f"특징 융합 완료: {fused_features.shape}")
            logger.info(f"  - CMI 특징: {cmi_features.shape[1]}개")
            logger.info(f"  - 음성 특징: {voice_features.shape[1]}개")
            logger.info(f"  - 융합 특징: {fused_features.shape[1]}개")
            
            return fused_features
            
        except Exception as e:
            logger.error(f"특징 융합 실패: {e}")
            return None
    
    def create_labels(self, cmi_data: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[np.ndarray]:
        """라벨 생성 (클러스터 정보 사용)"""
        try:
            logger.info("🏷️ 라벨 생성 시작")
            
            if not analysis['cluster_column']:
                logger.error("클러스터 컬럼을 찾을 수 없습니다")
                return None
            
            # 클러스터 정보를 라벨로 사용
            labels = cmi_data[analysis['cluster_column']].values
            
            # 클러스터 분포 확인
            unique_labels, counts = np.unique(labels, return_counts=True)
            logger.info(f"클러스터 분포:")
            for label, count in zip(unique_labels, counts):
                percentage = (count / len(labels)) * 100
                logger.info(f"  - 클러스터 {label}: {count}개 ({percentage:.2f}%)")
            
            return labels
            
        except Exception as e:
            logger.error(f"라벨 생성 실패: {e}")
            return None
    
    def prepare_training_dataset(self, fused_features: np.ndarray, labels: np.ndarray) -> bool:
        """훈련 데이터셋 준비"""
        try:
            logger.info("📊 훈련 데이터셋 준비 시작")
            
            # 데이터 분할 (70% 훈련, 15% 검증, 15% 테스트)
            X_temp, X_test, y_temp, y_test = train_test_split(
                fused_features, labels, test_size=0.15, random_state=42, stratify=labels
            )
            
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp
            )
            
            logger.info(f"데이터셋 분할 완료:")
            logger.info(f"  - 훈련: {X_train.shape[0]}개 샘플")
            logger.info(f"  - 검증: {X_val.shape[0]}개 샘플")
            logger.info(f"  - 테스트: {X_test.shape[0]}개 샘플")
            
            # 데이터 저장
            dataset_path = os.path.join(self.output_path, "fusion_dataset")
            os.makedirs(dataset_path, exist_ok=True)
            
            np.save(os.path.join(dataset_path, "train_features.npy"), X_train)
            np.save(os.path.join(dataset_path, "train_labels.npy"), y_train)
            np.save(os.path.join(dataset_path, "val_features.npy"), X_val)
            np.save(os.path.join(dataset_path, "val_labels.npy"), y_val)
            np.save(os.path.join(dataset_path, "test_features.npy"), X_test)
            np.save(os.path.join(dataset_path, "test_labels.npy"), y_test)
            
            # 데이터셋 정보 저장
            dataset_info = {
                'total_samples': len(fused_features),
                'training_samples': len(X_train),
                'validation_samples': len(X_val),
                'test_samples': len(X_test),
                'feature_dimension': fused_features.shape[1],
                'created_at': datetime.now().isoformat(),
                'data_type': 'real_cmi_fusion',
                'description': '실제 CMI 데이터와 시뮬레이션된 음성 데이터로 생성된 융합 모델 훈련 데이터셋'
            }
            
            with open(os.path.join(dataset_path, "dataset_info.json"), 'w', encoding='utf-8') as f:
                json.dump(dataset_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"훈련 데이터셋 준비 완료: {dataset_path}")
            return True
            
        except Exception as e:
            logger.error(f"훈련 데이터셋 준비 실패: {e}")
            return False
    
    def run_complete_pipeline(self) -> bool:
        """완전한 융합 파이프라인 실행"""
        try:
            logger.info("🚀 실제 데이터 융합 파이프라인 시작")
            
            # 1단계: CMI 데이터 로드
            cmi_data = self.load_cmi_data()
            if cmi_data is None:
                return False
            
            # 2단계: CMI 데이터 구조 분석
            analysis = self.analyze_cmi_data_structure(cmi_data)
            if not analysis:
                return False
            
            # 3단계: CMI 특징 추출
            cmi_features = self.prepare_cmi_features(cmi_data, analysis)
            if cmi_features is None:
                return False
            
            # 4단계: 음성 특징 생성 (시뮬레이션)
            voice_features = self.create_voice_features_simulation(cmi_features.shape[0])
            if voice_features is None:
                return False
            
            # 5단계: 특징 융합
            fused_features = self.fuse_features(cmi_features, voice_features)
            if fused_features is None:
                return False
            
            # 6단계: 라벨 생성
            labels = self.create_labels(cmi_data, analysis)
            if labels is None:
                return False
            
            # 7단계: 훈련 데이터셋 준비
            if not self.prepare_training_dataset(fused_features, labels):
                return False
            
            logger.info("🎉 실제 데이터 융합 파이프라인 완료!")
            return True
            
        except Exception as e:
            logger.error(f"융합 파이프라인 실행 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    try:
        logger.info("🎯 실제 데이터 융합 파이프라인 시작")
        
        # 파이프라인 초기화
        pipeline = RealDataFusionPipeline()
        
        # 완전한 파이프라인 실행
        success = pipeline.run_complete_pipeline()
        
        if success:
            logger.info("🎉 실제 데이터 융합 파이프라인 성공!")
            print("\n" + "="*60)
            print("🎉 실제 데이터 융합 파이프라인 성공!")
            print("="*60)
            print("✅ 실제 CMI 데이터 로드 및 분석 완료")
            print("✅ CMI-음성 특징 융합 완료")
            print("✅ 훈련 데이터셋 생성 완료")
            print("✅ '트윈 엔진' 실제 데이터 파이프라인 구축 완료!")
            print("="*60)
        else:
            logger.error("❌ 실제 데이터 융합 파이프라인 실패")
            print("\n" + "="*60)
            print("❌ 파이프라인 실패 - 문제를 파악하고 수정해주세요.")
            print("="*60)
        
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")
        print(f"\n❌ 실행 오류: {e}")

if __name__ == "__main__":
    main()
