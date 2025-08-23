#!/usr/bin/env python3
"""
융합 모델 훈련 테스트 스크립트
"""

import numpy as np
import pandas as pd
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Any

# 기존 서비스들 import
from .fusion_data_pipeline import FusionDataPipeline
from .fusion_training_script import FusionModelTrainer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FusionTrainingTester:
    """
    융합 모델 훈련 테스트 클래스
    
    핵심 기능:
    1. Mock 데이터 생성
    2. 훈련 파이프라인 테스트
    3. 결과 검증
    """
    
    def __init__(self):
        self.test_results = {}
        logger.info("융합 모델 훈련 테스터 초기화 완료")
    
    def run_complete_test(self) -> bool:
        """완전한 테스트 실행"""
        try:
            logger.info("🧪 융합 모델 훈련 완전 테스트 시작")
            
            # 1단계: Mock 데이터 생성
            logger.info("📊 1단계: Mock 데이터 생성")
            mock_data_success = self._create_mock_test_data()
            
            if not mock_data_success:
                logger.error("Mock 데이터 생성 실패")
                return False
            
            # 2단계: 데이터 파이프라인 테스트
            logger.info("🔧 2단계: 데이터 파이프라인 테스트")
            pipeline_success = self._test_data_pipeline()
            
            if not pipeline_success:
                logger.error("데이터 파이프라인 테스트 실패")
                return False
            
            # 3단계: 훈련 파이프라인 테스트
            logger.info("🎯 3단계: 훈련 파이프라인 테스트")
            training_success = self._test_training_pipeline()
            
            if not training_success:
                logger.error("훈련 파이프라인 테스트 실패")
                return False
            
            # 4단계: 결과 검증
            logger.info("✅ 4단계: 결과 검증")
            validation_success = self._validate_test_results()
            
            if not validation_success:
                logger.error("결과 검증 실패")
                return False
            
            logger.info("🎉 융합 모델 훈련 테스트 완료")
            return True
            
        except Exception as e:
            logger.error(f"테스트 실행 실패: {e}")
            return False
    
    def _create_mock_test_data(self) -> bool:
        """Mock 테스트 데이터 생성"""
        try:
            # 임시 디렉토리 생성
            with tempfile.TemporaryDirectory() as temp_dir:
                # CMI Mock 데이터 생성
                cmi_data_path = os.path.join(temp_dir, "cmi_data.csv")
                cmi_success = self._create_mock_cmi_data(cmi_data_path)
                
                if not cmi_success:
                    return False
                
                # 음성 Mock 데이터 생성
                voice_data_path = os.path.join(temp_dir, "voice_data")
                voice_success = self._create_mock_voice_data(voice_data_path)
                
                if not voice_success:
                    return False
                
                # 테스트 결과 저장
                self.test_results['mock_data'] = {
                    'cmi_path': cmi_data_path,
                    'voice_path': voice_data_path,
                    'temp_dir': temp_dir
                }
                
                logger.info("Mock 테스트 데이터 생성 완료")
                return True
                
        except Exception as e:
            logger.error(f"Mock 데이터 생성 실패: {e}")
            return False
    
    def _create_mock_cmi_data(self, file_path: str) -> bool:
        """CMI Mock 데이터 생성"""
        try:
            # 100개의 Mock CMI 샘플 생성
            n_samples = 100
            
            # 심박수: 60-120 범위
            heart_rates = np.random.normal(80, 15, n_samples)
            heart_rates = np.clip(heart_rates, 60, 120)
            
            # HRV: 20-100 범위
            hrv_values = np.random.normal(60, 20, n_samples)
            hrv_values = np.clip(hrv_values, 20, 100)
            
            # 스트레스 수준
            stress_levels = np.random.choice(['low', 'medium', 'high'], n_samples, p=[0.6, 0.3, 0.1])
            
            # 타임스탬프
            timestamps = [f"2025-08-23_{i:02d}:00:00" for i in range(n_samples)]
            
            # DataFrame 생성
            cmi_data = pd.DataFrame({
                'timestamp': timestamps,
                'heart_rate': heart_rates,
                'hrv': hrv_values,
                'stress_level': stress_levels
            })
            
            # CSV 파일로 저장
            cmi_data.to_csv(file_path, index=False)
            
            logger.info(f"CMI Mock 데이터 생성 완료: {len(cmi_data)}개 샘플")
            return True
            
        except Exception as e:
            logger.error(f"CMI Mock 데이터 생성 실패: {e}")
            return False
    
    def _create_mock_voice_data(self, dir_path: str) -> bool:
        """음성 Mock 데이터 생성"""
        try:
            # 디렉토리 생성
            os.makedirs(dir_path, exist_ok=True)
            
            # 8가지 감정별 Mock 데이터
            emotions = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprise']
            
            # 각 감정별 12개 샘플 생성 (총 96개)
            voice_data = []
            
            for emotion in emotions:
                for i in range(12):
                    sample = {
                        'emotion': emotion,
                        'pitch_hz': np.random.normal(150, 30),
                        'jitter_percent': np.random.uniform(0.5, 3.0),
                        'shimmer_db': np.random.uniform(0.3, 2.5),
                        'hnr_db': np.random.uniform(15, 25),
                        'energy': np.random.uniform(0.3, 0.8),
                        'sample_id': f"{emotion}_{i}"
                    }
                    voice_data.append(sample)
            
            # CSV 파일로 저장
            voice_file_path = os.path.join(dir_path, "voice_features.csv")
            voice_df = pd.DataFrame(voice_data)
            voice_df.to_csv(voice_file_path, index=False)
            
            logger.info(f"음성 Mock 데이터 생성 완료: {len(voice_data)}개 샘플")
            return True
            
        except Exception as e:
            logger.error(f"음성 Mock 데이터 생성 실패: {e}")
            return False
    
    def _test_data_pipeline(self) -> bool:
        """데이터 파이프라인 테스트"""
        try:
            # Mock 데이터 경로 가져오기
            mock_data = self.test_results.get('mock_data', {})
            cmi_path = mock_data.get('cmi_path')
            voice_path = mock_data.get('voice_path')
            
            if not cmi_path or not voice_path:
                logger.error("Mock 데이터 경로를 찾을 수 없습니다")
                return False
            
            # 데이터 파이프라인 초기화
            pipeline = FusionDataPipeline()
            
            # 데이터 통합 테스트
            output_path = "./test_output/fusion_dataset"
            
            success = pipeline.integrate_cmi_and_voice_data(
                cmi_data_path=cmi_path,
                voice_dataset_path=voice_path,
                output_path=output_path
            )
            
            if success:
                # 훈련 데이터 가져오기
                train_data, val_data, test_data = pipeline.get_training_data()
                
                # 데이터 검증
                if len(train_data) > 0 and len(val_data) > 0 and len(test_data) > 0:
                    logger.info(f"데이터 파이프라인 테스트 성공: 훈련 {len(train_data)}개, 검증 {len(val_data)}개, 테스트 {len(test_data)}개")
                    
                    # 테스트 결과 저장
                    self.test_results['pipeline_test'] = {
                        'success': True,
                        'train_samples': len(train_data),
                        'val_samples': len(val_data),
                        'test_samples': len(test_data),
                        'output_path': output_path
                    }
                    
                    return True
                else:
                    logger.error("데이터 파이프라인에서 유효한 데이터를 가져올 수 없습니다")
                    return False
            else:
                logger.error("데이터 파이프라인 실행 실패")
                return False
                
        except Exception as e:
            logger.error(f"데이터 파이프라인 테스트 실패: {e}")
            return False
    
    def _test_training_pipeline(self) -> bool:
        """훈련 파이프라인 테스트"""
        try:
            # Mock 데이터 경로 가져오기
            mock_data = self.test_results.get('mock_data', {})
            cmi_path = mock_data.get('cmi_path')
            voice_path = mock_data.get('voice_path')
            
            if not cmi_path or not voice_path:
                logger.error("Mock 데이터 경로를 찾을 수 없습니다")
                return False
            
            # 훈련기 초기화
            trainer = FusionModelTrainer()
            
            # 훈련 파이프라인 실행
            output_path = "./test_output/fusion_training"
            
            success = trainer.run_complete_training_pipeline(
                cmi_data_path=cmi_path,
                voice_dataset_path=voice_path,
                output_base_path=output_path
            )
            
            if success:
                # 훈련 요약 가져오기
                summary = trainer.get_training_summary()
                
                logger.info(f"훈련 파이프라인 테스트 성공: {summary}")
                
                # 테스트 결과 저장
                self.test_results['training_test'] = {
                    'success': True,
                    'summary': summary,
                    'output_path': output_path
                }
                
                return True
            else:
                logger.error("훈련 파이프라인 실행 실패")
                return False
                
        except Exception as e:
            logger.error(f"훈련 파이프라인 테스트 실패: {e}")
            return False
    
    def _validate_test_results(self) -> bool:
        """테스트 결과 검증"""
        try:
            logger.info("테스트 결과 검증 시작")
            
            # 1. 데이터 파이프라인 검증
            pipeline_test = self.test_results.get('pipeline_test', {})
            if not pipeline_test.get('success', False):
                logger.error("데이터 파이프라인 테스트 실패")
                return False
            
            # 2. 훈련 파이프라인 검증
            training_test = self.test_results.get('training_test', {})
            if not training_test.get('success', False):
                logger.error("훈련 파이프라인 테스트 실패")
                return False
            
            # 3. 성능 검증
            summary = training_test.get('summary', {})
            if summary.get('status') != 'completed':
                logger.error("훈련이 완료되지 않았습니다")
                return False
            
            # 4. 모델 저장 검증
            if not summary.get('model_saved', False):
                logger.error("모델이 저장되지 않았습니다")
                return False
            
            # 5. 정확도 검증
            best_accuracy = summary.get('best_accuracy', 0.0)
            if best_accuracy < 0.5:  # 최소 50% 정확도
                logger.warning(f"정확도가 낮습니다: {best_accuracy:.4f}")
            
            logger.info("테스트 결과 검증 완료")
            return True
            
        except Exception as e:
            logger.error(f"테스트 결과 검증 실패: {e}")
            return False
    
    def generate_test_report(self) -> str:
        """테스트 보고서 생성"""
        try:
            report = f"""# 🧪 융합 모델 훈련 테스트 보고서

## 📋 테스트 개요
- **테스트 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **테스트 유형**: 융합 모델 훈련 완전 테스트
- **테스트 상태**: {'성공' if self.test_results else '실패'}

## 📊 테스트 결과

### 1. Mock 데이터 생성
- **CMI 데이터**: {self.test_results.get('mock_data', {}).get('cmi_path', 'N/A')}
- **음성 데이터**: {self.test_results.get('mock_data', {}).get('voice_path', 'N/A')}

### 2. 데이터 파이프라인 테스트
"""
            
            pipeline_test = self.test_results.get('pipeline_test', {})
            if pipeline_test.get('success'):
                report += f"""
- **상태**: ✅ 성공
- **훈련 샘플**: {pipeline_test.get('train_samples', 0)}개
- **검증 샘플**: {pipeline_test.get('val_samples', 0)}개
- **테스트 샘플**: {pipeline_test.get('test_samples', 0)}개
"""
            else:
                report += "- **상태**: ❌ 실패\n"
            
            report += """
### 3. 훈련 파이프라인 테스트
"""
            
            training_test = self.test_results.get('training_test', {})
            if training_test.get('success'):
                summary = training_test.get('summary', {})
                report += f"""
- **상태**: ✅ 성공
- **훈련 상태**: {summary.get('status', 'N/A')}
- **최고 정확도**: {summary.get('best_accuracy', 0.0):.4f}
- **테스트 정확도**: {summary.get('test_accuracy', 0.0):.4f}
- **모델 저장**: {'✅ 성공' if summary.get('model_saved') else '❌ 실패'}
"""
            else:
                report += "- **상태**: ❌ 실패\n"
            
            report += f"""
## 🎯 결론
"""
            
            if self.test_results and pipeline_test.get('success') and training_test.get('success'):
                report += "🎉 **모든 테스트가 성공적으로 완료되었습니다!**\n\n"
                report += "융합 모델 훈련 파이프라인이 정상적으로 작동합니다.\n"
                report += "실제 데이터로 훈련을 진행할 수 있습니다."
            else:
                report += "❌ **일부 테스트가 실패했습니다.**\n\n"
                report += "문제를 파악하고 수정한 후 다시 테스트해주세요."
            
            return report
            
        except Exception as e:
            logger.error(f"테스트 보고서 생성 실패: {e}")
            return f"# 오류\n\n테스트 보고서 생성 실패: {str(e)}"
    
    def get_test_summary(self) -> Dict[str, Any]:
        """테스트 요약 반환"""
        return {
            'status': 'completed' if self.test_results else 'not_started',
            'pipeline_success': self.test_results.get('pipeline_test', {}).get('success', False),
            'training_success': self.test_results.get('training_test', {}).get('success', False),
            'total_tests': 3,
            'passed_tests': sum([
                bool(self.test_results.get('mock_data')),
                bool(self.test_results.get('pipeline_test', {}).get('success')),
                bool(self.test_results.get('training_test', {}).get('success'))
            ])
        }


def main():
    """메인 실행 함수"""
    try:
        logger.info("🧪 융합 모델 훈련 테스트 시작")
        
        # 테스터 초기화
        tester = FusionTrainingTester()
        
        # 완전한 테스트 실행
        success = tester.run_complete_test()
        
        if success:
            logger.info("🎉 융합 모델 훈련 테스트 완료!")
            
            # 테스트 요약 출력
            summary = tester.get_test_summary()
            logger.info(f"테스트 요약: {summary}")
            
            # 테스트 보고서 생성
            report = tester.generate_test_report()
            print("\n" + "="*50)
            print("🧪 융합 모델 훈련 테스트 보고서")
            print("="*50)
            print(report)
            
        else:
            logger.error("❌ 융합 모델 훈련 테스트 실패")
        
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")


if __name__ == "__main__":
    main()
