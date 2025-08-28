#!/usr/bin/env python3
"""
실제 분석 엔진 테스트 스크립트
"""

import sys
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """분석 엔진 import 테스트"""
    try:
        logger.info("🔍 분석 엔진 import 테스트 시작...")
        
        # Enhanced RPPG Analyzer
        from enhanced_rppg_analyzer import EnhancedRPPGAnalyzer
        logger.info("✅ EnhancedRPPGAnalyzer import 성공")
        
        # Voice Analyzer
        from voice_analyzer import VoiceAnalyzer
        logger.info("✅ VoiceAnalyzer import 성공")
        
        # Fusion Analyzer
        from fusion_analyzer import AdvancedFusionAnalyzer
        logger.info("✅ AdvancedFusionAnalyzer import 성공")
        
        # Signal Quality Validator
        from signal_quality_validator import SignalQualityValidator
        logger.info("✅ SignalQualityValidator import 성공")
        
        # Error Handler
        from error_handler import MeasurementErrorHandler
        logger.info("✅ MeasurementErrorHandler import 성공")
        
        # Measurement Protocol Manager
        from measurement_protocol_manager import MeasurementProtocolManager
        logger.info("✅ MeasurementProtocolManager import 성공")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import 실패: {e}")
        return False

def test_initialization():
    """분석 엔진 초기화 테스트"""
    try:
        logger.info("🔧 분석 엔진 초기화 테스트 시작...")
        
        # Enhanced RPPG Analyzer 초기화
        from enhanced_rppg_analyzer import EnhancedRPPGAnalyzer
        rppg_analyzer = EnhancedRPPGAnalyzer()
        logger.info("✅ EnhancedRPPGAnalyzer 초기화 성공")
        
        # Voice Analyzer 초기화
        from voice_analyzer import VoiceAnalyzer
        voice_analyzer = VoiceAnalyzer()
        logger.info("✅ VoiceAnalyzer 초기화 성공")
        
        # Fusion Analyzer 초기화
        from fusion_analyzer import AdvancedFusionAnalyzer
        fusion_analyzer = AdvancedFusionAnalyzer()
        logger.info("✅ AdvancedFusionAnalyzer 초기화 성공")
        
        # Signal Quality Validator 초기화
        from signal_quality_validator import SignalQualityValidator
        quality_validator = SignalQualityValidator()
        logger.info("✅ SignalQualityValidator 초기화 성공")
        
        # Error Handler 초기화
        from error_handler import MeasurementErrorHandler
        error_handler = MeasurementErrorHandler()
        logger.info("✅ MeasurementErrorHandler 초기화 성공")
        
        # Measurement Protocol Manager 초기화
        from measurement_protocol_manager import MeasurementProtocolManager
        protocol_manager = MeasurementProtocolManager()
        logger.info("✅ MeasurementProtocolManager 초기화 성공")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 초기화 실패: {e}")
        return False

def test_basic_functionality():
    """기본 기능 테스트"""
    try:
        logger.info("🧪 기본 기능 테스트 시작...")
        
        # RPPG 분석기 테스트
        from enhanced_rppg_analyzer import EnhancedRPPGAnalyzer
        rppg_analyzer = EnhancedRPPGAnalyzer()
        
        # 측정 세션 시작 테스트
        session_result = rppg_analyzer.start_measurement_session("quick_check")
        logger.info(f"✅ 측정 세션 시작: {session_result.get('status', 'unknown')}")
        
        # Voice 분석기 테스트
        from voice_analyzer import VoiceAnalyzer
        voice_analyzer = VoiceAnalyzer()
        
        # 시뮬레이션 음성 분석 테스트
        import asyncio
        voice_result = asyncio.run(voice_analyzer.analyze_voice(b"test_audio_data"))
        logger.info(f"✅ 음성 분석 테스트: F0={voice_result.get('f0', 'N/A')} Hz")
        
        # Fusion 분석기 테스트
        from fusion_analyzer import AdvancedFusionAnalyzer
        fusion_analyzer = AdvancedFusionAnalyzer()
        
        # 기본 융합 분석 테스트
        test_rppg_data = {"heart_rate": 72, "hrv": 45.2}
        test_voice_data = {"f0": 120.5, "jitter": 0.3}
        
        fusion_result = asyncio.run(fusion_analyzer.analyze_fusion(
            rppg_data=test_rppg_data,
            voice_data=test_voice_data
        ))
        logger.info(f"✅ 융합 분석 테스트: {fusion_result.get('digital_temperament', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 기본 기능 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    logger.info("🚀 실제 분석 엔진 테스트 시작")
    
    # 1단계: Import 테스트
    if not test_imports():
        logger.error("❌ Import 테스트 실패")
        return False
    
    # 2단계: 초기화 테스트
    if not test_initialization():
        logger.error("❌ 초기화 테스트 실패")
        return False
    
    # 3단계: 기본 기능 테스트
    if not test_basic_functionality():
        logger.error("❌ 기본 기능 테스트 실패")
        return False
    
    logger.info("🎉 모든 테스트 통과! 실제 분석 엔진이 정상적으로 작동합니다.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
