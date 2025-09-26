#!/usr/bin/env python3
"""
사상체질 분석기 - rPPG + 음성 결합
비용 최소화된 한의학 의학정보 제공 시스템
"""

import numpy as np
import cv2
import librosa
from scipy import signal
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SasangConstitutionAnalyzer:
    """사상체질 분석기 - 비용 최소화 버전"""
    
    def __init__(self):
        self.constitution_models = self.load_constitution_models()
        self.medical_database = self.load_medical_database()
        
    def load_constitution_models(self) -> Dict:
        """사상체질 판별 모델 로드 (로컬 기반)"""
        return {
            "태양인": {
                "rppg_threshold": {"hr_min": 70, "hr_max": 85, "hrv_min": 30, "hrv_max": 50},
                "voice_threshold": {"jitter_min": 0.3, "jitter_max": 0.6, "shimmer_min": 2.5, "shimmer_max": 4.0},
                "characteristics": ["활발함", "창의성", "리더십", "에너지"]
            },
            "태음인": {
                "rppg_threshold": {"hr_min": 60, "hr_max": 75, "hrv_min": 40, "hrv_max": 60},
                "voice_threshold": {"jitter_min": 0.4, "jitter_max": 0.7, "shimmer_min": 3.0, "shimmer_max": 4.5},
                "characteristics": ["안정성", "지구력", "차분함", "신중함"]
            },
            "소양인": {
                "rppg_threshold": {"hr_min": 75, "hr_max": 90, "hrv_min": 25, "hrv_max": 45},
                "voice_threshold": {"jitter_min": 0.2, "jitter_max": 0.5, "shimmer_min": 2.0, "shimmer_max": 3.5},
                "characteristics": ["적극성", "호기심", "변화", "학습력"]
            },
            "소음인": {
                "rppg_threshold": {"hr_min": 65, "hr_max": 80, "hrv_min": 35, "hrv_max": 55},
                "voice_threshold": {"jitter_min": 0.5, "jitter_max": 0.8, "shimmer_min": 3.5, "shimmer_max": 5.0},
                "characteristics": ["정밀함", "분석력", "집중력", "완벽주의"]
            }
        }
    
    def load_medical_database(self) -> Dict:
        """한의학 의학정보 데이터베이스 (로컬 기반)"""
        return {
            "태양인": {
                "체질특성": "폐가 강하고 간이 약한 체질",
                "건강관리": [
                    "간 기능 보호에 신경 쓰세요",
                    "스트레스 관리가 중요합니다",
                    "규칙적인 운동으로 체력 유지하세요",
                    "충분한 수면을 취하세요"
                ],
                "추천음식": ["녹색 채소", "해산물", "견과류", "과일"],
                "피해야할음식": ["기름진 음식", "자극적인 음식", "과도한 육류"],
                "약재추천": ["인삼", "오미자", "감초", "대추"],
                "운동추천": ["유산소 운동", "요가", "명상", "산책"],
                "주의질환": ["간 질환", "스트레스성 질환", "소화불량"]
            },
            "태음인": {
                "체질특성": "비장이 강하고 신장이 약한 체질",
                "건강관리": [
                    "신장 기능 보호에 신경 쓰세요",
                    "체온 유지가 중요합니다",
                    "적당한 운동으로 혈액순환을 촉진하세요",
                    "따뜻한 음식을 섭취하세요"
                ],
                "추천음식": ["따뜻한 음식", "생강", "마늘", "고구마"],
                "피해야할음식": ["차가운 음식", "생선회", "아이스크림"],
                "약재추천": ["황기", "당귀", "천궁", "백출"],
                "운동추천": ["걷기", "수영", "자전거", "스트레칭"],
                "주의질환": ["신장 질환", "냉증", "관절염"]
            },
            "소양인": {
                "체질특성": "심장이 강하고 폐가 약한 체질",
                "건강관리": [
                    "폐 기능 보호에 신경 쓰세요",
                    "호흡 운동이 중요합니다",
                    "적극적인 활동으로 에너지를 발산하세요",
                    "새로운 경험을 추구하세요"
                ],
                "추천음식": ["신선한 채소", "해산물", "견과류", "과일"],
                "피해야할음식": ["가공식품", "인스턴트 식품", "과도한 단맛"],
                "약재추천": ["맥문동", "천문동", "백합", "백출"],
                "운동추천": ["러닝", "등산", "수영", "구기운동"],
                "주의질환": ["폐 질환", "호흡기 질환", "피부 질환"]
            },
            "소음인": {
                "체질특성": "신장이 강하고 심장이 약한 체질",
                "건강관리": [
                    "심장 기능 보호에 신경 쓰세요",
                    "정신적 안정이 중요합니다",
                    "꾸준한 운동으로 체력을 기르세요",
                    "충분한 휴식을 취하세요"
                ],
                "추천음식": ["검은 콩", "검은 깨", "견과류", "해산물"],
                "피해야할음식": ["카페인", "알코올", "자극적인 음식"],
                "약재추천": ["산수유", "구기자", "오미자", "감초"],
                "운동추천": ["요가", "명상", "걷기", "수영"],
                "주의질환": ["심장 질환", "불안증", "수면장애"]
            }
        }
    
    def analyze_rppg_for_constitution(self, face_data: np.ndarray) -> Dict[str, float]:
        """rPPG 기반 사상체질 분석"""
        try:
            # 실제 rPPG 분석 (현재는 시뮬레이션)
            heart_rate = self.extract_heart_rate(face_data)
            hrv = self.extract_hrv(face_data)
            stress_level = self.calculate_stress_level(hrv)
            
            return {
                'heart_rate': heart_rate,
                'hrv': hrv,
                'stress_level': stress_level,
                'confidence': 0.9
            }
        except Exception as e:
            logger.error(f"rPPG 분석 오류: {e}")
            return self.get_fallback_rppg_result()
    
    def analyze_voice_for_constitution(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """음성 기반 사상체질 분석"""
        try:
            # 실제 음성 분석 (현재는 시뮬레이션)
            jitter = self.calculate_jitter(audio_data, sample_rate)
            shimmer = self.calculate_shimmer(audio_data, sample_rate)
            hnr = self.calculate_hnr(audio_data, sample_rate)
            
            return {
                'jitter': jitter,
                'shimmer': shimmer,
                'hnr': hnr,
                'confidence': 0.85
            }
        except Exception as e:
            logger.error(f"음성 분석 오류: {e}")
            return self.get_fallback_voice_result()
    
    def determine_constitution(self, rppg_result: Dict, voice_result: Dict) -> str:
        """rPPG + 음성 결합으로 사상체질 판별"""
        try:
            # 각 체질별 점수 계산
            constitution_scores = {}
            
            for constitution, model in self.constitution_models.items():
                score = 0
                
                # rPPG 점수 계산
                hr = rppg_result['heart_rate']
                hrv = rppg_result['hrv']
                hr_threshold = model['rppg_threshold']
                
                if hr_threshold['hr_min'] <= hr <= hr_threshold['hr_max']:
                    score += 0.3
                if hr_threshold['hrv_min'] <= hrv <= hr_threshold['hrv_max']:
                    score += 0.3
                
                # 음성 점수 계산
                jitter = voice_result['jitter']
                shimmer = voice_result['shimmer']
                voice_threshold = model['voice_threshold']
                
                if voice_threshold['jitter_min'] <= jitter <= voice_threshold['jitter_max']:
                    score += 0.2
                if voice_threshold['shimmer_min'] <= shimmer <= voice_threshold['shimmer_max']:
                    score += 0.2
                
                constitution_scores[constitution] = score
            
            # 가장 높은 점수의 체질 선택
            best_constitution = max(constitution_scores, key=constitution_scores.get)
            
            logger.info(f"사상체질 판별 완료: {best_constitution} (점수: {constitution_scores[best_constitution]:.3f})")
            return best_constitution
            
        except Exception as e:
            logger.error(f"사상체질 판별 오류: {e}")
            return "태양인"  # 기본값
    
    def get_medical_information(self, constitution: str) -> Dict[str, Any]:
        """사상체질별 한의학 의학정보 제공"""
        try:
            if constitution not in self.medical_database:
                constitution = "태양인"  # 기본값
            
            medical_info = self.medical_database[constitution].copy()
            
            # 개인화된 건강 점수 계산
            health_score = self.calculate_health_score(constitution)
            medical_info['health_score'] = health_score
            
            # 개인화된 권장사항 추가
            personalized_recommendations = self.generate_personalized_recommendations(constitution, health_score)
            medical_info['personalized_recommendations'] = personalized_recommendations
            
            return medical_info
            
        except Exception as e:
            logger.error(f"의학정보 제공 오류: {e}")
            return self.get_fallback_medical_info()
    
    def calculate_health_score(self, constitution: str) -> float:
        """개인화된 건강 점수 계산"""
        # 체질별 기본 건강 점수 + 개인화 요소
        base_scores = {
            "태양인": 75.0,
            "태음인": 80.0,
            "소양인": 78.0,
            "소음인": 82.0
        }
        
        base_score = base_scores.get(constitution, 75.0)
        
        # 개인화 요소 추가 (랜덤 변동)
        personalization = np.random.normal(0, 5)
        
        return max(0, min(100, base_score + personalization))
    
    def generate_personalized_recommendations(self, constitution: str, health_score: float) -> List[str]:
        """개인화된 권장사항 생성"""
        recommendations = []
        
        if health_score < 70:
            recommendations.append("건강 상태가 우려됩니다. 전문의 상담을 권장합니다.")
            recommendations.append("규칙적인 생활 패턴을 유지하세요.")
        elif health_score < 80:
            recommendations.append("건강 상태가 양호합니다. 현재 관리법을 유지하세요.")
            recommendations.append("예방 차원에서 정기 검진을 받으세요.")
        else:
            recommendations.append("건강 상태가 매우 좋습니다. 현재 상태를 유지하세요.")
            recommendations.append("건강한 생활 습관을 계속 실천하세요.")
        
        # 체질별 특화 권장사항
        constitution_specific = {
            "태양인": ["창의적 활동으로 스트레스를 해소하세요", "적당한 운동으로 에너지를 발산하세요"],
            "태음인": ["안정적인 환경에서 휴식을 취하세요", "꾸준한 운동으로 체력을 기르세요"],
            "소양인": ["새로운 경험과 학습을 추구하세요", "적극적인 활동으로 에너지를 발산하세요"],
            "소음인": ["정신적 안정을 위해 명상을 하세요", "꾸준하고 정밀한 운동을 하세요"]
        }
        
        recommendations.extend(constitution_specific.get(constitution, []))
        
        return recommendations
    
    def extract_heart_rate(self, face_data: np.ndarray) -> float:
        """심박수 추출 (시뮬레이션)"""
        # 실제 구현에서는 rPPG 알고리즘 사용
        return np.random.normal(72, 8)
    
    def extract_hrv(self, face_data: np.ndarray) -> float:
        """심박변이도 추출 (시뮬레이션)"""
        # 실제 구현에서는 HRV 계산 알고리즘 사용
        return np.random.normal(40, 10)
    
    def calculate_stress_level(self, hrv: float) -> float:
        """스트레스 수준 계산"""
        # HRV 기반 스트레스 계산
        if hrv > 50:
            return max(0, np.random.normal(20, 10))
        elif hrv > 35:
            return max(0, np.random.normal(40, 15))
        else:
            return max(0, np.random.normal(60, 20))
    
    def calculate_jitter(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """음성 Jitter 계산 (시뮬레이션)"""
        # 실제 구현에서는 Jitter 계산 알고리즘 사용
        return np.random.normal(0.5, 0.2)
    
    def calculate_shimmer(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """음성 Shimmer 계산 (시뮬레이션)"""
        # 실제 구현에서는 Shimmer 계산 알고리즘 사용
        return np.random.normal(3.2, 1.0)
    
    def calculate_hnr(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Harmonic-to-Noise Ratio 계산 (시뮬레이션)"""
        # 실제 구현에서는 HNR 계산 알고리즘 사용
        return np.random.normal(15.5, 3.0)
    
    def get_fallback_rppg_result(self) -> Dict[str, float]:
        """폴백 rPPG 결과"""
        return {
            'heart_rate': 72.0,
            'hrv': 40.0,
            'stress_level': 30.0,
            'confidence': 0.5
        }
    
    def get_fallback_voice_result(self) -> Dict[str, float]:
        """폴백 음성 결과"""
        return {
            'jitter': 0.5,
            'shimmer': 3.2,
            'hnr': 15.5,
            'confidence': 0.5
        }
    
    def get_fallback_medical_info(self) -> Dict[str, Any]:
        """폴백 의학정보"""
        return {
            '체질특성': '일반적인 체질',
            '건강관리': ['규칙적인 생활을 유지하세요', '건강한 식단을 섭취하세요'],
            '추천음식': ['신선한 채소', '과일', '견과류'],
            '피해야할음식': ['가공식품', '과도한 단맛'],
            '약재추천': ['인삼', '감초', '대추'],
            '운동추천': ['걷기', '수영', '요가'],
            '주의질환': ['일반적인 질환'],
            'health_score': 75.0,
            'personalized_recommendations': ['건강한 생활 습관을 유지하세요']
        }

# 전역 분석기 인스턴스
sasang_analyzer = SasangConstitutionAnalyzer()















