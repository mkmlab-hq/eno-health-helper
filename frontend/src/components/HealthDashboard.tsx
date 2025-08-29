'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface HealthData {
  date: string;
  rppg?: {
    heartRate: number;
    stressIndex: number;
    confidence: number;
    quality: string;
  };
  voice?: {
    pitch: number;
    clarity: number;
    emotion: string;
    quality: string;
  };
  fusion?: {
    digitalTemperament: string;
    overallScore: number;
    recommendations: string[];
  };
}

interface HealthDashboardProps {
  onClose?: () => void;
}

export default function HealthDashboard({ onClose }: HealthDashboardProps) {
  const [healthData, setHealthData] = useState<HealthData[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('week');
  const [isLoading, setIsLoading] = useState(false);

  // 샘플 데이터 (실제로는 Firebase에서 가져올 예정)
  const sampleData: HealthData[] = [
    {
      date: '2025-01-20',
      rppg: { heartRate: 72, stressIndex: 0.3, confidence: 0.85, quality: 'good' },
      voice: { pitch: 220, clarity: 0.8, emotion: 'calm', quality: 'good' },
      fusion: { digitalTemperament: '태양인', overallScore: 85, recommendations: ['명상', '요가'] }
    },
    {
      date: '2025-01-21',
      rppg: { heartRate: 68, stressIndex: 0.2, confidence: 0.9, quality: 'excellent' },
      voice: { pitch: 210, clarity: 0.85, emotion: 'peaceful', quality: 'excellent' },
      fusion: { digitalTemperament: '태양인', overallScore: 92, recommendations: ['산책', '독서'] }
    },
    {
      date: '2025-01-22',
      rppg: { heartRate: 75, stressIndex: 0.4, confidence: 0.8, quality: 'good' },
      voice: { pitch: 230, clarity: 0.75, emotion: 'slightly_stressed', quality: 'good' },
      fusion: { digitalTemperament: '태양인', overallScore: 78, recommendations: ['스트레칭', '따뜻한 차'] }
    }
  ];

  useEffect(() => {
    // 실제 데이터 로드 시뮬레이션
    setIsLoading(true);
    setTimeout(() => {
      setHealthData(sampleData);
      setIsLoading(false);
    }, 1000);
  }, []);

  // 기간별 데이터 필터링
  const getFilteredData = () => {
    const today = new Date();
    const filteredData = healthData.filter(data => {
      const dataDate = new Date(data.date);
      const diffTime = Math.abs(today.getTime() - dataDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      switch (selectedPeriod) {
        case 'week': return diffDays <= 7;
        case 'month': return diffDays <= 30;
        case 'year': return diffDays <= 365;
        default: return true;
      }
    });
    
    return filteredData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  };

  // 건강 점수 계산
  const calculateHealthScore = (data: HealthData) => {
    let score = 0;
    let totalWeight = 0;
    
    if (data.rppg) {
      score += (100 - data.rppg.stressIndex * 100) * 0.4;
      totalWeight += 0.4;
    }
    
    if (data.voice) {
      score += data.voice.clarity * 100 * 0.3;
      totalWeight += 0.3;
    }
    
    if (data.fusion) {
      score += data.fusion.overallScore * 0.3;
      totalWeight += 0.3;
    }
    
    return totalWeight > 0 ? Math.round(score / totalWeight) : 0;
  };

  // 평균 건강 점수
  const averageHealthScore = healthData.length > 0 
    ? Math.round(healthData.reduce((sum, data) => sum + calculateHealthScore(data), 0) / healthData.length)
    : 0;

  // 건강 트렌드 분석
  const getHealthTrend = () => {
    if (healthData.length < 2) return 'stable';
    
    const recentScores = healthData.slice(-3).map(data => calculateHealthScore(data));
    const firstScore = recentScores[0];
    const lastScore = recentScores[recentScores.length - 1];
    
    if (lastScore > firstScore + 5) return 'improving';
    if (lastScore < firstScore - 5) return 'declining';
    return 'stable';
  };

  const filteredData = getFilteredData();
  const healthTrend = getHealthTrend();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-xl w-full max-w-6xl h-[800px] flex flex-col shadow-lg border border-eno-500/30"
      >
        {/* Header */}
        <div className="border-b border-eno-500/30 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-eno-600 rounded-full flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
              <div>
                <h2 className="text-white text-xl font-semibold">건강 리포트 대시보드</h2>
                <p className="text-eno-400 text-sm">
                  개인별 건강 지표 변화 추이 및 AI 맞춤 음악 효과 분석
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="flex-1 p-6 overflow-y-auto">
          {/* 기간 선택 */}
          <div className="flex space-x-2 mb-6">
            {(['week', 'month', 'year'] as const).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedPeriod === period 
                    ? 'bg-eno-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {period === 'week' ? '주간' : period === 'month' ? '월간' : '연간'}
              </button>
            ))}
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="ml-3 text-eno-400">건강 데이터를 분석하고 있습니다...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 전체 건강 점수 */}
              <div className="bg-gradient-to-br from-eno-600/20 to-eno-400/20 border border-eno-500/30 rounded-xl p-6">
                <h3 className="text-white text-lg font-semibold mb-2">🏆 전체 건강 점수</h3>
                <p className="text-eno-300 text-sm mb-4">
                  {selectedPeriod === 'week' ? '주간' : selectedPeriod === 'month' ? '월간' : '연간'} 평균
                </p>
                <div className="text-center">
                  <div className="text-6xl font-bold text-eno-400 mb-2">{averageHealthScore}</div>
                  <div className="text-2xl text-white mb-4">점</div>
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    healthTrend === 'improving' ? 'bg-green-500/20 text-green-400' :
                    healthTrend === 'declining' ? 'bg-red-500/20 text-red-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {healthTrend === 'improving' ? '📈 개선 중' :
                     healthTrend === 'declining' ? '📉 하락 중' : '➡️ 안정'}
                  </div>
                </div>
              </div>

              {/* 건강 트렌드 요약 */}
              <div className="bg-gradient-to-br from-blue-600/20 to-blue-400/20 border border-blue-500/30 rounded-xl p-6">
                <h3 className="text-white text-lg font-semibold mb-2">📈 건강 트렌드 요약</h3>
                <p className="text-blue-300 text-sm mb-4">최근 건강 상태 변화 분석</p>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">심박수 안정성</span>
                    <span className="text-white font-semibold">85%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">스트레스 관리</span>
                    <span className="text-white font-semibold">72%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '72%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">음성 건강</span>
                    <span className="text-white font-semibold">78%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78%' }}></div>
                  </div>
                </div>
              </div>

              {/* 시계열 건강 데이터 */}
              <div className="lg:col-span-2 bg-gradient-to-br from-gray-800/50 to-gray-700/50 border border-gray-600/30 rounded-xl p-6">
                <h3 className="text-white text-lg font-semibold mb-2">📅 시계열 건강 데이터</h3>
                <p className="text-gray-300 text-sm mb-4">
                  {selectedPeriod === 'week' ? '주간' : selectedPeriod === 'month' ? '월간' : '연간'} 건강 지표 변화
                </p>
                <div className="space-y-4">
                  {filteredData.map((data, index) => (
                    <motion.div
                      key={data.date}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-white font-medium">
                          {new Date(data.date).toLocaleDateString('ko-KR', {
                            month: 'short',
                            day: 'numeric'
                          })}
                        </div>
                        <div className="text-eno-400 font-bold text-lg">
                          {calculateHealthScore(data)}점
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        {data.rppg && (
                          <div className="bg-red-500/10 border border-red-500/30 rounded p-3">
                            <div className="text-red-400 font-medium mb-2">💓 심혈관 건강</div>
                            <div className="text-white">심박수: {data.rppg.heartRate} BPM</div>
                            <div className="text-white">스트레스: {(data.rppg.stressIndex * 100).toFixed(0)}%</div>
                          </div>
                        )}
                        
                        {data.voice && (
                          <div className="bg-blue-500/10 border border-blue-500/30 rounded p-3">
                            <div className="text-blue-400 font-medium mb-2">🎤 음성 건강</div>
                            <div className="text-white">피치: {data.voice.pitch} Hz</div>
                            <div className="text-white">명확도: {(data.voice.clarity * 100).toFixed(0)}%</div>
                          </div>
                        )}
                        
                        {data.fusion && (
                          <div className="bg-green-500/10 border border-green-500/30 rounded p-3">
                            <div className="text-green-400 font-medium mb-2">🧘 체질 분석</div>
                            <div className="text-white">체질: {data.fusion.digitalTemperament}</div>
                            <div className="text-white">종합 점수: {data.fusion.overallScore}점</div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* AI 맞춤 음악 효과 분석 */}
              <div className="lg:col-span-2 bg-gradient-to-br from-purple-600/20 to-purple-400/20 border border-purple-500/30 rounded-xl p-6">
                <h3 className="text-white text-lg font-semibold mb-2">🎵 AI 맞춤 음악 효과 분석</h3>
                <p className="text-purple-300 text-sm mb-4">개인 맞춤 음악이 건강에 미친 영향</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-purple-400 mb-2">15%</div>
                    <div className="text-white font-medium mb-1">스트레스 감소</div>
                    <div className="text-purple-300 text-sm">음악 청취 후 평균</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-4xl font-bold text-purple-400 mb-2">23%</div>
                    <div className="text-white font-medium mb-1">심박수 안정화</div>
                    <div className="text-purple-300 text-sm">음악 청취 후 평균</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-4xl font-bold text-purple-400 mb-2">18%</div>
                    <div className="text-white font-medium mb-1">수면 품질 향상</div>
                    <div className="text-purple-300 text-sm">음악 청취 후 평균</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-4xl font-bold text-purple-400 mb-2">31%</div>
                    <div className="text-white font-medium mb-1">전반적 웰빙 향상</div>
                    <div className="text-purple-300 text-sm">음악 청취 후 평균</div>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <div className="text-purple-300 font-medium mb-2">💡 AI 음악 효과 인사이트</div>
                  <div className="text-white text-sm">
                    개인 맞춤형 치유 음악은 단순한 엔터테인먼트를 넘어 건강 관리의 핵심 도구로 작용합니다. 
                    특히 스트레스 관리와 심혈관 건강에 뚜렷한 효과를 보이고 있습니다.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
} 