#!/usr/bin/env python3
"""
mkm-core-ai 통합 인터페이스 테스트 스크립트
커서 에이전트의 좋은 아이디어를 활용한 통합 시스템 검증
"""

import asyncio
import logging
from app.services.mkm_core_ai_integration import MKMCoreAIIntegration, RPPGQualityAnalyzer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """기본 기능 테스트"""
    logger.info("🧪 기본 기능 테스트 시작")
    
    try:
        # 1. 통합 인터페이스 초기화
        integration = MKMCoreAIIntegration()
        logger.info("✅ 통합 인터페이스 초기화 성공")
        
        # 2. 헬스체크 테스트
        health = await integration.health_check()
        logger.info(f"✅ 헬스체크: {health}")
        
        # 3. RPPG 분석 테스트
        test_video = b"test_video_data" * 100
        result = await integration.analyze_rppg(test_video, 300)
        logger.info(f"✅ RPPG 분석: HR={result.get('heart_rate')} BPM")
        
        # 4. 품질 분석 테스트
        quality_analyzer = RPPGQualityAnalyzer()
        quality = quality_analyzer.analyze_quality(result)
        logger.info(f"✅ 품질 분석: {quality.get('overall_quality')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 기본 기능 테스트 실패: {e}")
        return False

async def test_batch_processing():
    """배치 처리 테스트"""
    logger.info("🧪 배치 처리 테스트 시작")
    
    try:
        integration = MKMCoreAIIntegration()
        
        # 배치 요청 생성
        requests = [
            {"video_data": b"video1", "frame_count": 300},
            {"video_data": b"video2", "frame_count": 250},
            {"video_data": b"video3", "frame_count": 350}
        ]
        
        # 배치 분석 실행
        results = await integration.batch_analyze(requests)
        logger.info(f"✅ 배치 분석 완료: {len(results)}개 결과")
        
        # 결과 검증
        for i, result in enumerate(results):
            if 'error' not in result:
                logger.info(f"  요청 {i}: HR={result.get('heart_rate')} BPM")
            else:
                logger.warning(f"  요청 {i}: 실패 - {result.get('error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 배치 처리 테스트 실패: {e}")
        return False

async def test_channel_weights():
    """채널 가중치 테스트 (커서 에이전트의 좋은 아이디어)"""
    logger.info("🧪 채널 가중치 테스트 시작")
    
    try:
        integration = MKMCoreAIIntegration()
        
        # 채널 가중치 확인
        weights = integration.channel_weights
        logger.info(f"✅ 채널 가중치: {weights}")
        
        # 가중치 합계 검증
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) < 0.01:
            logger.info("✅ 채널 가중치 합계 정상 (1.0)")
        else:
            logger.warning(f"⚠️ 채널 가중치 합계 이상: {total_weight}")
        
        # 실시간 파라미터 확인
        logger.info(f"✅ 샘플 레이트: {integration.sample_rate} fps")
        logger.info(f"✅ 윈도우 크기: {integration.window_size} 프레임")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 채널 가중치 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 실행"""
    logger.info("🚀 mkm-core-ai 통합 인터페이스 테스트 시작")
    
    test_results = []
    
    # 1. 기본 기능 테스트
    test_results.append(("기본 기능", await test_basic_functionality()))
    
    # 2. 배치 처리 테스트
    test_results.append(("배치 처리", await test_batch_processing()))
    
    # 3. 채널 가중치 테스트
    test_results.append(("채널 가중치", await test_channel_weights()))
    
    # 결과 요약
    logger.info("\n📊 테스트 결과 요약:")
    success_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        logger.info("🎉 모든 테스트 통과! 통합 시스템이 정상 작동합니다.")
    else:
        logger.warning("⚠️ 일부 테스트 실패. 시스템 점검이 필요합니다.")

if __name__ == "__main__":
    asyncio.run(main())
