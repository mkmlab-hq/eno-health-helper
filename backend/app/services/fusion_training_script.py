#!/usr/bin/env python3
"""
융합 모델 훈련 메인 스크립트
"""

import numpy as np
import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# 기존 서비스들 import
from .fusion_data_pipeline import FusionDataPipeline
from .fusion_analyzer import AdvancedFusionAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FusionModelTrainer:
    """
    융합 모델 훈련 메인 클래스
    
    핵심 기능:
    1. 데이터 파이프라인 실행
    2. 모델 훈련 및 검증
    3. 성능 평가 및 모델 저장
    4. 훈련 결과 보고서 생성
    """
    
    def __init__(self):
        # 파이프라인 및 분석기 초기화
        self.data_pipeline = FusionDataPipeline()
        self.fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 훈련 설정
        self.training_config = {
            'model_save_path': './models/fusion_model.joblib',
            'results_save_path': './results/training_results.json',
            'min_training_samples': 50,
            'target_accuracy': 0.85,
            'max_training_iterations': 3
        }
        
        # 훈련 결과
        self.training_results = {}
        
        logger.info("융합 모델 훈련기 초기화 완료")
    
    def run_complete_training_pipeline(
        self,
        cmi_data_path: str,
        voice_dataset_path: str,
        output_base_path: str
    ) -> bool:
        """
        완전한 훈련 파이프라인 실행
        
        Args:
            cmi_data_path: CMI 데이터 파일 경로
            voice_dataset_path: 음성 데이터셋 경로
            output_base_path: 출력 기본 경로
            
        Returns:
            훈련 성공 여부
        """
        try:
            logger.info("🚀 완전한 융합 모델 훈련 파이프라인 시작")
            
            # 1단계: 데이터 통합 및 전처리
            logger.info("📊 1단계: 데이터 통합 및 전처리")
            data_integration_success = self._integrate_data(
                cmi_data_path, voice_dataset_path, output_base_path
            )
            
            if not data_integration_success:
                logger.error("데이터 통합 실패")
                return False
            
            # 2단계: 훈련 데이터 검증
            logger.info("🔍 2단계: 훈련 데이터 검증")
            if not self._validate_training_data():
                logger.error("훈련 데이터 검증 실패")
                return False
            
            # 3단계: 모델 훈련
            logger.info("🎯 3단계: 모델 훈련")
            training_success = self._train_fusion_model()
            
            if not training_success:
                logger.error("모델 훈련 실패")
                return False
            
            # 4단계: 모델 성능 평가
            logger.info("📈 4단계: 모델 성능 평가")
            evaluation_success = self._evaluate_model_performance()
            
            if not evaluation_success:
                logger.error("모델 성능 평가 실패")
                return False
            
            # 5단계: 결과 저장 및 보고서 생성
            logger.info("💾 5단계: 결과 저장 및 보고서 생성")
            self._save_training_results(output_base_path)
            self._generate_training_report(output_base_path)
            
            logger.info("✅ 융합 모델 훈련 파이프라인 완료")
            return True
            
        except Exception as e:
            logger.error(f"훈련 파이프라인 실행 실패: {e}")
            return False
    
    def _integrate_data(
        self,
        cmi_data_path: str,
        voice_dataset_path: str,
        output_base_path: str
    ) -> bool:
        """데이터 통합 실행"""
        try:
            # 데이터 통합 실행
            success = self.data_pipeline.integrate_cmi_and_voice_data(
                cmi_data_path=cmi_data_path,
                voice_dataset_path=voice_dataset_path,
                output_path=f"{output_base_path}/integrated_dataset"
            )
            
            if success:
                logger.info("데이터 통합 성공")
                return True
            else:
                logger.error("데이터 통합 실패")
                return False
                
        except Exception as e:
            logger.error(f"데이터 통합 중 오류: {e}")
            return False
    
    def _validate_training_data(self) -> bool:
        """훈련 데이터 검증"""
        try:
            # 훈련 데이터 가져오기
            train_data, val_data, test_data = self.data_pipeline.get_training_data()
            
            # 데이터 수량 검증
            if len(train_data) < self.training_config['min_training_samples']:
                logger.error(f"훈련 데이터 부족: {len(train_data)}개 (최소 {self.training_config['min_training_samples']}개 필요)")
                return False
            
            # 데이터 품질 검증
            if not self._check_data_quality(train_data):
                logger.error("훈련 데이터 품질 검증 실패")
                return False
            
            logger.info(f"훈련 데이터 검증 성공: 훈련 {len(train_data)}개, 검증 {len(val_data)}개, 테스트 {len(test_data)}개")
            return True
            
        except Exception as e:
            logger.error(f"훈련 데이터 검증 중 오류: {e}")
            return False
    
    def _check_data_quality(self, training_data: List[Tuple[np.ndarray, float]]) -> bool:
        """데이터 품질 검증"""
        try:
            if not training_data:
                return False
            
            # 특징 차원 검증
            feature_dim = len(training_data[0][0])
            if feature_dim != 18:  # rPPG(10) + 음성(8)
                logger.error(f"특징 차원 불일치: {feature_dim} (예상: 18)")
                return False
            
            # 라벨 범위 검증
            labels = [label for _, label in training_data]
            if min(labels) < 0 or max(labels) > 1:
                logger.error(f"라벨 범위 오류: {min(labels)} ~ {max(labels)} (예상: 0~1)")
                return False
            
            # NaN/Inf 검증
            for features, _ in training_data:
                if np.any(np.isnan(features)) or np.any(np.isinf(features)):
                    logger.error("특징에 NaN 또는 Inf 값 발견")
                    return False
            
            logger.info("데이터 품질 검증 통과")
            return True
            
        except Exception as e:
            logger.error(f"데이터 품질 검증 중 오류: {e}")
            return False
    
    def _train_fusion_model(self) -> bool:
        """융합 모델 훈련"""
        try:
            # 훈련 데이터 가져오기
            train_data, val_data, test_data = self.data_pipeline.get_training_data()
            
            # 훈련 반복 (성능 향상을 위해)
            best_accuracy = 0.0
            best_iteration = 0
            
            for iteration in range(self.training_config['max_training_iterations']):
                logger.info(f"🔄 훈련 반복 {iteration + 1}/{self.training_config['max_training_iterations']}")
                
                # 모델 훈련
                training_success = self.fusion_analyzer.train_fusion_model(train_data)
                
                if not training_success:
                    logger.error(f"훈련 반복 {iteration + 1} 실패")
                    continue
                
                # 검증 데이터로 성능 평가
                accuracy = self._evaluate_on_validation_data(val_data)
                
                logger.info(f"훈련 반복 {iteration + 1} 정확도: {accuracy:.4f}")
                
                # 최고 성능 모델 저장
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_iteration = iteration + 1
                    
                    # 모델 저장
                    self._save_best_model()
                
                # 목표 정확도 달성 시 조기 종료
                if accuracy >= self.training_config['target_accuracy']:
                    logger.info(f"🎯 목표 정확도 달성: {accuracy:.4f}")
                    break
            
            # 최종 결과 저장
            self.training_results['best_accuracy'] = best_accuracy
            self.training_results['best_iteration'] = best_iteration
            self.training_results['total_iterations'] = iteration + 1
            
            logger.info(f"모델 훈련 완료: 최고 정확도 {best_accuracy:.4f} (반복 {best_iteration})")
            return True
            
        except Exception as e:
            logger.error(f"모델 훈련 중 오류: {e}")
            return False
    
    def _evaluate_on_validation_data(self, val_data: List[Tuple[np.ndarray, float]]) -> float:
        """검증 데이터로 성능 평가"""
        try:
            if not val_data:
                return 0.0
            
            correct_predictions = 0
            total_predictions = 0
            
            for features, true_label in val_data:
                try:
                    # 모델 예측
                    prediction = self.fusion_analyzer.fusion_model.predict(features.reshape(1, -1))[0]
                    
                    # 예측 정확도 계산 (0.1 이내 오차를 정확한 것으로 간주)
                    if abs(prediction - true_label) <= 0.1:
                        correct_predictions += 1
                    
                    total_predictions += 1
                    
                except Exception as e:
                    logger.warning(f"검증 예측 실패: {e}")
                    continue
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
            return accuracy
            
        except Exception as e:
            logger.error(f"검증 데이터 평가 중 오류: {e}")
            return 0.0
    
    def _evaluate_model_performance(self) -> bool:
        """모델 성능 평가"""
        try:
            # 테스트 데이터로 최종 성능 평가
            _, _, test_data = self.data_pipeline.get_training_data()
            
            if not test_data:
                logger.warning("테스트 데이터가 없습니다")
                return True
            
            # 정확도 평가
            test_accuracy = self._evaluate_on_validation_data(test_data)
            
            # 상세 성능 메트릭
            performance_metrics = self._calculate_detailed_metrics(test_data)
            
            # 결과 저장
            self.training_results['test_accuracy'] = test_accuracy
            self.training_results['performance_metrics'] = performance_metrics
            
            logger.info(f"최종 테스트 정확도: {test_accuracy:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"모델 성능 평가 중 오류: {e}")
            return False
    
    def _calculate_detailed_metrics(self, test_data: List[Tuple[np.ndarray, float]]) -> Dict[str, Any]:
        """상세 성능 메트릭 계산"""
        try:
            predictions = []
            true_labels = []
            
            for features, true_label in test_data:
                try:
                    prediction = self.fusion_analyzer.fusion_model.predict(features.reshape(1, -1))[0]
                    predictions.append(prediction)
                    true_labels.append(true_label)
                except Exception as e:
                    continue
            
            if not predictions:
                return {"error": "예측 실패"}
            
            # 기본 통계
            predictions = np.array(predictions)
            true_labels = np.array(true_labels)
            
            # 오차 계산
            errors = np.abs(predictions - true_labels)
            
            metrics = {
                'mean_absolute_error': float(np.mean(errors)),
                'mean_squared_error': float(np.mean(errors ** 2)),
                'root_mean_squared_error': float(np.sqrt(np.mean(errors ** 2))),
                'mean_absolute_percentage_error': float(np.mean(np.abs(errors / (true_labels + 1e-8))) * 100),
                'r_squared': float(self._calculate_r_squared(true_labels, predictions)),
                'correlation': float(np.corrcoef(true_labels, predictions)[0, 1])
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"상세 메트릭 계산 중 오류: {e}")
            return {"error": str(e)}
    
    def _calculate_r_squared(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """R² 점수 계산"""
        try:
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            return r2
        except Exception:
            return 0.0
    
    def _save_best_model(self) -> bool:
        """최고 성능 모델 저장"""
        try:
            # 모델 저장 디렉토리 생성
            os.makedirs(os.path.dirname(self.training_config['model_save_path']), exist_ok=True)
            
            # 모델 저장
            success = self.fusion_analyzer.save_model(self.training_config['model_save_path'])
            
            if success:
                logger.info(f"최고 성능 모델 저장 완료: {self.training_config['model_save_path']}")
                return True
            else:
                logger.error("모델 저장 실패")
                return False
                
        except Exception as e:
            logger.error(f"모델 저장 중 오류: {e}")
            return False
    
    def _save_training_results(self, output_base_path: str) -> bool:
        """훈련 결과 저장"""
        try:
            # 결과 저장 디렉토리 생성
            results_dir = f"{output_base_path}/training_results"
            os.makedirs(results_dir, exist_ok=True)
            
            # 결과 파일 경로
            results_file = f"{results_dir}/training_results.json"
            
            # 결과에 메타데이터 추가
            final_results = {
                'training_config': self.training_config,
                'training_results': self.training_results,
                'dataset_info': self.data_pipeline.get_dataset_info(),
                'training_timestamp': datetime.now().isoformat(),
                'model_path': self.training_config['model_save_path']
            }
            
            # JSON 파일로 저장
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"훈련 결과 저장 완료: {results_file}")
            return True
            
        except Exception as e:
            logger.error(f"훈련 결과 저장 중 오류: {e}")
            return False
    
    def _generate_training_report(self, output_base_path: str) -> bool:
        """훈련 보고서 생성"""
        try:
            # 보고서 디렉토리 생성
            report_dir = f"{output_base_path}/reports"
            os.makedirs(report_dir, exist_ok=True)
            
            # 보고서 파일 경로
            report_file = f"{report_dir}/training_report.md"
            
            # Markdown 보고서 생성
            report_content = self._create_markdown_report()
            
            # 파일 저장
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"훈련 보고서 생성 완료: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"훈련 보고서 생성 중 오류: {e}")
            return False
    
    def _create_markdown_report(self) -> str:
        """Markdown 형식의 훈련 보고서 생성"""
        try:
            dataset_info = self.data_pipeline.get_dataset_info()
            
            report = f"""# 🎯 융합 모델 훈련 보고서

## 📋 훈련 개요
- **훈련 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **모델 유형**: rPPG-음성 융합 모델
- **훈련 알고리즘**: Random Forest Ensemble

## 📊 데이터셋 정보
- **총 샘플 수**: {dataset_info.get('training_samples', 0) + dataset_info.get('validation_samples', 0) + dataset_info.get('test_samples', 0)}
- **훈련 샘플**: {dataset_info.get('training_samples', 0)}개
- **검증 샘플**: {dataset_info.get('validation_samples', 0)}개
- **테스트 샘플**: {dataset_info.get('test_samples', 0)}개
- **특징 차원**: {dataset_info.get('feature_dimension', 0)}개

## 🎯 훈련 결과
- **최고 정확도**: {self.training_results.get('best_accuracy', 0.0):.4f}
- **최고 성능 반복**: {self.training_results.get('best_iteration', 0)}회차
- **총 훈련 반복**: {self.training_results.get('total_iterations', 0)}회
- **테스트 정확도**: {self.training_results.get('test_accuracy', 0.0):.4f}

## 📈 성능 메트릭
"""
            
            # 성능 메트릭 추가
            if 'performance_metrics' in self.training_results:
                metrics = self.training_results['performance_metrics']
                if 'error' not in metrics:
                    report += f"""
- **평균 절대 오차 (MAE)**: {metrics.get('mean_absolute_error', 0.0):.4f}
- **평균 제곱 오차 (MSE)**: {metrics.get('mean_squared_error', 0.0):.4f}
- **루트 평균 제곱 오차 (RMSE)**: {metrics.get('root_mean_squared_error', 0.0):.4f}
- **평균 절대 백분율 오차 (MAPE)**: {metrics.get('mean_absolute_percentage_error', 0.0):.2f}%
- **R² 점수**: {metrics.get('r_squared', 0.0):.4f}
- **상관계수**: {metrics.get('correlation', 0.0):.4f}
"""
            
            report += f"""
## 💾 모델 정보
- **모델 저장 경로**: {self.training_config['model_save_path']}
- **결과 저장 경로**: {self.training_config['results_save_path']}

## 🎉 훈련 완료
융합 모델 훈련이 성공적으로 완료되었습니다.
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Markdown 보고서 생성 중 오류: {e}")
            return f"# 오류\n\n보고서 생성 실패: {str(e)}"
    
    def get_training_summary(self) -> Dict[str, Any]:
        """훈련 요약 반환"""
        return {
            'status': 'completed' if self.training_results else 'not_started',
            'best_accuracy': self.training_results.get('best_accuracy', 0.0),
            'test_accuracy': self.training_results.get('test_accuracy', 0.0),
            'model_saved': os.path.exists(self.training_config['model_save_path']),
            'dataset_info': self.data_pipeline.get_dataset_info()
        }


def main():
    """메인 실행 함수"""
    try:
        logger.info("🎯 융합 모델 훈련 스크립트 시작")
        
        # 훈련기 초기화
        trainer = FusionModelTrainer()
        
        # 예시 데이터 경로 (실제 사용 시 수정 필요)
        cmi_data_path = "./data/cmi_data.csv"  # 실제 CMI 데이터 경로
        voice_dataset_path = "./data/voice_dataset"  # 실제 음성 데이터셋 경로
        output_base_path = "./output/fusion_training"
        
        # 훈련 파이프라인 실행
        success = trainer.run_complete_training_pipeline(
            cmi_data_path=cmi_data_path,
            voice_dataset_path=voice_dataset_path,
            output_base_path=output_base_path
        )
        
        if success:
            logger.info("🎉 융합 모델 훈련 완료!")
            
            # 훈련 요약 출력
            summary = trainer.get_training_summary()
            logger.info(f"훈련 요약: {summary}")
        else:
            logger.error("❌ 융합 모델 훈련 실패")
        
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")


if __name__ == "__main__":
    main()
