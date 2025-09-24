#!/usr/bin/env python3
"""
부하 테스트 스크립트
동시 요청 처리 능력과 시스템 안정성을 측정합니다.
"""

import asyncio
import time
import statistics
import logging
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadTester:
    """부하 테스트기"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8002"):
        self.base_url = base_url
        self.results = []
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def single_request(self, endpoint: str, data: Dict = None) -> Dict:
        """단일 요청 실행"""
        start_time = time.time()
        
        try:
            if data:
                async with self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_time = time.time() - start_time
                    return {
                        'status': response.status,
                        'response_time': response_time,
                        'success': response.status < 400,
                        'error': None
                    }
            else:
                async with self.session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_time = time.time() - start_time
                    return {
                        'status': response.status,
                        'response_time': response_time,
                        'success': response.status < 400,
                        'error': None
                    }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'status': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e)
            }
    
    async def concurrent_requests(self, endpoint: str, concurrent_users: int, 
                                data: Dict = None) -> List[Dict]:
        """동시 요청 실행"""
        logger.info(f"🚀 {concurrent_users}명 동시 사용자 테스트 시작: {endpoint}")
        
        tasks = []
        for i in range(concurrent_users):
            task = self.single_request(endpoint, data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 0,
                    'response_time': 0,
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def health_check_load_test(self, concurrent_users: List[int] = [1, 5, 10, 20]) -> Dict:
        """헬스체크 부하 테스트"""
        logger.info("🏥 헬스체크 부하 테스트 시작")
        
        results = {}
        for users in concurrent_users:
            logger.info(f"📊 {users}명 동시 사용자 테스트")
            user_results = await self.concurrent_requests("/api/v1/health", users)
            
            # 통계 계산
            response_times = [r['response_time'] for r in user_results if r['success']]
            success_count = sum(1 for r in user_results if r['success'])
            error_count = len(user_results) - success_count
            
            if response_times:
                results[users] = {
                    'total_requests': len(user_results),
                    'successful_requests': success_count,
                    'failed_requests': error_count,
                    'success_rate': success_count / len(user_results),
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'std_response_time': statistics.stdev(response_times) if len(response_times) > 1 else 0
                }
            else:
                results[users] = {
                    'total_requests': len(user_results),
                    'successful_requests': 0,
                    'failed_requests': len(user_results),
                    'success_rate': 0.0,
                    'avg_response_time': 0,
                    'min_response_time': 0,
                    'max_response_time': 0,
                    'std_response_time': 0
                }
            
            logger.info(f"✅ {users}명: 성공률 {results[users]['success_rate']:.1%}, "
                       f"평균 응답시간 {results[users]['avg_response_time']:.3f}초")
        
        return results
    
    async def rppg_load_test(self, concurrent_users: List[int] = [1, 3, 5, 10]) -> Dict:
        """RPPG 분석 부하 테스트"""
        logger.info("📹 RPPG 분석 부하 테스트 시작")
        
        # 시뮬레이션 비디오 데이터
        test_data = {
            "video_data": "base64_encoded_video_data",
            "frame_count": 300
        }
        
        results = {}
        for users in concurrent_users:
            logger.info(f"📊 {users}명 동시 RPPG 분석 테스트")
            user_results = await self.concurrent_requests("/api/v1/measure/rppg", users, test_data)
            
            # 통계 계산
            response_times = [r['response_time'] for r in user_results if r['success']]
            success_count = sum(1 for r in user_results if r['success'])
            error_count = len(user_results) - success_count
            
            if response_times:
                results[users] = {
                    'total_requests': len(user_results),
                    'successful_requests': success_count,
                    'failed_requests': error_count,
                    'success_rate': success_count / len(user_results),
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'std_response_time': statistics.stdev(response_times) if len(response_times) > 1 else 0
                }
            else:
                results[users] = {
                    'total_requests': len(user_results),
                    'successful_requests': 0,
                    'failed_requests': len(user_results),
                    'success_rate': 0.0,
                    'avg_response_time': 0,
                    'min_response_time': 0,
                    'max_response_time': 0,
                    'std_response_time': 0
                }
            
            logger.info(f"✅ {users}명: 성공률 {results[users]['success_rate']:.1%}, "
                       f"평균 응답시간 {results[users]['avg_response_time']:.3f}초")
        
        return results
    
    def generate_load_report(self, health_results: Dict, rppg_results: Dict) -> str:
        """부하 테스트 보고서 생성"""
        logger.info("📋 부하 테스트 보고서 생성 중...")
        
        report = f"""
🎯 **엔오건강도우미 부하 테스트 보고서**

🏥 **헬스체크 부하 테스트 결과**
"""
        
        for users, data in health_results.items():
            report += f"""
• {users}명 동시 사용자:
  - 총 요청: {data['total_requests']}개
  - 성공률: {data['success_rate']:.1%}
  - 평균 응답시간: {data['avg_response_time']:.3f}초
  - 최소/최대 응답시간: {data['min_response_time']:.3f}초 / {data['max_response_time']:.3f}초
"""
        
        report += f"""

📹 **RPPG 분석 부하 테스트 결과**
"""
        
        for users, data in rppg_results.items():
            report += f"""
• {users}명 동시 사용자:
  - 총 요청: {data['total_requests']}개
  - 성공률: {data['success_rate']:.1%}
  - 평균 응답시간: {data['avg_response_time']:.3f}초
  - 최소/최대 응답시간: {data['min_response_time']:.3f}초 / {data['max_response_time']:.3f}초
"""
        
        # 전체 성능 평가
        health_success_rates = [data['success_rate'] for data in health_results.values()]
        rppg_success_rates = [data['success_rate'] for data in rppg_results.values()]
        
        avg_health_success = statistics.mean(health_success_rates) if health_success_rates else 0
        avg_rppg_success = statistics.mean(rppg_success_rates) if rppg_success_rates else 0
        
        report += f"""

📊 **전체 성능 평가**
• 헬스체크 평균 성공률: {avg_health_success:.1%}
• RPPG 분석 평균 성공률: {avg_rppg_success:.1%}
• 시스템 안정성: {'✅ 안정' if avg_health_success > 0.95 else '⚠️ 불안정' if avg_health_success < 0.8 else '🔄 보통'}

🎯 **부하 테스트 권장사항**
• 동시 사용자 목표: 20명 이상 안정 처리
• 응답 시간 목표: 5초 이하
• 성공률 목표: 95% 이상
"""
        
        return report

async def main():
    """메인 함수"""
    logger.info("🚀 부하 테스트 시작")
    
    async with LoadTester() as tester:
        # 헬스체크 부하 테스트
        health_results = await tester.health_check_load_test()
        
        # RPPG 분석 부하 테스트
        rppg_results = await tester.rppg_load_test()
        
        # 보고서 생성
        report = tester.generate_load_report(health_results, rppg_results)
        print(report)
        
        # 결과 저장
        with open('load_test_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("✅ 부하 테스트 완료 - load_test_report.txt 저장됨")

if __name__ == "__main__":
    asyncio.run(main())
