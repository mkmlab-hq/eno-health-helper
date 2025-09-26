#!/usr/bin/env python3
"""
통합 워크플로우 테스트 스크립트
전체 건강 분석 워크플로우를 검증합니다.
"""

import asyncio
import time
import logging
from typing import Dict, List
import json

from app.services.mkm_core_ai_integration import MKMCoreAIIntegration
from app.services.voice_analyzer import VoiceAnalyzer
from app.services.fusion_analyzer import AdvancedFusionAnalyzer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowTester:
    """워크플로우 테스터"""
    
    def __init__(self):
        self.rppg_analyzer = MKMCoreAIIntegration()
        self.voice_analyzer = VoiceAnalyzer()
        self.fusion_analyzer = AdvancedFusionAnalyzer()
        self.test_results = []
    
    async def test_rppg_workflow(self) -> Dict:
        """RPPG 워크플로우 테스트"""
        logger.info("📹 RPPG 워크플로우 테스트 시작")
        
        start_time = time.time()
        
        try:
            # 1단계: RPPG 분석
            rppg_result = await self.rppg_analyzer.analyze_rppg(
                video_data=b"simulated_video_data",
                frame_count=300
            )
            
            # 2단계: 품질 분석
            quality_result = await self.rppg_analyzer.analyze_quality(rppg_result)
            
            workflow_time = time.time() - start_time
            
            result = {
                'workflow': 'RPPG Analysis',
                'status': 'success',
                'duration': workflow_time,
                'rppg_data': rppg_result,
                'quality_score': quality_result.get('quality_score', 0),
                'error': None
            }
            
            logger.info(f"✅ RPPG 워크플로우 완료: {workflow_time:.3f}초, "
                       f"품질점수: {quality_result.get('quality_score', 0):.2f}")
            
        except Exception as e:
            workflow_time = time.time() - start_time
            result = {
                'workflow': 'RPPG Analysis',
                'status': 'failed',
                'duration': workflow_time,
                'rppg_data': None,
                'quality_score': 0,
                'error': str(e)
            }
            logger.error(f"❌ RPPG 워크플로우 실패: {e}")
        
        return result
    
    async def test_voice_workflow(self) -> Dict:
        """음성 분석 워크플로우 테스트"""
        logger.info("🎵 음성 분석 워크플로우 테스트 시작")
        
        start_time = time.time()
        
        try:
            # 1단계: 음성 분석
            voice_result = await self.voice_analyzer.analyze_voice(
                audio_data=b"simulated_audio_data"
            )
            
            workflow_time = time.time() - start_time
            
            result = {
                'workflow': 'Voice Analysis',
                'status': 'success',
                'duration': workflow_time,
                'voice_data': voice_result,
                'error': None
            }
            
            logger.info(f"✅ 음성 분석 워크플로우 완료: {workflow_time:.3f}초")
            
        except Exception as e:
            workflow_time = time.time() - start_time
            result = {
                'workflow': 'Voice Analysis',
                'status': 'failed',
                'duration': workflow_time,
                'voice_data': None,
                'error': str(e)
            }
            logger.error(f"❌ 음성 분석 워크플로우 실패: {e}")
        
        return result
    
    async def test_fusion_workflow(self) -> Dict:
        """융합 분석 워크플로우 테스트"""
        logger.info("🔗 융합 분석 워크플로우 테스트 시작")
        
        start_time = time.time()
        
        try:
            # 1단계: RPPG 데이터 준비
            rppg_data = {
                'hr': 72.0,
                'hrv': 45.2,
                'stress_level': 0.3,
                'confidence': 0.85,
                'timestamp': time.time()
            }
            
            # 2단계: 음성 데이터 준비
            voice_data = {
                'f0': 180.5,
                'jitter': 0.02,
                'shimmer': 0.15,
                'hnr': 12.5,
                'confidence': 0.90,
                'timestamp': time.time()
            }
            
            # 3단계: 융합 분석
            fusion_result = await self.fusion_analyzer.analyze_fusion(
                rppg_data=rppg_data,
                voice_data=voice_data
            )
            
            workflow_time = time.time() - start_time
            
            result = {
                'workflow': 'Fusion Analysis',
                'status': 'success',
                'duration': workflow_time,
                'fusion_data': fusion_result,
                'error': None
            }
            
            logger.info(f"✅ 융합 분석 워크플로우 완료: {workflow_time:.3f}초")
            
        except Exception as e:
            workflow_time = time.time() - start_time
            result = {
                'workflow': 'Fusion Analysis',
                'status': 'failed',
                'duration': workflow_time,
                'fusion_data': None,
                'error': str(e)
            }
            logger.error(f"❌ 융합 분석 워크플로우 실패: {e}")
        
        return result
    
    async def test_end_to_end_workflow(self) -> Dict:
        """전체 워크플로우 테스트"""
        logger.info("🚀 전체 워크플로우 테스트 시작")
        
        start_time = time.time()
        
        try:
            # 1단계: RPPG 분석
            rppg_result = await self.test_rppg_workflow()
            
            # 2단계: 음성 분석
            voice_result = await self.test_voice_workflow()
            
            # 3단계: 융합 분석 (성공한 경우에만)
            if (rppg_result['status'] == 'success' and 
                voice_result['status'] == 'success'):
                
                # 실제 데이터로 융합 분석
                fusion_result = await self.fusion_analyzer.analyze_fusion(
                    rppg_data=rppg_result['rppg_data'],
                    voice_data=voice_result['voice_data']
                )
            else:
                fusion_result = None
            
            total_time = time.time() - start_time
            
            result = {
                'workflow': 'End-to-End Health Analysis',
                'status': 'success' if all(r['status'] == 'success' for r in [rppg_result, voice_result]) else 'partial',
                'duration': total_time,
                'components': {
                    'rppg': rppg_result,
                    'voice': voice_result,
                    'fusion': fusion_result
                },
                'error': None
            }
            
            logger.info(f"✅ 전체 워크플로우 완료: {total_time:.3f}초")
            
        except Exception as e:
            total_time = time.time() - start_time
            result = {
                'workflow': 'End-to-End Health Analysis',
                'status': 'failed',
                'duration': total_time,
                'components': {},
                'error': str(e)
            }
            logger.error(f"❌ 전체 워크플로우 실패: {e}")
        
        return result
    
    def generate_workflow_report(self, results: List[Dict]) -> str:
        """워크플로우 테스트 보고서 생성"""
        logger.info("📋 워크플로우 테스트 보고서 생성 중...")
        
        # 통계 계산
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['status'] == 'success')
        failed_tests = sum(1 for r in results if r['status'] == 'failed')
        partial_tests = sum(1 for r in results if r['status'] == 'partial')
        
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # 평균 처리 시간
        successful_durations = [r['duration'] for r in results if r['status'] == 'success']
        avg_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0
        
        report = f"""
🎯 **엔오건강도우미 워크플로우 테스트 보고서**

📊 **전체 테스트 결과**
• 총 테스트: {total_tests}개
• 성공: {successful_tests}개
• 부분 성공: {partial_tests}개
• 실패: {failed_tests}개
• 성공률: {success_rate:.1%}

⏱️ **성능 지표**
• 평균 처리 시간: {avg_duration:.3f}초
• 최고 처리 시간: {max(r['duration'] for r in results):.3f}초
• 최저 처리 시간: {min(r['duration'] for r in results):.3f}초

🔍 **개별 워크플로우 결과**
"""
        
        for result in results:
            status_emoji = "✅" if result['status'] == 'success' else "⚠️" if result['status'] == 'partial' else "❌"
            report += f"""
• {status_emoji} {result['workflow']}:
  - 상태: {result['status']}
  - 처리 시간: {result['duration']:.3f}초
  - 오류: {result['error'] or '없음'}
"""
        
        # 전체 시스템 평가
        if success_rate >= 0.9:
            system_status = "✅ 우수"
        elif success_rate >= 0.7:
            system_status = "🔄 양호"
        elif success_rate >= 0.5:
            system_status = "⚠️ 보통"
        else:
            system_status = "❌ 불량"
        
        report += f"""

🎯 **시스템 전체 평가**
• 시스템 상태: {system_status}
• 안정성: {'✅ 안정' if success_rate >= 0.8 else '⚠️ 불안정' if success_rate < 0.6 else '🔄 보통'}
• 성능: {'✅ 우수' if avg_duration < 1.0 else '🔄 양호' if avg_duration < 3.0 else '⚠️ 보통'}

📋 **권장 조치사항**
"""
        
        if failed_tests > 0:
            report += "• 실패한 워크플로우의 오류 원인 분석 및 수정 필요\n"
        
        if avg_duration > 3.0:
            report += "• 워크플로우 처리 시간 최적화 필요\n"
        
        if success_rate < 0.8:
            report += "• 시스템 안정성 향상을 위한 추가 테스트 및 디버깅 필요\n"
        
        if success_rate >= 0.9 and avg_duration < 2.0:
            report += "• 시스템이 목표 성능을 달성했습니다. 프로덕션 배포 준비 완료\n"
        
        return report

async def main():
    """메인 함수"""
    logger.info("🚀 워크플로우 테스트 시작")
    
    tester = WorkflowTester()
    
    # 개별 워크플로우 테스트
    results = []
    
    # RPPG 워크플로우 테스트
    rppg_result = await tester.test_rppg_workflow()
    results.append(rppg_result)
    
    # 음성 분석 워크플로우 테스트
    voice_result = await tester.test_voice_workflow()
    results.append(voice_result)
    
    # 융합 분석 워크플로우 테스트
    fusion_result = await tester.test_fusion_workflow()
    results.append(fusion_result)
    
    # 전체 워크플로우 테스트
    e2e_result = await tester.test_end_to_end_workflow()
    results.append(e2e_result)
    
    # 보고서 생성
    report = tester.generate_workflow_report(results)
    print(report)
    
    # 결과 저장
    with open('workflow_test_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("✅ 워크플로우 테스트 완료 - workflow_test_report.txt 저장됨")

if __name__ == "__main__":
    asyncio.run(main())
