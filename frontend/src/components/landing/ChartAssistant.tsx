'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface ChartData {
  id: string;
  patientName: string;
  chartType: string;
  uploadDate: string;
  status: 'pending' | 'analyzing' | 'completed';
  summary: string;
  insights: string[];
  recommendations: string[];
}

export default function ChartAssistant() {
  const [selectedChart, setSelectedChart] = useState<ChartData | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const sampleCharts: ChartData[] = [
    {
      id: '1',
      patientName: '김환자',
      chartType: '혈액검사',
      uploadDate: '2025-01-15',
      status: 'completed',
      summary: '전반적으로 양호한 상태이나, 철분 수치가 다소 낮습니다.',
      insights: [
        '헤모글로빈: 12.5 g/dL (정상 범위)',
        '철분: 45 μg/dL (경미한 부족)',
        '콜레스테롤: 180 mg/dL (정상 범위)'
      ],
      recommendations: [
        '철분이 풍부한 식품 섭취 권장',
        '3개월 후 재검사 권장',
        '현재 약물 복용 중단 없음'
      ]
    },
    {
      id: '2',
      patientName: '이환자',
      chartType: '심전도',
      uploadDate: '2025-01-14',
      status: 'analyzing',
      summary: '심전도 분석 중입니다.',
      insights: [],
      recommendations: []
    }
  ];

  const chartTypes = ['혈액검사', '심전도', 'X-ray', 'MRI', '초음파', '기타'];
  const analysisSteps = [
    '차트 데이터 로딩',
    'AI 패턴 분석',
    '의학적 인사이트 추출',
    '치료 권장사항 생성',
    '보고서 작성 완료'
  ];

  const startAnalysis = () => {
    if (!selectedChart) return;
    
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    
    const interval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsAnalyzing(false);
          return 100;
        }
        return prev + 20;
      });
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900">
      {/* 헤더 */}
      <header className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center shadow-neon-cyan">
              <div className="w-6 h-6 text-white neon-glow">🤖</div>
            </div>
            <div>
              <h1 className="text-2xl font-orbitron font-bold text-white neon-text">
                AI 차트 어시스턴트
              </h1>
              <p className="text-sm text-gray-300 font-noto">의료진을 위한 AI 보조 진단 도구</p>
            </div>
          </div>
          
          <Link 
            href="/"
            className="glass-button text-gray-300 hover:text-eno-400 transition-colors font-noto"
          >
            🏠 홈으로
          </Link>
        </div>
      </header>

      <main className="relative z-10 px-6 pb-20">
        <div className="max-w-7xl mx-auto">
          {/* 히어로 섹션 */}
          <section className="text-center py-16">
            <h2 className="text-5xl md:text-6xl font-orbitron font-bold mb-6">
              <span className="neon-text">AI가 분석하는</span>
              <br/>
              <span className="text-eno-400">의료 차트</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12 font-noto leading-relaxed">
              복잡한 환자 차트를 AI가 자동으로 분석하여<br/>
              <span className="text-eno-400 font-semibold">핵심 인사이트와 치료 방향</span>을 제시합니다
            </p>
          </section>

          {/* 메인 컨텐츠 */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* 왼쪽: 차트 업로드 및 목록 */}
            <div className="lg:col-span-2">
              {/* 차트 업로드 */}
              <div className="glass-card p-8 rounded-2xl mb-8">
                <h3 className="text-2xl font-orbitron font-bold text-white mb-6 neon-text">
                  📁 차트 업로드
                </h3>
                
                <div className="space-y-6">
                  {/* 파일 업로드 영역 */}
                  <div className="border-2 border-dashed border-slate-600 rounded-2xl p-8 text-center hover:border-eno-400 transition-colors">
                    <div className="text-6xl mb-4">📄</div>
                    <h4 className="text-xl font-semibold text-white mb-2">차트 파일을 여기에 드래그하세요</h4>
                    <p className="text-gray-400 mb-4">또는 클릭하여 파일 선택</p>
                    <button className="glass-button px-6 py-3">
                      파일 선택하기
                    </button>
                    <p className="text-sm text-gray-500 mt-2">
                      지원 형식: PDF, JPG, PNG, DICOM (최대 50MB)
                    </p>
                  </div>

                  {/* 차트 정보 입력 */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-300 font-semibold mb-2">환자명</label>
                      <input
                        type="text"
                        className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:border-eno-400 focus:ring-2 focus:ring-eno-400/20"
                        placeholder="환자명을 입력하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 font-semibold mb-2">차트 유형</label>
                      <select className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:border-eno-400 focus:ring-2 focus:ring-eno-400/20">
                        <option value="">차트 유형 선택</option>
                        {chartTypes.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* 업로드 버튼 */}
                  <button className="w-full glass-button text-lg py-4 font-semibold neon-glow">
                    🚀 차트 분석 시작
                  </button>
                </div>
              </div>

              {/* 차트 목록 */}
              <div className="glass-card p-8 rounded-2xl">
                <h3 className="text-2xl font-orbitron font-bold text-white mb-6 neon-text">
                  📋 분석된 차트 목록
                </h3>
                
                <div className="space-y-4">
                  {sampleCharts.map(chart => (
                    <div
                      key={chart.id}
                      onClick={() => setSelectedChart(chart)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all ${
                        selectedChart?.id === chart.id
                          ? 'border-eno-400 bg-eno-400/20'
                          : 'border-slate-600 hover:border-slate-500'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-lg font-semibold text-white">{chart.patientName}</h4>
                          <p className="text-gray-400">{chart.chartType} • {chart.uploadDate}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            chart.status === 'completed'
                              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                              : chart.status === 'analyzing'
                              ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                              : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
                          }`}>
                            {chart.status === 'completed' ? '완료' : 
                             chart.status === 'analyzing' ? '분석중' : '대기중'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 오른쪽: 분석 결과 및 진행상황 */}
            <div className="space-y-6">
              {/* 분석 진행상황 */}
              {isAnalyzing && (
                <div className="glass-card p-6 rounded-2xl">
                  <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                    🔄 AI 분석 진행중
                  </h4>
                  
                  <div className="space-y-4">
                    <div className="w-full bg-slate-800 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-eno-400 to-eno-600 h-3 rounded-full transition-all duration-1000"
                        style={{ width: `${analysisProgress}%` }}
                      />
                    </div>
                    <p className="text-center text-sm text-gray-400">
                      {analysisProgress}% 완료
                    </p>
                    
                    <div className="space-y-2">
                      {analysisSteps.map((step, index) => (
                        <div
                          key={index}
                          className={`flex items-center space-x-2 text-sm ${
                            index * 20 <= analysisProgress
                              ? 'text-eno-400' : 'text-gray-500'
                          }`}
                        >
                          <span className={`w-4 h-4 rounded-full flex items-center justify-center ${
                            index * 20 <= analysisProgress
                              ? 'bg-eno-400 text-white' : 'bg-slate-600'
                          }`}>
                            {index * 20 <= analysisProgress ? '✓' : index + 1}
                          </span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* 선택된 차트 분석 결과 */}
              {selectedChart && selectedChart.status === 'completed' && (
                <>
                  <div className="glass-card p-6 rounded-2xl">
                    <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                      📊 분석 요약
                    </h4>
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {selectedChart.summary}
                    </p>
                  </div>

                  <div className="glass-card p-6 rounded-2xl">
                    <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                      🔍 주요 발견사항
                    </h4>
                    <div className="space-y-2">
                      {selectedChart.insights.map((insight, index) => (
                        <div key={index} className="flex items-start space-x-2">
                          <span className="text-eno-400 mt-1">•</span>
                          <span className="text-gray-300 text-sm">{insight}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="glass-card p-6 rounded-2xl">
                    <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                      💡 치료 권장사항
                    </h4>
                    <div className="space-y-2">
                      {selectedChart.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start space-x-2">
                          <span className="text-green-400 mt-1">→</span>
                          <span className="text-gray-300 text-sm">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={startAnalysis}
                    className="w-full glass-button py-3 font-semibold neon-glow"
                  >
                    🔄 재분석하기
                  </button>
                </>
              )}

              {/* AI 성능 통계 */}
              <div className="glass-card p-6 rounded-2xl">
                <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                  📈 AI 성능 통계
                </h4>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-eno-400 neon-glow">98.7%</div>
                    <div className="text-sm text-gray-400">정확도</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-eno-400 neon-glow">2.3초</div>
                    <div className="text-sm text-gray-400">평균 분석 시간</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-eno-400 neon-glow">15,432</div>
                    <div className="text-sm text-gray-400">총 분석 차트</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
