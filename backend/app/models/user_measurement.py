from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class MeasurementType(str, Enum):
    """측정 유형"""
    BEFORE = "before"  # 복용 전
    AFTER = "after"    # 복용 후


class UserMeasurement(BaseModel):
    """사용자 측정 데이터 모델"""
    measurement_id: str = Field(..., description="측정 ID")
    user_id: str = Field(..., description="사용자 ID")
    timestamp: datetime = Field(..., description="측정 시간")
    measurement_type: MeasurementType = Field(..., description="측정 유형")
    
    # rPPG 분석 결과
    heart_rate: float = Field(..., description="심박수 (BPM)")
    hrv: float = Field(..., description="심박변이도 (HRV)")
    stress_level: float = Field(..., description="스트레스 수준 (0-100)")
    signal_quality: float = Field(..., description="신호 품질 (0-1)")
    
    # 음성 분석 결과
    voice_stability: float = Field(..., description="음성 안정성 (0-1)")
    jitter_percent: float = Field(..., description="Jitter (%)")
    shimmer_db: float = Field(..., description="Shimmer (dB)")
    
    # 종합 건강 점수
    overall_health_score: float = Field(..., description="종합 건강 점수 (0-100)")
    temperament: str = Field(..., description="디지털 기질 타입")
    confidence: float = Field(..., description="분석 신뢰도 (0-1)")
    
    # 메타데이터
    analysis_duration: float = Field(..., description="분석 소요 시간 (초)")
    created_at: datetime = Field(default_factory=datetime.now)


class MeasurementPair(BaseModel):
    """30분 전후 측정 페어 모델"""
    pair_id: str = Field(..., description="페어 ID")
    before_measurement: UserMeasurement = Field(..., description="복용 전 측정")
    after_measurement: UserMeasurement = Field(..., description="복용 후 측정")
    time_interval_minutes: float = Field(..., description="측정 간격 (분)")
    created_at: datetime = Field(default_factory=datetime.now)


class ComparisonResult(BaseModel):
    """측정 페어 비교 분석 결과 모델"""
    pair_id: str = Field(..., description="페어 ID")
    before_measurement: UserMeasurement = Field(..., description="복용 전 측정")
    after_measurement: UserMeasurement = Field(..., description="복용 후 측정")
    time_interval_minutes: float = Field(..., description="측정 간격 (분)")
    
    # 변화량 데이터
    changes: Dict[str, Dict[str, float]] = Field(..., description="각 지표별 변화량")
    improvement_rate: float = Field(..., description="개선률 (%)")
    overall_assessment: str = Field(..., description="전체 평가 결과")
    
    created_at: datetime = Field(default_factory=datetime.now)


class UserMeasurementSummary(BaseModel):
    """사용자 측정 요약 정보"""
    user_id: str = Field(..., description="사용자 ID")
    total_measurements: int = Field(..., description="총 측정 횟수")
    total_pairs: int = Field(..., description="총 측정 페어 수")
    average_improvement_rate: float = Field(..., description="평균 개선률 (%)")
    last_measurement_date: Optional[datetime] = Field(None, description="마지막 측정 날짜")
    created_at: datetime = Field(default_factory=datetime.now)
