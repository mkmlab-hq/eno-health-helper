#!/usr/bin/env python3
"""
30분 전후 변화 확인 API 테스트 스크립트
"""

import asyncio
import json
from datetime import datetime, timedelta
from app.models.user_measurement import (
    UserMeasurement, MeasurementType, MeasurementPair
)
from app.services.firebase_service import FirebaseService

# 테스트용 사용자 ID
TEST_USER_ID = "test_user_001"

async def create_test_measurements():
    """테스트용 측정 데이터 생성"""
    
    # 현재 시간 기준으로 테스트 데이터 생성
    now = datetime.now()
    
    # 복용 전 측정 (30분 전)
    before_measurement = UserMeasurement(
        measurement_id="test_before_001",
        user_id=TEST_USER_ID,
        timestamp=now - timedelta(minutes=30),
        measurement_type=MeasurementType.BEFORE,
        heart_rate=75.0,
        hrv=45.0,
        stress_level=65.0,
        signal_quality=0.85,
        voice_stability=0.72,
        jitter_percent=2.1,
        shimmer_db=1.8,
        overall_health_score=68.0,
        temperament="B타입",
        confidence=0.88,
        analysis_duration=35.2
    )
    
    # 복용 후 측정 (현재)
    after_measurement = UserMeasurement(
        measurement_id="test_after_001",
        user_id=TEST_USER_ID,
        timestamp=now,
        measurement_type=MeasurementType.AFTER,
        heart_rate=71.0,
        hrv=52.0,
        stress_level=45.0,
        signal_quality=0.91,
        voice_stability=0.80,
        jitter_percent=1.8,
        shimmer_db=1.5,
        overall_health_score=74.0,
        temperament="B타입",
        confidence=0.92,
        analysis_duration=32.8
    )
    
    return before_measurement, after_measurement

async def test_measurement_pair_creation():
    """측정 페어 생성 테스트"""
    
    print("🧪 측정 페어 생성 테스트 시작...")
    
    # 테스트 데이터 생성
    before_measurement, after_measurement = await create_test_measurements()
    
    # 측정 페어 생성
    pair = MeasurementPair(
        pair_id="test_pair_001",
        before_measurement=before_measurement,
        after_measurement=after_measurement,
        time_interval_minutes=30.0,
        created_at=datetime.now()
    )
    
    print(f"✅ 측정 페어 생성 완료:")
    print(f"   - 페어 ID: {pair.pair_id}")
    print(f"   - 시간 간격: {pair.time_interval_minutes}분")
    print(f"   - 복용 전 점수: {pair.before_measurement.overall_health_score}")
    print(f"   - 복용 후 점수: {pair.after_measurement.overall_health_score}")
    
    return pair

async def test_comparison_analysis():
    """비교 분석 테스트"""
    
    print("\n🧪 비교 분석 테스트 시작...")
    
    # 측정 페어 생성
    pair = await test_measurement_pair_creation()
    
    # 변화량 계산
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
    
    print(f"✅ 비교 분석 완료:")
    print(f"   - 개선률: {improvement_rate:.1f}%")
    print(f"   - 개선된 지표: {improvement_count}/{total_metrics}")
    
    # 각 지표별 변화량 출력
    for metric_name, metric_data in changes.items():
        change = metric_data["change"]
        change_percent = metric_data["change_percentage"]
        direction = "▲" if change > 0 else "▼" if change < 0 else "─"
        
        print(f"   - {metric_name}: {direction} {change:+.1f} ({change_percent:+.1f}%)")
    
    return changes, improvement_rate

async def test_api_endpoints():
    """API 엔드포인트 테스트"""
    
    print("\n🧪 API 엔드포인트 테스트 시작...")
    
    # Firebase 서비스 초기화 (테스트용)
    try:
        firebase_service = FirebaseService()
        print("✅ Firebase 서비스 초기화 성공")
    except Exception as e:
        print(f"❌ Firebase 서비스 초기화 실패: {e}")
        return
    
    # 테스트 데이터 생성
    before_measurement, after_measurement = await create_test_measurements()
    
    # 측정 페어 생성
    pair = MeasurementPair(
        pair_id="test_pair_001",
        before_measurement=before_measurement,
        after_measurement=after_measurement,
        time_interval_minutes=30.0,
        created_at=datetime.now()
    )
    
    # 측정 페어 저장 테스트
    try:
        save_success = await firebase_service.save_measurement_pair(pair)
        if save_success:
            print("✅ 측정 페어 저장 성공")
        else:
            print("❌ 측정 페어 저장 실패")
    except Exception as e:
        print(f"❌ 측정 페어 저장 중 오류: {e}")
    
    # 측정 페어 조회 테스트
    try:
        retrieved_pair = await firebase_service.get_measurement_pair(TEST_USER_ID, "test_pair_001")
        if retrieved_pair:
            print("✅ 측정 페어 조회 성공")
        else:
            print("❌ 측정 페어 조회 실패")
    except Exception as e:
        print(f"❌ 측정 페어 조회 중 오류: {e}")

async def main():
    """메인 테스트 함수"""
    
    print("🚀 30분 전후 변화 확인 API 테스트 시작")
    print("=" * 50)
    
    try:
        # 1. 측정 페어 생성 테스트
        await test_measurement_pair_creation()
        
        # 2. 비교 분석 테스트
        await test_comparison_analysis()
        
        # 3. API 엔드포인트 테스트
        await test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # asyncio 이벤트 루프 실행
    asyncio.run(main())
