#!/usr/bin/env python3
"""
Phase 3 통합 테스트 - '불사조 엔진' 웹 앱 통합 검증
"""

import requests
import json
import time
import logging
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase3IntegrationTester:
    """Phase 3 통합 테스트기"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_prefix = "/api/v1"
        self.test_results = {}
        
    def test_server_health(self) -> bool:
        """서버 상태 확인"""
        try:
            logger.info("🔍 서버 상태 확인 중...")
            response = requests.get(f"{self.base_url}{self.api_prefix}/ping", timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ 서버 정상 작동")
                return True
            else:
                logger.error(f"❌ 서버 오류: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ 서버 연결 실패 - 서버가 실행 중인지 확인하세요")
            return False
        except Exception as e:
            logger.error(f"❌ 서버 상태 확인 실패: {e}")
            return False
    
    def test_combined_measurement_api(self) -> bool:
        """통합 측정 API 테스트"""
        try:
            logger.info("🧪 통합 측정 API 테스트 시작...")
            
            # 테스트용 더미 데이터 생성
            test_video_data = b"dummy_video_data_for_testing"
            test_audio_data = b"dummy_audio_data_for_testing"
            test_user_id = "test_user_123"
            
            # FormData 구성
            files = {
                'video_file': ('test_video.mp4', test_video_data, 'video/mp4'),
                'audio_file': ('test_audio.wav', test_audio_data, 'audio/wav')
            }
            data = {
                'user_id': test_user_id
            }
            
            # API 호출
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/measure/combined",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ 통합 측정 API 성공!")
                logger.info(f"   측정 ID: {result.get('measurement_id', 'N/A')}")
                logger.info(f"   건강 점수: {result.get('health_score', 'N/A')}")
                logger.info(f"   엔진 버전: {result.get('engine_version', 'N/A')}")
                
                # RPPG 결과 확인
                rppg_result = result.get('rppg_result', {})
                logger.info(f"   RPPG - HR: {rppg_result.get('heart_rate', 'N/A')} BPM")
                logger.info(f"   RPPG - 품질: {rppg_result.get('signal_quality', 'N/A')}")
                
                # 음성 결과 확인
                voice_result = result.get('voice_result', {})
                logger.info(f"   음성 - F0: {voice_result.get('f0', 'N/A')} Hz")
                logger.info(f"   음성 - Jitter: {voice_result.get('jitter', 'N/A')}")
                
                self.test_results['combined_api'] = {
                    'status': 'success',
                    'result': result
                }
                return True
                
            else:
                logger.error(f"❌ 통합 측정 API 실패: {response.status_code}")
                logger.error(f"   응답: {response.text}")
                self.test_results['combined_api'] = {
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ 통합 측정 API 테스트 실패: {e}")
            self.test_results['combined_api'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_frontend_integration(self) -> bool:
        """프론트엔드 통합 테스트"""
        try:
            logger.info("🌐 프론트엔드 통합 테스트 시작...")
            
            # 프론트엔드 서버 상태 확인
            frontend_url = "http://localhost:3000"
            response = requests.get(frontend_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ 프론트엔드 서버 정상 작동")
                
                # 측정 페이지 접근 테스트
                measure_page_url = f"{frontend_url}/measure"
                measure_response = requests.get(measure_page_url, timeout=10)
                
                if measure_response.status_code == 200:
                    logger.info("✅ 측정 페이지 접근 성공")
                    self.test_results['frontend_integration'] = {
                        'status': 'success',
                        'frontend_server': 'running',
                        'measure_page': 'accessible'
                    }
                    return True
                else:
                    logger.error(f"❌ 측정 페이지 접근 실패: {measure_response.status_code}")
                    self.test_results['frontend_integration'] = {
                        'status': 'failed',
                        'frontend_server': 'running',
                        'measure_page': 'inaccessible'
                    }
                    return False
            else:
                logger.error(f"❌ 프론트엔드 서버 오류: {response.status_code}")
                self.test_results['frontend_integration'] = {
                    'status': 'failed',
                    'frontend_server': 'not_running'
                }
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ 프론트엔드 서버 연결 실패")
            self.test_results['frontend_integration'] = {
                'status': 'failed',
                'frontend_server': 'connection_failed'
            }
            return False
        except Exception as e:
            logger.error(f"❌ 프론트엔드 통합 테스트 실패: {e}")
            self.test_results['frontend_integration'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """End-to-End 워크플로우 테스트"""
        try:
            logger.info("🔄 End-to-End 워크플로우 테스트 시작...")
            
            # 1단계: 서버 상태 확인
            if not self.test_server_health():
                return False
            
            # 2단계: API 테스트
            if not self.test_combined_measurement_api():
                return False
            
            # 3단계: 프론트엔드 통합 테스트
            if not self.test_frontend_integration():
                return False
            
            logger.info("🎉 End-to-End 워크플로우 테스트 완료!")
            return True
            
        except Exception as e:
            logger.error(f"❌ End-to-End 테스트 실패: {e}")
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """테스트 결과 보고서 생성"""
        logger.info("📊 테스트 결과 보고서 생성 중...")
        
        # 성공률 계산
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() 
                             if result.get('status') == 'success')
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": round(success_rate, 1)
            },
            "test_details": self.test_results,
            "phase": "Phase 3 - 웹 앱 통합",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "engine_version": "불사조_엔진_v2.0"
        }
        
        return report
    
    def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        logger.info("🚀 Phase 3 통합 테스트 시작")
        logger.info("=" * 60)
        
        try:
            # 전체 워크플로우 테스트
            success = self.test_end_to_end_workflow()
            
            # 결과 보고서 생성
            report = self.generate_test_report()
            
            logger.info("\n" + "=" * 60)
            logger.info("📋 Phase 3 테스트 결과 요약")
            logger.info("=" * 60)
            
            summary = report['test_summary']
            logger.info(f"총 테스트: {summary['total_tests']}개")
            logger.info(f"성공: {summary['successful_tests']}개")
            logger.info(f"실패: {summary['failed_tests']}개")
            logger.info(f"성공률: {summary['success_rate']}%")
            
            if success:
                logger.info("🎉 Phase 3 통합 테스트 성공!")
                logger.info("✅ '불사조 엔진'이 웹 앱에 성공적으로 통합되었습니다!")
            else:
                logger.error("❌ Phase 3 통합 테스트 실패")
                logger.error("일부 테스트에서 문제가 발생했습니다.")
            
            # 상세 결과 출력
            logger.info("\n📊 상세 테스트 결과:")
            for test_name, result in self.test_results.items():
                status = "✅ 성공" if result.get('status') == 'success' else "❌ 실패"
                logger.info(f"   {test_name}: {status}")
                if result.get('status') == 'failed' and 'error' in result:
                    logger.error(f"      오류: {result['error']}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 테스트 실행 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    tester = Phase3IntegrationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            logger.info("✅ Phase 3 통합 테스트 완료!")
            return True
        else:
            logger.error("❌ Phase 3 통합 테스트 실패!")
            return False
            
    except Exception as e:
        logger.error(f"❌ 테스트 실행 실패: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
