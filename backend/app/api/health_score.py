from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import logging
from typing import List, Dict, Any
import numpy as np
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Score"])


class RPPGResult(BaseModel):
    """rPPG 측정 결과"""
    heart_rate: float
    hrv: float
    stress_level: str
    signal_quality: str
    confidence: float


class VoiceResult(BaseModel):
    """음성 분석 결과"""
    f0_mean: float
    f0_std: float
    jitter: float
    shimmer: float
    hnr: float
    voice_quality: str
    stress_level: str


class HealthScoreRequest(BaseModel):
    """건강 점수 계산 요청"""
    rppg_result: RPPGResult
    voice_result: VoiceResult
    user_age: int = 30
    user_gender: str = "unknown"
    measurement_time: str = None


class HealthScoreCalculator:
    """의학 논문 기반 건강 점수 계산기"""
    
    def __init__(self):
        # 연령별 정상 범위 정의 (의학 문헌 기반)
        self.age_ranges = {
            "young": (18, 39),
            "middle": (40, 59),
            "elderly": (60, 100)
        }
        
        # 성별별 정상 범위
        self.gender_factors = {
            "male": {"hr_factor": 1.0, "hrv_factor": 1.0},
            "female": {"hr_factor": 1.05, "hrv_factor": 1.1},
            "unknown": {"hr_factor": 1.025, "hrv_factor": 1.05}
        }
    
    def calculate_age_group(self, age: int) -> str:
        """연령대 분류"""
        if age < 40:
            return "young"
        elif age < 60:
            return "middle"
        else:
            return "elderly"
    
    def get_normal_ranges(self, age_group: str, gender: str) -> Dict[str, tuple]:
        """연령대 및 성별별 정상 범위"""
        # 의학 문헌 기반 정상 범위
        ranges = {
            "young": {
                "heart_rate": (60, 100),
                "hrv": (20, 100),
                "jitter": (0, 2.0),
                "shimmer": (0, 5.0),
                "hnr": (15, 30)
            },
            "middle": {
                "heart_rate": (65, 105),
                "hrv": (15, 80),
                "jitter": (0, 2.5),
                "shimmer": (0, 6.0),
                "hnr": (12, 25)
            },
            "elderly": {
                "heart_rate": (70, 110),
                "hrv": (10, 60),
                "jitter": (0, 3.0),
                "shimmer": (0, 7.0),
                "hnr": (10, 22)
            }
        }
        
        return ranges[age_group]
    
    def calculate_heart_score(self, heart_rate: float, hrv: float, 
                            age_group: str, gender: str) -> Dict[str, Any]:
        """심혈관 건강 점수 계산"""
        normal_ranges = self.get_normal_ranges(age_group, gender)
        gender_factors = self.gender_factors[gender]
        
        # 심박수 점수 (0-100)
        hr_min, hr_max = normal_ranges["heart_rate"]
        hr_factor = gender_factors["hr_factor"]
        
        # 성별 보정된 정상 범위
        adjusted_hr_min = hr_min * hr_factor
        adjusted_hr_max = hr_max * hr_factor
        
        if adjusted_hr_min <= heart_rate <= adjusted_hr_max:
            hr_score = 100  # 정상 범위
        else:
            # 정상 범위에서 벗어날수록 감점
            if heart_rate < adjusted_hr_min:
                deviation = (adjusted_hr_min - heart_rate) / adjusted_hr_min
            else:
                deviation = (heart_rate - adjusted_hr_max) / adjusted_hr_max
            
            hr_score = max(0, 100 - (deviation * 100))
        
        # HRV 점수 (0-100)
        hrv_min, hrv_max = normal_ranges["hrv"]
        hrv_factor = gender_factors["hrv_factor"]
        
        adjusted_hrv_min = hrv_min * hrv_factor
        adjusted_hrv_max = hrv_max * hrv_factor
        
        if adjusted_hrv_min <= hrv <= adjusted_hrv_max:
            hrv_score = 100
        else:
            if hrv < adjusted_hrv_min:
                deviation = (adjusted_hrv_min - hrv) / adjusted_hrv_min
            else:
                deviation = (hrv - adjusted_hrv_max) / adjusted_hrv_max
            
            hrv_score = max(0, 100 - (deviation * 100))
        
        # 심혈관 종합 점수
        cardiovascular_score = (hr_score * 0.6) + (hrv_score * 0.4)
        
        return {
            "heart_rate_score": round(hr_score, 1),
            "hrv_score": round(hrv_score, 1),
            "cardiovascular_score": round(cardiovascular_score, 1),
            "heart_rate_grade": self.get_grade(hr_score),
            "hrv_grade": self.get_grade(hrv_score),
            "cardiovascular_grade": self.get_grade(cardiovascular_score)
        }
    
    def calculate_voice_score(self, voice_result: VoiceResult, 
                            age_group: str) -> Dict[str, Any]:
        """음성 건강 점수 계산"""
        normal_ranges = self.get_normal_ranges(age_group, "unknown")
        
        # Jitter 점수 (0-100)
        jitter_max = normal_ranges["jitter"]
        if voice_result.jitter <= jitter_max:
            jitter_score = 100
        else:
            deviation = (voice_result.jitter - jitter_max) / jitter_max
            jitter_score = max(0, 100 - (deviation * 100))
        
        # Shimmer 점수 (0-100)
        shimmer_max = normal_ranges["shimmer"]
        if voice_result.shimmer <= shimmer_max:
            shimmer_score = 100
        else:
            deviation = (voice_result.shimmer - shimmer_max) / shimmer_max
            shimmer_score = max(0, 100 - (deviation * 100))
        
        # HNR 점수 (0-100)
        hnr_min, hnr_max = normal_ranges["hnr"]
        if hnr_min <= voice_result.hnr <= hnr_max:
            hnr_score = 100
        else:
            if voice_result.hnr < hnr_min:
                deviation = (hnr_min - voice_result.hnr) / hnr_min
            else:
                deviation = (voice_result.hnr - hnr_max) / hnr_max
            
            hnr_score = max(0, 100 - (deviation * 100))
        
        # F0 안정성 점수
        f0_cv = voice_result.f0_std / voice_result.f0_mean if voice_result.f0_mean > 0 else 0
        f0_stability_score = max(0, 100 - (f0_cv * 1000))
        
        # 음성 종합 점수
        voice_score = (
            jitter_score * 0.25 + 
            shimmer_score * 0.25 + 
            hnr_score * 0.3 + 
            f0_stability_score * 0.2
        )
        
        return {
            "jitter_score": round(jitter_score, 1),
            "shimmer_score": round(shimmer_score, 1),
            "hnr_score": round(hnr_score, 1),
            "f0_stability_score": round(f0_stability_score, 1),
            "voice_score": round(voice_score, 1),
            "jitter_grade": self.get_grade(jitter_score),
            "shimmer_grade": self.get_grade(shimmer_score),
            "hnr_grade": self.get_grade(hnr_score),
            "voice_grade": self.get_grade(voice_score)
        }
    
    def calculate_stress_score(self, rppg_result: RPPGResult, 
                             voice_result: VoiceResult) -> Dict[str, Any]:
        """스트레스 점수 계산"""
        # rPPG 스트레스 점수
        stress_levels = {"매우 낮음": 0, "낮음": 25, "보통": 50, "높음": 75}
        rppg_stress_score = stress_levels.get(rppg_result.stress_level, 50)
        
        # 음성 스트레스 점수
        voice_stress_score = stress_levels.get(voice_result.stress_level, 50)
        
        # 종합 스트레스 점수
        total_stress_score = (rppg_stress_score * 0.6) + (voice_stress_score * 0.4)
        
        # 스트레스 등급
        if total_stress_score < 25:
            stress_grade = "매우 낮음"
        elif total_stress_score < 50:
            stress_grade = "낮음"
        elif total_stress_score < 75:
            stress_grade = "보통"
        else:
            stress_grade = "높음"
        
        return {
            "rppg_stress_score": round(rppg_stress_score, 1),
            "voice_stress_score": round(voice_stress_score, 1),
            "total_stress_score": round(total_stress_score, 1),
            "stress_grade": stress_grade
        }
    
    def get_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"
    
    def generate_recommendations(self, scores: Dict[str, Any], 
                               age_group: str) -> List[str]:
        """건강 점수 기반 권장사항 생성"""
        recommendations = []
        
        # 심혈관 건강 권장사항
        if scores["cardiovascular_score"] < 70:
            recommendations.append(
                "심혈관 건강이 우려됩니다. 규칙적인 유산소 운동과 "
                "심장 건강에 좋은 식단을 권장합니다."
            )
        
        if scores["heart_rate_score"] < 60:
            recommendations.append(
                "심박수가 정상 범위를 벗어났습니다. "
                "의료진과 상담하여 원인을 파악하시기 바랍니다."
            )
        
        if scores["hrv_score"] < 60:
            recommendations.append(
                "심박변이도가 낮습니다. 스트레스 관리와 "
                "충분한 휴식을 취하시기 바랍니다."
            )
        
        # 음성 건강 권장사항
        if scores["voice_score"] < 70:
            recommendations.append(
                "음성 건강이 우려됩니다. 목소리 휴식과 "
                "적절한 수분 섭취를 권장합니다."
            )
        
        if scores["jitter_score"] < 60:
            recommendations.append(
                "음성의 주파수 안정성이 낮습니다. "
                "목소리 사용을 줄이고 휴식을 취하세요."
            )
        
        if scores["hnr_score"] < 60:
            recommendations.append(
                "음성의 하모닉 성분이 부족합니다. "
                "호흡법과 발성법을 개선해보세요."
            )
        
        # 스트레스 관리 권장사항
        if scores["total_stress_score"] > 60:
            recommendations.append(
                "스트레스 수준이 높습니다. 명상, 요가, "
                "자연 속 산책 등으로 스트레스를 해소하세요."
            )
        
        # 연령대별 특화 권장사항
        if age_group == "elderly":
            recommendations.append(
                "고령자 특성상 정기적인 건강 검진과 "
                "적절한 운동 강도를 유지하시기 바랍니다."
            )
        elif age_group == "young":
            recommendations.append(
                "젊은 나이에 건강한 습관을 만드는 것이 중요합니다. "
                "규칙적인 운동과 균형 잡힌 식단을 유지하세요."
            )
        
        # 기본 권장사항
        if not recommendations:
            recommendations.append(
                "전반적으로 건강한 상태입니다. "
                "현재의 건강한 습관을 계속 유지하세요."
            )
        
        return recommendations


