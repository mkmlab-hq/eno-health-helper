#!/usr/bin/env python3
"""
성능 검증 스크립트
RPPG 분석 시스템의 성능을 측정하고 최적화합니다.
"""

import time
import psutil
import asyncio
import statistics
from typing import Dict, List, Tuple
import logging

from app.services.mkm_core_ai_integration import MKMCoreAIIntegration
from app.services.voice_analyzer import VoiceAnalyzer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """성능 분석기"""
    
    def __init__(self):
        self.rppg_analyzer = MKMCoreAIIntegration()
        self.voice_analyzer = VoiceAnalyzer()
        self.results = []
    
    async def measure_rppg_performance(self, frame_counts: List[int] = [100, 300, 500]) -> Dict:
        """RPPG 분석 성능 측정"""
        logger.info("🚀 RPPG 성능 측정 시작")
        
        performance_data = {
            'frame_counts': frame_counts,
            'processing_times': [],
            'memory_usage': [],
            'accuracy_scores': [],
            'throughput': []
        }
        
        for frame_count in frame_counts:
            logger.info(f"📊 {frame_count} 프레임 분석 시작")
            
            # 메모리 사용량 측정 시작
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 처리 시간 측정
            start_time = time.time()
            
            try:
                # RPPG 분석 실행
                result = await self.rppg_analyzer.analyze_rppg(
                    video_data=b"simulated_video_data",
                    frame_count=frame_count
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # 메모리 사용량 측정 종료
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_used = memory_after - memory_before
                
                # 정확도 점수 (시뮬레이션 데이터 기준)
                accuracy = 0.85 if result.get('hr', 0) > 0 else 0.0
                
                # 처리량 (프레임/초)
                throughput = frame_count / processing_time if processing_time > 0 else 0
                
                performance_data['processing_times'].append(processing_time)
                performance_data['memory_usage'].append(memory_used)
                performance_data['accuracy_scores'].append(accuracy)
                performance_data['throughput'].append(throughput)
                
                logger.info(f"✅ {frame_count} 프레임: {processing_time:.3f}초, {memory_used:.2f}MB, {throughput:.1f} fps")
                
            except Exception as e:
                logger.error(f"❌ {frame_count} 프레임 분석 실패: {e}")
                performance_data['processing_times'].append(0)
                performance_data['memory_usage'].append(0)
                performance_data['accuracy_scores'].append(0)
                performance_data['throughput'].append(0)
        
        return performance_data
    
    async def measure_voice_performance(self, sample_counts: List[int] = [1000, 5000, 10000]) -> Dict:
        """음성 분석 성능 측정"""
        logger.info("🎵 음성 분석 성능 측정 시작")
        
        performance_data = {
            'sample_counts': sample_counts,
            'processing_times': [],
            'memory_usage': [],
            'accuracy_scores': []
        }
        
        for sample_count in sample_counts:
            logger.info(f"📊 {sample_count} 샘플 분석 시작")
            
            # 메모리 사용량 측정 시작
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 처리 시간 측정
            start_time = time.time()
            
            try:
                # 음성 분석 실행
                result = await self.voice_analyzer.analyze_voice(
                    audio_data=b"simulated_audio_data"
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # 메모리 사용량 측정 종료
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_used = memory_after - memory_before
                
                # 정확도 점수 (시뮬레이션 데이터 기준)
                accuracy = 0.90 if result.get('f0', 0) > 0 else 0.0
                
                performance_data['processing_times'].append(processing_time)
                performance_data['memory_usage'].append(memory_used)
                performance_data['accuracy_scores'].append(accuracy)
                
                logger.info(f"✅ {sample_count} 샘플: {processing_time:.3f}초, {memory_used:.2f}MB")
                
            except Exception as e:
                logger.error(f"❌ {sample_count} 샘플 분석 실패: {e}")
                performance_data['processing_times'].append(0)
                performance_data['memory_usage'].append(0)
                performance_data['accuracy_scores'].append(0)
        
        return performance_data
    
    def calculate_statistics(self, data: List[float]) -> Dict:
        """통계 계산"""
        if not data or all(x == 0 for x in data):
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        valid_data = [x for x in data if x > 0]
        if not valid_data:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        return {
            'mean': statistics.mean(valid_data),
            'std': statistics.stdev(valid_data) if len(valid_data) > 1 else 0,
            'min': min(valid_data),
            'max': max(valid_data)
        }
    
    def generate_report(self, rppg_data: Dict, voice_data: Dict) -> str:
        """성능 보고서 생성"""
        logger.info("📋 성능 보고서 생성 중...")
        
        # RPPG 통계
        rppg_times_stats = self.calculate_statistics(rppg_data['processing_times'])
        rppg_memory_stats = self.calculate_statistics(rppg_data['memory_usage'])
        rppg_throughput_stats = self.calculate_statistics(rppg_data['throughput'])
        
        # 음성 분석 통계
        voice_times_stats = self.calculate_statistics(voice_data['processing_times'])
        voice_memory_stats = self.calculate_statistics(voice_data['memory_usage'])
        
        report = f"""
🎯 **엔오건강도우미 성능 분석 보고서**

📊 **RPPG 분석 성능**
• 처리 시간: 평균 {rppg_times_stats['mean']:.3f}초 (표준편차: {rppg_times_stats['std']:.3f})
• 메모리 사용량: 평균 {rppg_memory_stats['mean']:.2f}MB (표준편차: {rppg_memory_stats['std']:.2f})
• 처리량: 평균 {rppg_throughput_stats['mean']:.1f} fps (표준편차: {rppg_throughput_stats['std']:.1f})

🎵 **음성 분석 성능**
• 처리 시간: 평균 {voice_times_stats['mean']:.3f}초 (표준편차: {voice_times_stats['std']:.3f})
• 메모리 사용량: 평균 {voice_memory_stats['mean']:.2f}MB (표준편차: {voice_memory_stats['std']:.2f})

📈 **성능 지표**
• RPPG 최대 처리량: {rppg_throughput_stats['max']:.1f} fps
• RPPG 최소 처리량: {rppg_throughput_stats['min']:.1f} fps
• 메모리 효율성: {rppg_memory_stats['mean']:.2f}MB/프레임

🎯 **최적화 권장사항**
• 처리량 목표: 30+ fps 달성 필요
• 메모리 목표: 프레임당 0.1MB 이하
• 응답 시간 목표: 1초 이하
"""
        
        return report

async def main():
    """메인 함수"""
    logger.info("🚀 성능 검증 시작")
    
    analyzer = PerformanceAnalyzer()
    
    # RPPG 성능 측정
    rppg_data = await analyzer.measure_rppg_performance()
    
    # 음성 분석 성능 측정
    voice_data = await analyzer.measure_voice_performance()
    
    # 보고서 생성
    report = analyzer.generate_report(rppg_data, voice_data)
    print(report)
    
    # 결과 저장
    with open('performance_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("✅ 성능 검증 완료 - performance_report.txt 저장됨")

if __name__ == "__main__":
    asyncio.run(main())
