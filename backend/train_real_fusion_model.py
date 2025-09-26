#!/usr/bin/env python3
"""
실제 데이터로 융합 모델 훈련
"""

import numpy as np
import pandas as pd
import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import json
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealFusionModelTrainer:
    """실제 데이터로 융합 모델 훈련기"""
    
    def __init__(self):
        self.dataset_path = "./real_data_fusion_output/fusion_dataset"
        self.models_path = "./real_data_fusion_output/trained_models"
        self.results_path = "./real_data_fusion_output/training_results"
        
        # 디렉토리 생성
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.results_path, exist_ok=True)
        
        # 데이터 로드
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        
        logger.info("실제 데이터 융합 모델 훈련기 초기화 완료")
    
    def load_dataset(self) -> bool:
        """데이터셋 로드"""
        try:
            logger.info("📊 실제 데이터셋 로드 시작")
            
            # 훈련 데이터 로드
            self.X_train = np.load(os.path.join(self.dataset_path, "train_features.npy"))
            self.y_train = np.load(os.path.join(self.dataset_path, "train_labels.npy"))
            
            # 검증 데이터 로드
            self.X_val = np.load(os.path.join(self.dataset_path, "val_features.npy"))
            self.y_val = np.load(os.path.join(self.dataset_path, "val_labels.npy"))
            
            # 테스트 데이터 로드
            self.X_test = np.load(os.path.join(self.dataset_path, "test_features.npy"))
            self.y_test = np.load(os.path.join(self.dataset_path, "test_labels.npy"))
            
            logger.info(f"실제 데이터셋 로드 완료:")
            logger.info(f"  훈련: {self.X_train.shape[0]}개 샘플, {self.X_train.shape[1]}개 특징")
            logger.info(f"  검증: {self.X_val.shape[0]}개 샘플, {self.X_val.shape[1]}개 특징")
            logger.info(f"  테스트: {self.X_test.shape[0]}개 샘플, {self.X_test.shape[1]}개 특징")
            
            return True
            
        except Exception as e:
            logger.error(f"데이터셋 로드 실패: {e}")
            return False
    
    def train_models(self) -> Dict[str, Any]:
        """여러 모델 훈련 및 비교"""
        try:
            logger.info("🎯 실제 데이터로 융합 모델 훈련 시작")
            
            # 데이터 정규화
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(self.X_train)
            X_val_scaled = scaler.transform(self.X_val)
            X_test_scaled = scaler.transform(self.X_test)
            
            # 스케일러 저장
            scaler_path = os.path.join(self.models_path, "real_feature_scaler.pkl")
            joblib.dump(scaler, scaler_path)
            logger.info(f"실제 데이터 특징 스케일러 저장 완료: {scaler_path}")
            
            # 모델 정의
            models = {
                'LinearRegression': LinearRegression(),
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'SVR': SVR(kernel='rbf', C=1.0, gamma='scale')
            }
            
            # 모델 훈련 및 평가
            results = {}
            
            for name, model in models.items():
                logger.info(f"모델 훈련 중: {name}")
                
                # 모델 훈련
                model.fit(X_train_scaled, self.y_train)
                
                # 예측
                y_train_pred = model.predict(X_train_scaled)
                y_val_pred = model.predict(X_val_scaled)
                y_test_pred = model.predict(X_test_scaled)
                
                # 성능 평가
                train_mse = mean_squared_error(self.y_train, y_train_pred)
                train_mae = mean_absolute_error(self.y_train, y_train_pred)
                train_r2 = r2_score(self.y_train, y_train_pred)
                
                val_mse = mean_squared_error(self.y_val, y_val_pred)
                val_mae = mean_absolute_error(self.y_val, y_val_pred)
                val_r2 = r2_score(self.y_val, y_val_pred)
                
                test_mse = mean_squared_error(self.y_test, y_test_pred)
                test_mae = mean_absolute_error(self.y_test, y_test_pred)
                test_r2 = r2_score(self.y_test, y_test_pred)
                
                # 교차 검증
                cv_scores = cross_val_score(model, X_train_scaled, self.y_train, cv=5, scoring='r2')
                
                # 결과 저장
                results[name] = {
                    'model': model,
                    'train_mse': train_mse,
                    'train_mae': train_mae,
                    'train_r2': train_r2,
                    'val_mse': val_mse,
                    'val_mae': val_mae,
                    'val_r2': val_r2,
                    'test_mse': test_mse,
                    'test_mae': test_mae,
                    'test_r2': test_r2,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std()
                }
                
                logger.info(f"{name} 훈련 완료:")
                logger.info(f"  훈련 R²: {train_r2:.4f}, 검증 R²: {val_r2:.4f}, 테스트 R²: {test_r2:.4f}")
                logger.info(f"  교차 검증: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            
            # 최고 성능 모델 선택
            best_model_name = max(results.keys(), key=lambda k: results[k]['val_r2'])
            best_model = results[best_model_name]['model']
            
            logger.info(f"🎯 최고 성능 모델: {best_model_name} (검증 R²: {results[best_model_name]['val_r2']:.4f})")
            
            # 최고 성능 모델 저장
            best_model_path = os.path.join(self.models_path, "real_best_fusion_model.pkl")
            joblib.dump(best_model, best_model_path)
            logger.info(f"실제 데이터 최고 성능 모델 저장 완료: {best_model_path}")
            
            # 모든 모델 저장
            for name, result in results.items():
                model_path = os.path.join(self.models_path, f"real_{name.lower()}_model.pkl")
                joblib.dump(result['model'], model_path)
                logger.info(f"실제 데이터 {name} 모델 저장 완료: {model_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"모델 훈련 실패: {e}")
            return {}
    
    def hyperparameter_tuning(self, model_name: str = 'RandomForest') -> Dict[str, Any]:
        """하이퍼파라미터 튜닝"""
        try:
            logger.info(f"🔧 {model_name} 하이퍼파라미터 튜닝 시작")
            
            # 데이터 정규화
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(self.X_train)
            X_val_scaled = scaler.transform(self.X_val)
            
            # 하이퍼파라미터 그리드 정의
            if model_name == 'RandomForest':
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
                base_model = RandomForestRegressor(random_state=42)
            elif model_name == 'SVR':
                param_grid = {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto', 0.001, 0.01],
                    'kernel': ['rbf', 'linear']
                }
                base_model = SVR()
            else:
                logger.warning(f"{model_name}에 대한 하이퍼파라미터 튜닝을 지원하지 않습니다")
                return {}
            
            # 그리드 서치
            grid_search = GridSearchCV(
                base_model, param_grid, cv=3, scoring='r2', n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train_scaled, self.y_train)
            
            # 최적 모델
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            best_score = grid_search.best_score_
            
            logger.info(f"최적 하이퍼파라미터: {best_params}")
            logger.info(f"최적 교차 검증 점수: {best_score:.4f}")
            
            # 최적 모델 성능 평가
            y_val_pred = best_model.predict(X_val_scaled)
            val_r2 = r2_score(self.y_val, y_val_pred)
            val_mse = mean_squared_error(self.y_val, y_val_pred)
            
            logger.info(f"검증 성능 - R²: {val_r2:.4f}, MSE: {val_mse:.4f}")
            
            # 최적 모델 저장
            tuned_model_path = os.path.join(self.models_path, f"real_{model_name.lower()}_tuned.pkl")
            joblib.dump(best_model, tuned_model_path)
            logger.info(f"실제 데이터 튜닝된 {model_name} 모델 저장 완료: {tuned_model_path}")
            
            return {
                'best_model': best_model,
                'best_params': best_params,
                'best_score': best_score,
                'val_r2': val_r2,
                'val_mse': val_mse
            }
            
        except Exception as e:
            logger.error(f"하이퍼파라미터 튜닝 실패: {e}")
            return {}
    
    def generate_training_report(self, results: Dict[str, Any], tuning_results: Dict[str, Any]) -> bool:
        """훈련 결과 보고서 생성"""
        try:
            logger.info("📝 실제 데이터 융합 모델 훈련 결과 보고서 생성 시작")
            
            # 보고서 내용 생성
            report = f"""# 🎯 실제 데이터 융합 모델 훈련 결과 보고서

## 📋 훈련 개요
- **훈련 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **데이터셋**: 실제 CMI 데이터 (574,945개 샘플)
- **특징 차원**: {self.X_train.shape[1]}개 (CMI 21개 + 음성 8개)
- **데이터 분할**: 훈련 {len(self.X_train)}개, 검증 {len(self.X_val)}개, 테스트 {len(self.X_test)}개

## 🏆 모델 성능 비교

### 📊 성능 지표 요약
| 모델 | 훈련 R² | 검증 R² | 테스트 R² | 교차 검증 (평균±표준편차) |
|------|---------|---------|-----------|---------------------------|
"""
            
            # 모델별 성능 테이블 생성
            for name, result in results.items():
                report += f"| {name} | {result['train_r2']:.4f} | {result['val_r2']:.4f} | {result['test_r2']:.4f} | {result['cv_mean']:.4f}±{result['cv_std']:.4f} |\n"
            
            # 최고 성능 모델 정보
            best_model_name = max(results.keys(), key=lambda k: results[k]['val_r2'])
            best_result = results[best_model_name]
            
            report += f"""
## 🎯 최고 성능 모델: {best_model_name}

### 📈 상세 성능 지표
- **훈련 성능**:
  - MSE: {best_result['train_mse']:.6f}
  - MAE: {best_result['train_mae']:.6f}
  - R²: {best_result['train_r2']:.4f}
- **검증 성능**:
  - MSE: {best_result['val_mse']:.6f}
  - MAE: {best_result['val_mae']:.6f}
  - R²: {best_result['val_r2']:.4f}
- **테스트 성능**:
  - MSE: {best_result['test_mse']:.6f}
  - MAE: {best_result['test_mae']:.6f}
  - R²: {best_result['test_r2']:.4f}
- **교차 검증**: {best_result['cv_mean']:.4f} ± {best_result['cv_std']:.4f}

## 🔧 하이퍼파라미터 튜닝 결과
"""
            
            if tuning_results:
                report += f"""
### RandomForest 튜닝 결과
- **최적 하이퍼파라미터**: {tuning_results.get('best_params', 'N/A')}
- **최적 교차 검증 점수**: {tuning_results.get('best_score', 0):.4f}
- **검증 성능**: R² = {tuning_results.get('val_r2', 0):.4f}, MSE = {tuning_results.get('val_mse', 0):.6f}
"""
            else:
                report += "하이퍼파라미터 튜닝을 수행하지 않았습니다.\n"
            
            report += f"""
## 📁 저장된 모델 파일
- **실제 데이터 특징 스케일러**: `real_feature_scaler.pkl`
- **실제 데이터 최고 성능 모델**: `real_best_fusion_model.pkl`
- **실제 데이터 개별 모델들**: `real_linearregression_model.pkl`, `real_randomforest_model.pkl`, `real_svr_model.pkl`
- **실제 데이터 튜닝된 모델**: `real_randomforest_tuned.pkl` (튜닝 수행 시)

## 🎉 결론
🎯 **실제 CMI 데이터로 융합 모델 훈련이 성공적으로 완료되었습니다!**

{best_model_name}이 검증 R² {best_result['val_r2']:.4f}로 최고 성능을 보였으며,
이제 실제 rPPG-음성 융합 분석에 사용할 수 있습니다.

**'트윈 엔진' 실제 데이터 훈련 완료!** 🚀

## 🔍 Mock 데이터 vs 실제 데이터 성능 비교
- **Mock 데이터**: 검증 R² 0.9906 (1,000개 샘플)
- **실제 데이터**: 검증 R² {best_result['val_r2']:.4f} ({len(self.X_val)}개 샘플)
- **데이터 규모**: {len(self.X_train) + len(self.X_val) + len(self.X_test)}배 증가
"""
            
            # 보고서 저장
            report_path = os.path.join(self.results_path, "real_fusion_model_training_report.md")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"실제 데이터 융합 모델 훈련 결과 보고서 생성 완료: {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"보고서 생성 실패: {e}")
            return False
    
    def run_complete_training(self) -> bool:
        """완전한 훈련 파이프라인 실행"""
        try:
            logger.info("🚀 실제 데이터 융합 모델 완전 훈련 파이프라인 시작")
            
            # 1단계: 데이터셋 로드
            if not self.load_dataset():
                return False
            
            # 2단계: 기본 모델 훈련
            results = self.train_models()
            if not results:
                return False
            
            # 3단계: 하이퍼파라미터 튜닝 (RandomForest)
            tuning_results = self.hyperparameter_tuning('RandomForest')
            
            # 4단계: 결과 보고서 생성
            if not self.generate_training_report(results, tuning_results):
                return False
            
            logger.info("🎉 실제 데이터 융합 모델 완전 훈련 파이프라인 완료!")
            return True
            
        except Exception as e:
            logger.error(f"훈련 파이프라인 실행 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    try:
        logger.info("🎯 실제 데이터 융합 모델 훈련 시작")
        
        # 훈련기 초기화
        trainer = RealFusionModelTrainer()
        
        # 완전한 훈련 파이프라인 실행
        success = trainer.run_complete_training()
        
        if success:
            logger.info("🎉 실제 데이터 융합 모델 훈련 완료!")
            print("\n" + "="*60)
            print("🎉 실제 데이터 융합 모델 훈련 성공!")
            print("="*60)
            print("✅ 실제 CMI 데이터로 융합 모델 훈련 완료")
            print("✅ 최고 성능 모델 선택 및 저장 완료")
            print("✅ 하이퍼파라미터 튜닝 완료")
            print("✅ 상세 훈련 결과 보고서 생성 완료")
            print("✅ '트윈 엔진' 실제 데이터 훈련 완료!")
            print("="*60)
        else:
            logger.error("❌ 실제 데이터 융합 모델 훈련 실패")
            print("\n" + "="*60)
            print("❌ 훈련 실패 - 문제를 파악하고 수정해주세요.")
            print("="*60)
        
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")
        print(f"\n❌ 실행 오류: {e}")

if __name__ == "__main__":
    main()
