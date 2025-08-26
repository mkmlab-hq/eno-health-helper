from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from ..services.firebase_service import FirebaseService
from ..models.user_measurement import UserMeasurement, MeasurementPair, ComparisonResult

router = APIRouter(prefix="/api/user/measurements", tags=["user_measurements"])
logger = logging.getLogger(__name__)

# Firebase 서비스 인스턴스
firebase_service = FirebaseService()

@router.get("/{user_id}/pairs", response_model=List[MeasurementPair])
async def get_user_measurement_pairs(
    user_id: str,
    days_back: int = 30
):
    """
    사용자의 30분 전후 측정 페어를 자동으로 생성하여 반환
    
    Args:
        user_id: 사용자 ID
        days_back: 몇 일 전까지의 데이터를 가져올지 (기본값: 30일)
    
    Returns:
        List[MeasurementPair]: 30분 전후 측정 페어 목록
    """
    try:
        logger.info(f"사용자 {user_id}의 측정 페어 조회 시작 (최근 {days_back}일)")
        
        # 사용자의 모든 측정 기록 조회
        measurements = await firebase_service.get_user_measurements(user_id, days_back)
        
        if not measurements:
            logger.info(f"사용자 {user_id}의 측정 기록이 없습니다.")
            return []
        
        # 30분 전후 페어 자동 생성
        pairs = create_measurement_pairs(measurements)
        
        logger.info(f"사용자 {user_id}의 측정 페어 {len(pairs)}개 생성 완료")
        return pairs
        
    except Exception as e:
        logger.error(f"측정 페어 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"측정 페어 조회 실패: {str(e)}")

@router.get("/{user_id}/pairs/{pair_id}/comparison", response_model=ComparisonResult)
async def get_measurement_comparison(
    user_id: str,
    pair_id: str
):
    """
    특정 측정 페어의 상세 비교 분석 결과 반환
    
    Args:
        user_id: 사용자 ID
        pair_id: 측정 페어 ID
    
    Returns:
        ComparisonResult: 상세 비교 분석 결과
    """
    try:
        logger.info(f"사용자 {user_id}의 측정 페어 {pair_id} 비교 분석 시작")
        
        # 측정 페어 데이터 조회
        pair = await firebase_service.get_measurement_pair(user_id, pair_id)
        
        if not pair:
            raise HTTPException(status_code=404, detail="측정 페어를 찾을 수 없습니다.")
        
        # 비교 분석 수행
        comparison = perform_comparison_analysis(pair)
        
        logger.info(f"측정 페어 {pair_id} 비교 분석 완료")
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비교 분석 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"비교 분석 실패: {str(e)}")

def create_measurement_pairs(measurements: List[UserMeasurement]) -> List[MeasurementPair]:
    """
    30분 전후 측정 페어를 자동으로 생성
    
    Args:
        measurements: 사용자의 모든 측정 기록
    
    Returns:
        List[MeasurementPair]: 30분 전후 측정 페어 목록
    """
    pairs = []
    sorted_measurements = sorted(measurements, key=lambda x: x.timestamp)
    
    for i, measurement in enumerate(sorted_measurements):
        # 30분 ± 10분 범위 내의 다음 측정 찾기
        for j in range(i + 1, len(sorted_measurements)):
            next_measurement = sorted_measurements[j]
            time_diff = next_measurement.timestamp - measurement.timestamp
            
            # 20분 ~ 40분 범위 내인 경우 페어 생성
            if timedelta(minutes=20) <= time_diff <= timedelta(minutes=40):
                pair = MeasurementPair(
                    pair_id=f"pair_{len(pairs) + 1}",
                    before_measurement=measurement,
                    after_measurement=next_measurement,
                    time_interval_minutes=time_diff.total_seconds() / 60,
                    created_at=datetime.now()
                )
                pairs.append(pair)
                break  # 첫 번째 매칭된 페어만 생성
    
    return pairs

def perform_comparison_analysis(pair: MeasurementPair) -> ComparisonResult:
    """
    측정 페어의 상세 비교 분석 수행
    
    Args:
        pair: 측정 페어 데이터
    
    Returns:
        ComparisonResult: 비교 분석 결과
    """
    before = pair.before_measurement
    after = pair.after_measurement
    
    # 주요 지표 변화량 계산
    changes = {
        "overall_health_score": {
            "before": before.overall_health_score,
            "after": after.overall_health_score,
            "change": after.overall_health_score - before.overall_health_score,
            "change_percentage": ((after.overall_health_score - before.overall_health_score) / before.overall_health_score) * 100
        },
        "heart_rate": {
            "before": before.heart_rate,
            "after": after.heart_rate,
            "change": after.heart_rate - before.heart_rate,
            "change_percentage": ((after.heart_rate - before.heart_rate) / before.heart_rate) * 100
        },
        "hrv": {
            "before": before.hrv,
            "after": after.hrv,
            "change": after.hrv - before.hrv,
            "change_percentage": ((after.hrv - before.hrv) / before.hrv) * 100
        },
        "stress_level": {
            "before": before.stress_level,
            "after": after.stress_level,
            "change": after.stress_level - before.stress_level,
            "change_percentage": ((after.stress_level - before.stress_level) / before.stress_level) * 100
        },
        "voice_stability": {
            "before": before.voice_stability,
            "after": after.voice_stability,
            "change": after.voice_stability - before.voice_stability,
            "change_percentage": ((after.voice_stability - before.voice_stability) / before.voice_stability) * 100
        }
    }
    
    # 변화 방향 분석
    improvement_count = sum(1 for metric in changes.values() if metric["change"] > 0)
    total_metrics = len(changes)
    improvement_rate = (improvement_count / total_metrics) * 100
    
    return ComparisonResult(
        pair_id=pair.pair_id,
        before_measurement=before,
        after_measurement=after,
        time_interval_minutes=pair.time_interval_minutes,
        changes=changes,
        improvement_rate=improvement_rate,
        overall_assessment=get_overall_assessment(changes, improvement_rate),
        created_at=datetime.now()
    )

def get_overall_assessment(changes: Dict, improvement_rate: float) -> str:
    """
    전체적인 변화 평가 결과 반환
    
    Args:
        changes: 각 지표별 변화 데이터
        improvement_rate: 개선률
    
    Returns:
        str: 전체 평가 결과
    """
    if improvement_rate >= 80:
        return "매우 우수한 개선"
    elif improvement_rate >= 60:
        return "우수한 개선"
    elif improvement_rate >= 40:
        return "양호한 개선"
    elif improvement_rate >= 20:
        return "약간의 개선"
    else:
        return "개선 효과 미미"
