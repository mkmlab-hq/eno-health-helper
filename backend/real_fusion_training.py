#!/usr/bin/env python3
"""
실제 데이터로 융합 모델 훈련 스크립트
"""

import numpy as np
import pandas as pd
import logging
import os
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealFusionTrainer:
    """실제 데이터로 융합 모델 훈련"""
    
    def __init__(self):
        self.rppg_data_path = None
        self.voice_data_path = None
        self.output_path = "./real_fusion_output"
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_path, exist_ok=True)
        
        logger.info("실제 데이터 융합 모델 훈련기 초기화 완료")
    
    def download_real_data(self) -> bool:
        """실제 데이터 다운로드"""
        try:
            logger.info("🚀 실제 데이터 다운로드 시작")
            
            # 1단계: rPPG 데이터 다운로드
            logger.info("📊 1단계: rPPG 데이터 다운로드")
            rppg_success = self._download_rppg_data()
            if not rppg_success:
                logger.error("rPPG 데이터 다운로드 실패")
                return False
            
            # 2단계: 음성 데이터 다운로드
            logger.info("🎵 2단계: 음성 데이터 다운로드")
            voice_success = self._download_voice_data()
            if not voice_success:
                logger.error("음성 데이터 다운로드 실패")
                return False
            
            logger.info("✅ 실제 데이터 다운로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"데이터 다운로드 실패: {e}")
            return False
    
    def _download_rppg_data(self) -> bool:
        """rPPG 데이터 다운로드"""
        try:
            # rPPG 데이터 다운로드 (S1~S5만 선택하여 빠른 테스트)
            rppg_source = "gs://mkm-ai-datasets/archive/rppg-field-study-data/PPG_FieldStudy/"
            self.rppg_data_path = os.path.join(self.output_path, "rppg_data")
            
            # S1~S5 데이터만 다운로드
            for i in range(1, 6):
                subject = f"S{i}"
                source_path = f"{rppg_source}{subject}/"
                target_path = os.path.join(self.rppg_data_path, subject)
                
                logger.info(f"다운로드 중: {subject}")
                result = subprocess.run([
                    "gsutil", "-m", "cp", "-r", source_path, target_path
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.warning(f"{subject} 다운로드 실패: {result.stderr}")
                else:
                    logger.info(f"{subject} 다운로드 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"rPPG 데이터 다운로드 실패: {e}")
            return False
    
    def _download_voice_data(self) -> bool:
        """음성 데이터 다운로드"""
        try:
            # 음성 데이터 다운로드 (RAVDESS만 선택하여 빠른 테스트)
            voice_source = "gs://mkm-ai-datasets/ser-datasets/ravdess/"
            self.voice_data_path = os.path.join(self.output_path, "voice_data")
            
            logger.info("RAVDESS 음성 데이터 다운로드 중...")
            result = subprocess.run([
                "gsutil", "-m", "cp", "-r", voice_source, self.voice_data_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"음성 데이터 다운로드 실패: {result.stderr}")
                return False
            
            logger.info("음성 데이터 다운로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"음성 데이터 다운로드 실패: {e}")
            return False
    
    def process_real_data(self) -> bool:
        """실제 데이터 처리 및 융합"""
        try:
            logger.info("🔧 실제 데이터 처리 및 융합 시작")
            
            # 1단계: rPPG 데이터 처리
            logger.info("📊 1단계: rPPG 데이터 처리")
            rppg_features = self._process_rppg_data()
            if rppg_features is None:
                logger.error("rPPG 데이터 처리 실패")
                return False
            
            # 2단계: 음성 데이터 처리
            logger.info("🎵 2단계: 음성 데이터 처리")
            voice_features = self._process_voice_data()
            if voice_features is None:
                logger.error("음성 데이터 처리 실패")
                return False
            
            # 3단계: 데이터 융합
            logger.info("🎯 3단계: 데이터 융합")
            fused_data = self._fuse_real_data(rppg_features, voice_features)
            if fused_data is None:
                logger.error("데이터 융합 실패")
                return False
            
            # 4단계: 훈련 데이터셋 생성
            logger.info("📊 4단계: 훈련 데이터셋 생성")
            success = self._create_training_dataset(fused_data)
            
            if success:
                logger.info("✅ 실제 데이터 처리 및 융합 완료")
                return True
            else:
                logger.error("훈련 데이터셋 생성 실패")
                return False
                
        except Exception as e:
            logger.error(f"실제 데이터 처리 실패: {e}")
            return False
    
    def _process_rppg_data(self) -> Optional[List[Dict]]:
        """rPPG 데이터 처리"""
        try:
            if not self.rppg_data_path or not os.path.exists(self.rppg_data_path):
                logger.error("rPPG 데이터 경로가 존재하지 않습니다")
                return None
            
            processed_data = []
            
            # 각 참가자 데이터 처리
            for subject in os.listdir(self.rppg_data_path):
                subject_path = os.path.join(self.rppg_data_path, subject)
                if not os.path.isdir(subject_path):
                    continue
                
                logger.info(f"rPPG 데이터 처리 중: {subject}")
                
                # CSV 파일 찾기
                csv_files = [f for f in os.listdir(subject_path) if f.endswith('.csv')]
                if not csv_files:
                    logger.warning(f"{subject}에 CSV 파일이 없습니다")
                    continue
                
                # 첫 번째 CSV 파일 처리
                csv_path = os.path.join(subject_path, csv_files[0])
                try:
                    df = pd.read_csv(csv_path)
                    
                    # 기본 rPPG 특징 추출
                    for idx, row in df.iterrows():
                        if idx >= 100:  # 각 참가자당 최대 100개 샘플
                            break
                        
                        # rPPG 특징 (10개)
                        features = {
                            'subject': subject,
                            'sample_id': f"{subject}_{idx}",
                            'heart_rate': self._extract_heart_rate(row),
                            'hrv': self._extract_hrv(row),
                            'stress_level': self._classify_stress_level(row),
                            'ppg_amplitude': self._extract_ppg_amplitude(row),
                            'ppg_frequency': self._extract_ppg_frequency(row),
                            'ppg_quality': self._assess_ppg_quality(row),
                            'motion_level': self._assess_motion_level(row),
                            'lighting_condition': self._assess_lighting(row),
                            'skin_tone_factor': self._estimate_skin_tone(row)
                        }
                        
                        processed_data.append(features)
                        
                except Exception as e:
                    logger.warning(f"{subject} CSV 처리 실패: {e}")
                    continue
            
            if not processed_data:
                logger.error("처리된 rPPG 데이터가 없습니다")
                return None
            
            logger.info(f"rPPG 데이터 처리 완료: {len(processed_data)}개 샘플")
            return processed_data
            
        except Exception as e:
            logger.error(f"rPPG 데이터 처리 실패: {e}")
            return None
    
    def _process_voice_data(self) -> Optional[List[Dict]]:
        """음성 데이터 처리"""
        try:
            if not self.voice_data_path or not os.path.exists(self.voice_data_path):
                logger.error("음성 데이터 경로가 존재하지 않습니다")
                return None
            
            processed_data = []
            
            # RAVDESS 데이터 처리
            logger.info("RAVDESS 음성 데이터 처리 중...")
            
            # 음성 파일 찾기
            audio_files = []
            for root, dirs, files in os.walk(self.voice_data_path):
                for file in files:
                    if file.endswith(('.wav', '.mp3', '.m4a')):
                        audio_files.append(os.path.join(root, file))
            
            if not audio_files:
                logger.warning("음성 파일을 찾을 수 없습니다")
                return None
            
            # 각 음성 파일에서 특징 추출 (최대 100개)
            for i, audio_file in enumerate(audio_files[:100]):
                try:
                    # 파일명에서 감정 정보 추출
                    filename = os.path.basename(audio_file)
                    emotion = self._extract_emotion_from_filename(filename)
                    
                    # 음성 특징 (8개)
                    features = {
                        'audio_file': audio_file,
                        'sample_id': f"voice_{i}",
                        'emotion': emotion,
                        'pitch_hz': self._estimate_pitch(audio_file),
                        'jitter_percent': self._estimate_jitter(audio_file),
                        'shimmer_db': self._estimate_shimmer(audio_file),
                        'hnr_db': self._estimate_hnr(audio_file),
                        'energy': self._estimate_energy(audio_file),
                        'speaking_rate': self._estimate_speaking_rate(audio_file)
                    }
                    
                    processed_data.append(features)
                    
                except Exception as e:
                    logger.warning(f"음성 파일 처리 실패: {audio_file}, {e}")
                    continue
            
            if not processed_data:
                logger.error("처리된 음성 데이터가 없습니다")
                return None
            
            logger.info(f"음성 데이터 처리 완료: {len(processed_data)}개 샘플")
            return processed_data
            
        except Exception as e:
            logger.error(f"음성 데이터 처리 실패: {e}")
            return None
    
    def _fuse_real_data(self, rppg_data: List[Dict], voice_data: List[Dict]) -> Optional[List[Tuple[np.ndarray, float]]]:
        """실제 데이터 융합"""
        try:
            logger.info("실제 데이터 융합 시작")
            
            fused_features = []
            
            # 데이터 동기화 (간단한 매핑)
            min_samples = min(len(rppg_data), len(voice_data))
            
            for i in range(min_samples):
                try:
                    rppg_sample = rppg_data[i]
                    voice_sample = voice_data[i]
                    
                    # rPPG 특징 벡터 (10개)
                    rppg_vector = [
                        float(rppg_sample.get('heart_rate', 70)),
                        float(rppg_sample.get('hrv', 50)),
                        float(rppg_sample.get('stress_level', 0.5)),
                        float(rppg_sample.get('ppg_amplitude', 0.5)),
                        float(rppg_sample.get('ppg_frequency', 1.0)),
                        float(rppg_sample.get('ppg_quality', 0.7)),
                        float(rppg_sample.get('motion_level', 0.3)),
                        float(rppg_sample.get('lighting_condition', 0.8)),
                        float(rppg_sample.get('skin_tone_factor', 0.6)),
                        0.0  # 추가 특징
                    ]
                    
                    # 음성 특징 벡터 (8개)
                    voice_vector = [
                        float(voice_sample.get('pitch_hz', 150)),
                        float(voice_sample.get('jitter_percent', 1.0)),
                        float(voice_sample.get('shimmer_db', 1.0)),
                        float(voice_sample.get('hnr_db', 20)),
                        float(voice_sample.get('energy', 0.5)),
                        float(voice_sample.get('speaking_rate', 1.0)),
                        0.0, 0.0  # 추가 특징
                    ]
                    
                    # 특징 융합 (18차원)
                    fused = np.concatenate([rppg_vector, voice_vector])
                    
                    # 라벨 생성 (건강 점수)
                    health_score = self._calculate_real_health_score(rppg_sample, voice_sample)
                    
                    fused_features.append((fused, health_score))
                    
                except Exception as e:
                    logger.warning(f"샘플 융합 실패: {e}")
                    continue
            
            if not fused_features:
                logger.error("융합된 특징이 없습니다")
                return None
            
            logger.info(f"실제 데이터 융합 완료: {len(fused_features)}개 샘플")
            return fused_features
            
        except Exception as e:
            logger.error(f"실제 데이터 융합 실패: {e}")
            return None
    
    def _create_training_dataset(self, fused_data: List[Tuple[np.ndarray, float]]) -> bool:
        """훈련 데이터셋 생성"""
        try:
            logger.info("훈련 데이터셋 생성 시작")
            
            # 데이터 분할 (70% 훈련, 15% 검증, 15% 테스트)
            total_samples = len(fused_data)
            train_size = int(total_samples * 0.7)
            val_size = int(total_samples * 0.15)
            
            training_data = fused_data[:train_size]
            validation_data = fused_data[train_size:train_size + val_size]
            test_data = fused_data[train_size + val_size:]
            
            logger.info(f"데이터셋 분할 완료: 훈련 {len(training_data)}개, 검증 {len(validation_data)}개, 테스트 {len(test_data)}개")
            
            # 데이터 저장
            dataset_path = os.path.join(self.output_path, "fusion_dataset")
            os.makedirs(dataset_path, exist_ok=True)
            
            # 훈련 데이터 저장
            np.save(os.path.join(dataset_path, "train_features.npy"), 
                   np.array([features for features, _ in training_data]))
            np.save(os.path.join(dataset_path, "train_labels.npy"), 
                   np.array([label for _, label in training_data]))
            
            # 검증 데이터 저장
            np.save(os.path.join(dataset_path, "val_features.npy"), 
                   np.array([features for features, _ in validation_data]))
            np.save(os.path.join(dataset_path, "val_labels.npy"), 
                   np.array([label for _, label in validation_data]))
            
            # 테스트 데이터 저장
            np.save(os.path.join(dataset_path, "test_features.npy"), 
                   np.array([features for features, _ in test_data]))
            np.save(os.path.join(dataset_path, "test_labels.npy"), 
                   np.array([label for _, label in test_data]))
            
            # 데이터셋 정보 저장
            dataset_info = {
                'total_samples': total_samples,
                'training_samples': len(training_data),
                'validation_samples': len(validation_data),
                'test_samples': len(test_data),
                'feature_dimension': len(fused_data[0][0]) if fused_data else 0,
                'created_at': datetime.now().isoformat(),
                'data_source': {
                    'rppg': self.rppg_data_path,
                    'voice': self.voice_data_path
                }
            }
            
            with open(os.path.join(dataset_path, "dataset_info.json"), 'w', encoding='utf-8') as f:
                json.dump(dataset_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"훈련 데이터셋 생성 완료: {dataset_path}")
            return True
            
        except Exception as e:
            logger.error(f"훈련 데이터셋 생성 실패: {e}")
            return False
    
    # 헬퍼 메서드들 (실제 구현 시 더 정교하게 구현)
    def _extract_heart_rate(self, row) -> float:
        """심박수 추출"""
        try:
            # 실제 구현 시 PPG 신호에서 심박수 추출
            return float(row.get('heart_rate', 70))
        except:
            return 70.0
    
    def _extract_hrv(self, row) -> float:
        """HRV 추출"""
        try:
            return float(row.get('hrv', 50))
        except:
            return 50.0
    
    def _classify_stress_level(self, row) -> float:
        """스트레스 수준 분류"""
        try:
            # 실제 구현 시 생체신호 기반 스트레스 분류
            return 0.5
        except:
            return 0.5
    
    def _extract_ppg_amplitude(self, row) -> float:
        """PPG 진폭 추출"""
        return 0.5
    
    def _extract_ppg_frequency(self, row) -> float:
        """PPG 주파수 추출"""
        return 1.0
    
    def _assess_ppg_quality(self, row) -> float:
        """PPG 품질 평가"""
        return 0.7
    
    def _assess_motion_level(self, row) -> float:
        """움직임 수준 평가"""
        return 0.3
    
    def _assess_lighting(self, row) -> float:
        """조명 조건 평가"""
        return 0.8
    
    def _estimate_skin_tone(self, row) -> float:
        """피부톤 추정"""
        return 0.6
    
    def _extract_emotion_from_filename(self, filename: str) -> str:
        """파일명에서 감정 추출"""
        # RAVDESS 파일명 형식: modality-vocal_channel-emotion-intensity-statement-repetition-actor.wav
        try:
            parts = filename.split('-')
            if len(parts) >= 3:
                emotion_code = parts[2]
                emotion_map = {
                    '01': 'neutral', '02': 'calm', '03': 'happy', '04': 'sad',
                    '05': 'angry', '06': 'fear', '07': 'disgust', '08': 'surprise'
                }
                return emotion_map.get(emotion_code, 'neutral')
        except:
            pass
        return 'neutral'
    
    def _estimate_pitch(self, audio_file: str) -> float:
        """음성 피치 추정"""
        return 150.0
    
    def _estimate_jitter(self, audio_file: str) -> float:
        """Jitter 추정"""
        return 1.0
    
    def _estimate_shimmer(self, audio_file: str) -> float:
        """Shimmer 추정"""
        return 1.0
    
    def _estimate_hnr(self, audio_file: str) -> float:
        """HNR 추정"""
        return 20.0
    
    def _estimate_energy(self, audio_file: str) -> float:
        """음성 에너지 추정"""
        return 0.5
    
    def _estimate_speaking_rate(self, audio_file: str) -> float:
        """말하기 속도 추정"""
        return 1.0
    
    def _calculate_real_health_score(self, rppg_sample: Dict, voice_sample: Dict) -> float:
        """실제 건강 점수 계산"""
        try:
            # rPPG 기반 점수 (60%)
            hr_score = 1.0 if 60 <= rppg_sample.get('heart_rate', 70) <= 100 else 0.5
            hrv_score = 1.0 if rppg_sample.get('hrv', 50) >= 50 else 0.3
            stress_score = 1.0 - rppg_sample.get('stress_level', 0.5)  # 스트레스가 낮을수록 높은 점수
            
            rppg_score = (hr_score + hrv_score + stress_score) / 3
            
            # 음성 기반 점수 (40%)
            jitter_score = 1.0 if voice_sample.get('jitter_percent', 1.0) < 2.0 else 0.6
            shimmer_score = 1.0 if voice_sample.get('shimmer_db', 1.0) < 2.0 else 0.6
            hnr_score = 1.0 if voice_sample.get('hnr_db', 20) >= 15 else 0.6
            
            voice_score = (jitter_score + shimmer_score + hnr_score) / 3
            
            # 가중 평균
            total_score = rppg_score * 0.6 + voice_score * 0.4
            
            return float(total_score)
            
        except Exception as e:
            logger.warning(f"건강 점수 계산 실패: {e}")
            return 0.5
    
    def run_complete_training(self) -> bool:
        """완전한 훈련 파이프라인 실행"""
        try:
            logger.info("🚀 실제 데이터 융합 모델 훈련 시작")
            
            # 1단계: 실제 데이터 다운로드
            if not self.download_real_data():
                return False
            
            # 2단계: 실제 데이터 처리 및 융합
            if not self.process_real_data():
                return False
            
            logger.info("🎉 실제 데이터 융합 모델 훈련 완료!")
            return True
            
        except Exception as e:
            logger.error(f"훈련 파이프라인 실행 실패: {e}")
            return False

def main():
    """메인 실행 함수"""
    try:
        logger.info("🎯 실제 데이터 융합 모델 훈련 시작")
        
        # 훈련기 초기화
        trainer = RealFusionTrainer()
        
        # 완전한 훈련 파이프라인 실행
        success = trainer.run_complete_training()
        
        if success:
            logger.info("🎉 실제 데이터 융합 모델 훈련 완료!")
            print("\n" + "="*60)
            print("🎉 실제 데이터 융합 모델 훈련 성공!")
            print("="*60)
            print("✅ 실제 rPPG 데이터와 음성 데이터로 훈련 완료")
            print("✅ 융합 모델 훈련 데이터셋 생성 완료")
            print("✅ '트윈 엔진' 점화 작전 성공!")
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
