'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { Chart, registerables } from 'chart.js';
import { Button } from '@/components/ui';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';

// Chart.js 등록
Chart.register(...registerables);

interface MeasurementData {
  pairId: number;
  type: 'before' | 'after';
  date: string;
  score: number;
  temperament: string;
  stress: string;
  heartrate: number;
  hrv: number;
  voiceStability: number;
}

interface PairedData {
  [key: number]: {
    before?: MeasurementData;
    after?: MeasurementData;
  };
}

export default function DashboardPage() {
  const [selectedPairId, setSelectedPairId] = useState<number | null>(null);
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstanceRef = useRef<Chart | null>(null);

  // Mock Data simulating before/after measurements
  const mockData: MeasurementData[] = [
    { pairId: 1, type: 'before', date: '2025-08-27 09:00', score: 75, temperament: 'A타입', stress: '낮음', heartrate: 68, hrv: 55, voiceStability: 0.85 },
    { pairId: 1, type: 'after', date: '2025-08-27 09:32', score: 85, temperament: 'A타입', stress: '매우 낮음', heartrate: 64, hrv: 65, voiceStability: 0.91 },
    
    { pairId: 2, type: 'before', date: '2025-08-20 14:30', score: 68, temperament: 'B타입', stress: '보통', heartrate: 75, hrv: 45, voiceStability: 0.72 },
    { pairId: 2, type: 'after', date: '2025-08-20 15:01', score: 74, temperament: 'B타입', stress: '낮음', heartrate: 71, hrv: 52, voiceStability: 0.80 },

    { pairId: 3, type: 'before', date: '2025-08-12 21:00', score: 65, temperament: 'C타입', stress: '높음', heartrate: 82, hrv: 38, voiceStability: 0.65 },
    { pairId: 3, type: 'after', date: '2025-08-12 21:35', score: 72, temperament: 'C타입', stress: '보통', heartrate: 76, hrv: 48, voiceStability: 0.75 },
  ];

  // 데이터 페어링 처리 (useMemo로 최적화)
  const pairedData = useMemo(() => {
    return mockData.reduce((acc, item) => {
      if (!acc[item.pairId]) {
        acc[item.pairId] = {};
      }
      // 타입 안전성 강화
      const pairId = item.pairId;
      if (acc[pairId]) {
        acc[pairId][item.type] = item;
      }
      return acc;
    }, {} as PairedData);
  }, []);

  // Chart.js 초기화
  useEffect(() => {
    if (chartRef.current) {
      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
        // 기존 차트 인스턴스 정리
        if (chartInstanceRef.current) {
          chartInstanceRef.current.destroy();
        }

        chartInstanceRef.current = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['복용 전', '복용 후'],
            datasets: [{
              label: '종합 건강 점수',
              data: [],
              borderColor: '#00d4ff',
              backgroundColor: 'rgba(0, 212, 255, 0.2)',
              fill: true,
              tension: 0.1,
              pointBackgroundColor: '#ffffff',
              pointBorderColor: '#00d4ff',
              pointRadius: 6,
              pointHoverRadius: 8,
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: false,
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                ticks: { color: '#9ca3af' }
              },
              x: {
                grid: { display: false },
                ticks: { color: '#9ca3af', font: { size: 14, weight: 'bold' } }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    }

    // 컴포넌트 언마운트 시 차트 정리
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, []);

  // 점수에 따른 색상 반환
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-cyan-400';
    if (score >= 60) return 'text-green-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  // 비교 데이터 업데이트
  const updateComparison = (pairId: number): void => {
    setSelectedPairId(pairId);
    
    const pair = pairedData[pairId];
    if (pair && pair.before && pair.after && chartInstanceRef.current) {
      const before = pair.before;
      const after = pair.after;

      // 차트 데이터 업데이트
      if (chartInstanceRef.current.data.datasets[0]) {
        chartInstanceRef.current.data.datasets[0].data = [before.score, after.score];
      }
      
      const allScores = [before.score, after.score];
      if (chartInstanceRef.current.options.scales?.y) {
        chartInstanceRef.current.options.scales.y.min = Math.min(...allScores) - 10;
        chartInstanceRef.current.options.scales.y.max = Math.max(...allScores) + 10;
      }
      chartInstanceRef.current.update();
    }
  };

  // 상세 비교 행 생성
  const createDetailRow = (label: string, val1: number, val2: number): JSX.Element => {
    const change = val2 - val1;
    const color = change > 0 ? 'text-green-400' : (change < 0 ? 'text-red-400' : 'text-gray-400');
    const icon = change > 0 ? '▲' : (change < 0 ? '▼' : '');
    const changeText = change !== 0 ? 
      <span className={color}>{icon} {Math.abs(change).toFixed(2)}</span> : 
      <span className="text-gray-400">-</span>;

    return (
      <div key={label} className="flex justify-between items-center text-sm p-2 bg-white/5 rounded-md border border-white/10">
        <span className="font-semibold text-gray-300">{label}</span>
        <div className="flex items-center space-x-3">
          <span className="text-gray-400">{val1}</span>
          <span className="text-gray-500">→</span>
          <span className="text-white font-bold">{val2}</span>
          {changeText}
        </div>
      </div>
    );
  };

  // 새로운 검사 시작 핸들러
  const handleNewTest = (): void => {
    // 새로운 검사 페이지로 이동
    window.location.href = '/measure';
  };

  // 선택된 페어 데이터
  const selectedPair = selectedPairId ? pairedData[selectedPairId] : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-900/50 backdrop-blur-sm shadow-2xl sticky top-0 z-50 border-b border-cyan-500/20">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400 neon-glow">복용 전후 건강 변화</h1>
            <p className="text-sm text-gray-400">모든 데이터는 비식별 처리되어 안전하게 관리됩니다.</p>
          </div>
          <Button
            variant="default"
            onClick={handleNewTest}
            className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 shadow-lg hover:shadow-cyan-500/50"
          >
            새로운 검사 시작
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {/* Comparison Section */}
        {selectedPair && selectedPair.before && selectedPair.after && (
          <Card variant="glass" className="mb-12 border-cyan-500/20 shadow-2xl">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-white">복용 전후 상세 비교</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                {/* Comparison Chart */}
                <div>
                  <h3 className="font-semibold text-cyan-400 mb-2">종합 건강 점수 변화</h3>
                  <div className="h-64">
                    <canvas ref={chartRef}></canvas>
                  </div>
                </div>
                {/* Comparison Details */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-cyan-400 mb-2">주요 지표 변화</h3>
                  {createDetailRow('심박수 (BPM)', selectedPair.before.heartrate, selectedPair.after.heartrate)}
                  {createDetailRow('심박변이도 (HRV)', selectedPair.before.hrv, selectedPair.after.hrv)}
                  {createDetailRow('음성 안정성', selectedPair.before.voiceStability, selectedPair.after.voiceStability)}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* History List Section */}
        <Card variant="glass" className="border-cyan-500/20 shadow-2xl">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-2xl font-bold text-white">나의 복용 기록</CardTitle>
              <p className="text-sm text-gray-400">비교하고 싶은 기록을 선택하세요</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
              {Object.values(pairedData).map((pair) => {
                if (pair.before && pair.after) {
                  return (
                    <Card 
                      key={pair.before.pairId}
                      variant="glass" 
                      className="p-4 hover:bg-gray-700/50 transition-colors duration-200 cursor-pointer"
                      onClick={() => updateComparison(pair.before.pairId)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <input 
                            type="radio" 
                            name="comparison_radio" 
                            checked={selectedPairId === pair.before.pairId}
                            onChange={() => updateComparison(pair.before.pairId)}
                            className="h-5 w-5 bg-gray-800 border-gray-600 text-cyan-500 focus:ring-cyan-600"
                          />
                          <div>
                            <p className="font-bold text-white">
                              {pair.before.date.substring(0, 10)} 복용 기록
                            </p>
                            <p className="text-sm text-gray-400">
                              {pair.before.date.substring(11)} (복용 전) → {pair.after.date.substring(11)} (복용 후)
                            </p>
                          </div>
                        </div>
                        <div className="text-right flex items-center space-x-4">
                          <p className={`text-xl font-bold ${getScoreColor(pair.before.score)}`}>
                            {pair.before.score}점
                          </p>
                          <p className="text-gray-400">→</p>
                          <p className={`text-xl font-bold ${getScoreColor(pair.after.score)}`}>
                            {pair.after.score}점
                          </p>
                        </div>
                      </div>
                    </Card>
                  );
                }
                return null;
              })}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
