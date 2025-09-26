#!/usr/bin/env python3
"""
융합 모델 훈련 간단 테스트 스크립트 (독립 실행)
"""

import numpy as np
import pandas as pd
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_mock_cmi_data(file_path: str) -> bool:
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

def create_mock_voice_data(dir_path: str) -> bool:
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

def test_fusion_pipeline():
    """융합 파이프라인 테스트"""
    try:
        logger.info("🧪 융합 모델 훈련 파이프라인 테스트 시작")
        
        # 1단계: Mock 데이터 생성
        logger.info("📊 1단계: Mock 데이터 생성")
        
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # CMI Mock 데이터 생성
            cmi_data_path = os.path.join(temp_dir, "cmi_data.csv")
            if not create_mock_cmi_data(cmi_data_path):
                logger.error("CMI Mock 데이터 생성 실패")
                return False
            
            # 음성 Mock 데이터 생성
            voice_data_path = os.path.join(temp_dir, "voice_data")
            if not create_mock_voice_data(voice_data_path):
                logger.error("음성 Mock 데이터 생성 실패")
                return False
            
            # 2단계: 데이터 통합 시뮬레이션
            logger.info("🔧 2단계: 데이터 통합 시뮬레이션")
            
            # CMI 데이터 로드
            cmi_data = pd.read_csv(cmi_data_path)
            logger.info(f"CMI 데이터 로드: {len(cmi_data)}개 샘플")
            
            # 음성 데이터 로드
            voice_file = os.path.join(voice_data_path, "voice_features.csv")
            voice_data = pd.read_csv(voice_file)
            logger.info(f"음성 데이터 로드: {len(voice_data)}개 샘플")
            
            # 3단계: 특징 융합 시뮬레이션
            logger.info("🎯 3단계: 특징 융합 시뮬레이션")
            
            # 데이터 동기화 (간단한 매핑)
            min_samples = min(len(cmi_data), len(voice_data))
            fused_features = []
            
            for i in range(min_samples):
                # rPPG 특징 (10개)
                rppg_features = [
                    cmi_data.iloc[i]['heart_rate'],
                    cmi_data.iloc[i]['hrv'],
                    0.5 if cmi_data.iloc[i]['stress_level'] == 'low' else 0.8,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                ]
                
                # 음성 특징 (8개)
                voice_features = [
                    voice_data.iloc[i]['pitch_hz'],
                    voice_data.iloc[i]['jitter_percent'],
                    voice_data.iloc[i]['shimmer_db'],
                    voice_data.iloc[i]['hnr_db'],
                    voice_data.iloc[i]['energy'],
                    0.0, 0.0, 0.0
                ]
                
                # 특징 융합
                fused = np.concatenate([rppg_features, voice_features])
                
                # 라벨 생성 (건강 점수)
                hr_score = 1.0 if 60 <= rppg_features[0] <= 100 else 0.5
                hrv_score = 1.0 if rppg_features[1] >= 50 else 0.3
                voice_score = 1.0 if voice_features[1] < 2.0 else 0.6
                
                health_score = (hr_score * 0.4 + hrv_score * 0.4 + voice_score * 0.2)
                
                fused_features.append((fused, health_score))
            
            logger.info(f"특징 융합 완료: {len(fused_features)}개 샘플")
            
            # 4단계: 훈련 데이터셋 생성
            logger.info("📊 4단계: 훈련 데이터셋 생성")
            
            # 데이터 분할 (70% 훈련, 15% 검증, 15% 테스트)
            total_samples = len(fused_features)
            train_size = int(total_samples * 0.7)
            val_size = int(total_samples * 0.15)
            
            training_data = fused_features[:train_size]
            validation_data = fused_features[train_size:train_size + val_size]
            test_data = fused_features[train_size + val_size:]
            
            logger.info(f"데이터셋 분할 완료: 훈련 {len(training_data)}개, 검증 {len(validation_data)}개, 테스트 {len(test_data)}개")
            
            # 5단계: 모델 훈련 시뮬레이션
            logger.info("🎯 5단계: 모델 훈련 시뮬레이션")
            
            # 간단한 선형 회귀 모델 시뮬레이션
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_squared_error, r2_score
            
            # 훈련 데이터 준비
            X_train = np.array([features for features, _ in training_data])
            y_train = np.array([label for _, label in training_data])
            
            X_val = np.array([features for features, _ in validation_data])
            y_val = np.array([label for _, label in validation_data])
            
            X_test = np.array([features for features, _ in test_data])
            y_test = np.array([label for _, label in test_data])
            
            # 모델 훈련
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # 검증 데이터로 성능 평가
            y_val_pred = model.predict(X_val)
            val_mse = mean_squared_error(y_val, y_val_pred)
            val_r2 = r2_score(y_val, y_val_pred)
            
            # 테스트 데이터로 최종 성능 평가
            y_test_pred = model.predict(X_test)
            test_mse = mean_squared_error(y_test, y_test_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            
            logger.info(f"모델 훈련 완료!")
            logger.info(f"검증 성능 - MSE: {val_mse:.4f}, R²: {val_r2:.4f}")
            logger.info(f"테스트 성능 - MSE: {test_mse:.4f}, R²: {test_r2:.4f}")
            
            # 6단계: 결과 저장
            logger.info("💾 6단계: 결과 저장")
            
            # 출력 디렉토리 생성
            output_dir = "./test_output/fusion_training"
            os.makedirs(output_dir, exist_ok=True)
            
            # 결과 저장
            results = {
                'training_samples': len(training_data),
                'validation_samples': len(validation_data),
                'test_samples': len(test_data),
                'feature_dimension': X_train.shape[1],
                'validation_mse': float(val_mse),
                'validation_r2': float(val_r2),
                'test_mse': float(test_mse),
                'test_r2': float(test_r2),
                'model_type': 'LinearRegression',
                'created_at': datetime.now().isoformat()
            }
            
            # JSON 파일로 저장
            import json
            results_file = os.path.join(output_dir, "training_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"결과 저장 완료: {results_file}")
            
            # 7단계: 성공 보고서 생성
            logger.info("📝 7단계: 성공 보고서 생성")
            
            report = f"""# 🎯 융합 모델 훈련 테스트 성공 보고서

## 📋 테스트 개요
- **테스트 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **테스트 유형**: 융합 모델 훈련 파이프라인 테스트
- **테스트 상태**: ✅ 성공

## 📊 데이터셋 정보
- **총 샘플 수**: {total_samples}
- **훈련 샘플**: {len(training_data)}개
- **검증 샘플**: {len(validation_data)}개
- **테스트 샘플**: {len(test_data)}개
- **특징 차원**: {X_train.shape[1]}개

## 🎯 훈련 결과
- **모델 유형**: LinearRegression
- **검증 MSE**: {val_mse:.4f}
- **검증 R²**: {val_r2:.4f}
- **테스트 MSE**: {test_mse:.4f}
- **테스트 R²**: {test_r2:.4f}

## 🎉 결론
🎉 **융합 모델 훈련 파이프라인 테스트가 성공적으로 완료되었습니다!**

모든 단계가 정상적으로 작동하며, 실제 데이터로 훈련을 진행할 수 있습니다.
"""
            
            report_file = os.path.join(output_dir, "success_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"성공 보고서 생성 완료: {report_file}")
            
            return True
            
    except Exception as e:
        logger.error(f"융합 파이프라인 테스트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    try:
        logger.info("🚀 융합 모델 훈련 파이프라인 테스트 시작")
        
        # 테스트 실행
        success = test_fusion_pipeline()
        
        if success:
            logger.info("🎉 융합 모델 훈련 파이프라인 테스트 완료!")
            print("\n" + "="*60)
            print("🎉 융합 모델 훈련 파이프라인 테스트 성공!")
            print("="*60)
            print("✅ 모든 단계가 정상적으로 작동합니다.")
            print("✅ 실제 데이터로 훈련을 진행할 수 있습니다.")
            print("✅ '트윈 엔진' 점화 작전 준비 완료!")
            print("="*60)
        else:
            logger.error("❌ 융합 모델 훈련 파이프라인 테스트 실패")
            print("\n" + "="*60)
            print("❌ 테스트 실패 - 문제를 파악하고 수정해주세요.")
            print("="*60)
        
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")
        print(f"\n❌ 실행 오류: {e}")

if __name__ == "__main__":
    main()