@router.post("/calculate-score")
async def calculate_health_score(request: HealthScoreRequest):
    """건강 점수 계산 API 엔드포인트"""
    try:
        logger.info(f"건강 점수 계산 시작: 연령 {request.user_age}, "
                   f"성별 {request.user_gender}")
        
        # 측정 시간 설정
        if not request.measurement_time:
            request.measurement_time = datetime.now().isoformat()
        
        # 건강 점수 계산기 초기화
        calculator = HealthScoreCalculator()
        
        # 연령대 분류
        age_group = calculator.calculate_age_group(request.user_age)
        
        # 각 영역별 점수 계산
        heart_scores = calculator.calculate_heart_score(
            request.rppg_result.heart_rate,
            request.rppg_result.hrv,
            age_group,
            request.user_gender
        )
        
        voice_scores = calculator.calculate_voice_score(
            request.voice_result,
            age_group
        )
        
        stress_scores = calculator.calculate_stress_score(
            request.rppg_result,
            request.voice_result
        )
        
        # 종합 건강 점수 계산
        overall_score = (
            heart_scores["cardiovascular_score"] * 0.5 +
            voice_scores["voice_score"] * 0.3 +
            (100 - stress_scores["total_stress_score"]) * 0.2
        )
        
        # 권장사항 생성
        all_scores = {
            **heart_scores,
            **voice_scores,
            **stress_scores,
            "overall_score": round(overall_score, 1)
        }
        
        recommendations = calculator.generate_recommendations(
            all_scores, age_group
        )
        
        # 최종 결과
        result = {
            "success": True,
            "measurement_id": str(uuid.uuid4()),
            "measurement_time": request.measurement_time,
            "user_profile": {
                "age": request.user_age,
                "age_group": age_group,
                "gender": request.user_gender
            },
            "scores": {
                "overall": {
                    "score": round(overall_score, 1),
                    "grade": calculator.get_grade(overall_score)
                },
                "cardiovascular": {
                    "score": heart_scores["cardiovascular_score"],
                    "grade": heart_scores["cardiovascular_grade"],
                    "details": {
                        "heart_rate": heart_scores["heart_rate_score"],
                        "hrv": heart_scores["hrv_score"]
                    }
                },
                "voice": {
                    "score": voice_scores["voice_score"],
                    "grade": voice_scores["voice_grade"],
                    "details": {
                        "jitter": voice_scores["jitter_score"],
                        "shimmer": voice_scores["shimmer_score"],
                        "hnr": voice_scores["hnr_score"],
                        "f0_stability": voice_scores["f0_stability_score"]
                    }
                },
                "stress": {
                    "score": stress_scores["total_stress_score"],
                    "grade": stress_scores["stress_grade"]
                }
            },
            "recommendations": recommendations,
            "analysis_metadata": {
                "algorithm_version": "2.0.0",
                "calculation_method": "의학 논문 기반 알고리즘",
                "confidence_level": "high"
            }
        }
        
        logger.info(f"건강 점수 계산 완료: 종합 점수 {overall_score:.1f}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"건강 점수 계산 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"건강 점수 계산 중 오류 발생: {str(e)}"
        )


@router.get("/health")
async def health_score_health_check():
    """건강 점수 계산 서비스 상태 확인"""
    return {
        "service": "Health Score Calculator", 
        "status": "healthy", 
        "version": "2.0.0",
        "features": [
            "의학 논문 기반 알고리즘",
            "연령대별 정상 범위 적용",
            "성별별 보정 계수",
            "심혈관 건강 점수",
            "음성 건강 점수",
            "스트레스 점수",
            "개인화된 권장사항"
        ]
    }
