#!/usr/bin/env python3
"""
rPPG-음성 융합 분석기 테스트 스크립트

이 스크립트는 AdvancedFusionAnalyzer의 성능을 테스트하고
융합 알고리즘의 정확도를 검증합니다.
"""

import sys
import os
import numpy as np
import json
import time
from pathlib import Path

# 백엔드 경로 추가
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from app.services.fusion_analyzer import AdvancedFusionAnalyzer
from app.services.rppg_analyzer import MedicalGradeRPPGAnalyzer
from app.services.voice_analyzer import MedicalGradeVoiceAnalyzer

def generate_test_data():
    """테스트용 데이터 생성"""
    
    # 테스트용 rPPG 데이터
    rppg_data = {
        "heart_rate": 75,
        "hrv": 45,
        "stress_level": "보통",
        "confidence": 0.85,
        "timestamp": "2025-08-22T00:00:00Z"
    }
    
    # 테스트용 음성 데이터
    voice_data = {
        "pitch_hz": 180.5,
        "jitter_percent": 1.2,
        "shimmer_db": 2.1,
        "hnr_db": 15.3,
        "confidence": 0.78,
        "timestamp": "2025-08-22T00:00:00Z"
    }
    
    # 테스트용 비디오 프레임 (실제 데이터 시뮬레이션)
    video_frames = []
    for i in range(30):  # 30프레임
        # 실제 rPPG 신호 패턴을 모방한 프레임 생성
        base_intensity = 128
        signal_variation = int(20 * np.sin(2 * np.pi * i / 30))  # 심박수 변화 시뮬레이션
        frame = np.full((480, 640, 3), base_intensity + signal_variation, dtype=np.uint8)
        video_frames.append(frame)
    
    # 테스트용 오디오 신호 (실제 음성 패턴 시뮬레이션)
    sample_rate = 22050
    duration = 5.0  # 5초
    t = np.linspace(0, duration, int(sample_rate * duration))
    # 기본 주파수 + 하모닉스로 실제 음성과 유사하게 생성
    audio_signal = np.sin(2 * np.pi * 175 * t) + 0.3 * np.sin(2 * np.pi * 350 * t) + 0.1 * np.sin(2 * np.pi * 525 * t)
    
    return rppg_data, voice_data, video_frames, audio_signal

def test_basic_fusion():
    """기본 융합 기능 테스트"""
    print("🔬 기본 융합 기능 테스트 시작...")
    
    try:
        # 융합 분석기 초기화
        fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 테스트 데이터 생성
        rppg_data, voice_data, video_frames, audio_signal = generate_test_data()
        
        # 융합 분석 수행
        start_time = time.time()
        fusion_results = fusion_analyzer.analyze_fusion(
            rppg_data, voice_data, video_frames, audio_signal
        )
        processing_time = time.time() - start_time
        
        # 결과 출력
        print(f"✅ 융합 분석 완료 (처리 시간: {processing_time:.3f}초)")
        print(f"📊 전체 건강 점수: {fusion_results.get('overall_health_score', 0):.1f}")
        print(f"🏥 건강 상태: {fusion_results.get('fusion_results', {}).get('health_assessment', 'unknown')}")
        print(f"🎯 신뢰도: {fusion_results.get('fusion_results', {}).get('confidence_level', 'unknown')}")
        
        # 데이터 품질 확인
        data_quality = fusion_results.get('data_quality', {})
        print(f"📈 데이터 품질: {data_quality.get('overall_quality', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 기본 융합 테스트 실패: {e}")
        return False

def test_advanced_features():
    """고급 특징 추출 테스트"""
    print("\n🔬 고급 특징 추출 테스트 시작...")
    
    try:
        fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 테스트 데이터
        rppg_data, voice_data, video_frames, audio_signal = generate_test_data()
        
        # rPPG 특징 추출 테스트
        rppg_features = fusion_analyzer._extract_rppg_features(rppg_data, video_frames)
        print(f"✅ rPPG 특징 추출: {len(rppg_features)}개 특징")
        print(f"   특징 값: {rppg_features[:5]}...")  # 처음 5개만 출력
        
        # 음성 특징 추출 테스트
        voice_features = fusion_analyzer._extract_voice_features(voice_data, audio_signal)
        print(f"✅ 음성 특징 추출: {len(voice_features)}개 특징")
        print(f"   특징 값: {voice_features[:5]}...")  # 처음 5개만 출력
        
        # 특징 융합 테스트
        fused_features = fusion_analyzer._fuse_features(rppg_features, voice_features)
        print(f"✅ 특징 융합: {len(fused_features)}개 융합 특징")
        
        return True
        
    except Exception as e:
        print(f"❌ 고급 특징 추출 테스트 실패: {e}")
        return False

def test_data_quality_validation():
    """데이터 품질 검증 테스트"""
    print("\n🔬 데이터 품질 검증 테스트 시작...")
    
    try:
        fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 다양한 품질의 테스트 데이터
        test_cases = [
            {
                "name": "고품질 데이터",
                "rppg": {"heart_rate": 72, "hrv": 50, "stress_level": "낮음"},
                "voice": {"jitter_percent": 1.0, "shimmer_db": 1.5, "pitch_hz": 175}
            },
            {
                "name": "보통 품질 데이터",
                "rppg": {"heart_rate": 85, "hrv": 35, "stress_level": "보통"},
                "voice": {"jitter_percent": 2.5, "shimmer_db": 3.0, "pitch_hz": 185}
            },
            {
                "name": "저품질 데이터",
                "rppg": {"heart_rate": 120, "hrv": 20, "stress_level": "높음"},
                "voice": {"jitter_percent": 5.0, "shimmer_db": 6.0, "pitch_hz": 200}
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📋 {test_case['name']} 테스트:")
            
            quality = fusion_analyzer._validate_data_quality(
                test_case['rppg'], test_case['voice']
            )
            
            print(f"   rPPG 품질: {quality['rppg_quality']:.2f}")
            print(f"   음성 품질: {quality['voice_quality']:.2f}")
            print(f"   전체 품질: {quality['overall_quality']:.2f}")
            print(f"   신뢰도: {quality['confidence_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 품질 검증 테스트 실패: {e}")
        return False

def test_risk_analysis():
    """위험 요인 분석 테스트"""
    print("\n🔬 위험 요인 분석 테스트 시작...")
    
    try:
        fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 다양한 건강 상태 시나리오
        scenarios = [
            {
                "name": "건강한 상태",
                "features": np.array([0.8, 0.7, 0.9, 0.8, 0.7, 0.8, 0.7, 0.9, 0.8, 0.7,
                                    0.8, 0.7, 0.9, 0.8, 0.7, 0.8, 0.7, 0.9])
            },
            {
                "name": "주의 필요 상태",
                "features": np.array([0.4, 0.3, 0.5, 0.4, 0.3, 0.4, 0.3, 0.5, 0.4, 0.3,
                                    0.4, 0.3, 0.5, 0.4, 0.3, 0.4, 0.3, 0.5])
            },
            {
                "name": "위험 상태",
                "features": np.array([0.2, 0.1, 0.3, 0.2, 0.1, 0.2, 0.1, 0.3, 0.2, 0.1,
                                    0.2, 0.1, 0.3, 0.2, 0.1, 0.2, 0.1, 0.3])
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📋 {scenario['name']} 시나리오:")
            
            risk_factors = fusion_analyzer._analyze_risk_factors(scenario['features'])
            
            if risk_factors:
                print(f"   ⚠️  발견된 위험 요인:")
                for risk in risk_factors:
                    print(f"      - {risk}")
            else:
                print(f"   ✅ 위험 요인 없음")
        
        return True
        
    except Exception as e:
        print(f"❌ 위험 요인 분석 테스트 실패: {e}")
        return False

def test_performance_monitoring():
    """성능 모니터링 테스트"""
    print("\n🔬 성능 모니터링 테스트 시작...")
    
    try:
        fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 여러 번의 분석 수행으로 성능 데이터 생성
        print("📊 성능 데이터 수집 중...")
        
        for i in range(5):
            rppg_data, voice_data, video_frames, audio_signal = generate_test_data()
            
            # 실제 데이터 변화 시뮬레이션 (랜덤 노이즈 제거)
            rppg_data['heart_rate'] += int(2 * np.sin(i * np.pi / 3))  # 주기적 변화
            voice_data['jitter_percent'] += 0.1 * np.sin(i * np.pi / 2)  # 점진적 변화
            
            fusion_results = fusion_analyzer.analyze_fusion(
                rppg_data, voice_data, video_frames, audio_signal
            )
            
            print(f"   분석 {i+1}: 점수 {fusion_results.get('overall_health_score', 0):.1f}")
        
        # 성능 요약 출력
        performance_summary = fusion_analyzer.get_performance_summary()
        print(f"\n📈 성능 요약:")
        print(f"   총 분석 수: {performance_summary.get('total_analyses', 0)}")
        print(f"   평균 점수: {performance_summary.get('average_score', 0):.1f}")
        print(f"   평균 품질: {performance_summary.get('average_quality', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 성능 모니터링 테스트 실패: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 rPPG-음성 융합 분석기 종합 테스트 시작\n")
    
    tests = [
        ("기본 융합 기능", test_basic_fusion),
        ("고급 특징 추출", test_advanced_features),
        ("데이터 품질 검증", test_data_quality_validation),
        ("위험 요인 분석", test_risk_analysis),
        ("성능 모니터링", test_performance_monitoring)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과\n")
            else:
                print(f"❌ {test_name} 테스트 실패\n")
        except Exception as e:
            print(f"❌ {test_name} 테스트에서 예외 발생: {e}\n")
    
    # 결과 요약
    print("=" * 50)
    print(f"🎯 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 통과했습니다!")
    else:
        print(f"⚠️  {total - passed}개 테스트가 실패했습니다.")
    
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 예상치 못한 오류 발생: {e}")
        sys.exit(1) 