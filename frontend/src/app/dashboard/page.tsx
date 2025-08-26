'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Chart from 'chart.js/auto';

export default function DashboardPage() {
  const router = useRouter();
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstanceRef = useRef<Chart | null>(null);
  const [selectedPairId, setSelectedPairId] = useState<number | null>(null);

  // Mock Data simulating before/after measurements
  const mockData = [
    { pairId: 1, type: 'before', date: '2025-08-27 09:00', score: 75, temperament: 'A타입', stress: '낮음', heartrate: 68, hrv: 55, voiceStability: 0.85 },
    { pairId: 1, type: 'after', date: '2025-08-27 09:32', score: 85, temperament: 'A타입', stress: '매우 낮음', heartrate: 64, hrv: 65, voiceStability: 0.91 },
    
    { pairId: 2, type: 'before', date: '2025-08-20 14:30', score: 68, temperament: 'B타입', stress: '보통', heartrate: 75, hrv: 45, voiceStability: 0.72 },
    { pairId: 2, type: 'after', date: '2025-08-20 15:01', score: 74, temperament: 'B타입', stress: '낮음', heartrate: 71, hrv: 52, voiceStability: 0.80 },

    { pairId: 3, type: 'before', date: '2025-08-12 21:00', score: 65, temperament: 'C타입', stress: '높음', heartrate: 82, hrv: 38, voiceStability: 0.65 },
    { pairId: 3, type: 'after', date: '2025-08-12 21:35', score: 72, temperament: 'C타입', stress: '보통', heartrate: 76, hrv: 48, voiceStability: 0.75 },
  ];

  // Group data by pairId
  const pairedData = mockData.reduce((acc: any, item) => {
    if (!acc[item.pairId]) {
      acc[item.pairId] = {};
    }
    acc[item.pairId][item.type] = item;
    return acc;
  }, {});

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-cyan-400';
    if (score >= 60) return 'text-green-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  const handleNewTest = () => {
    router.push('/measure');
  };

  const handleComparisonSelect = (pairId: number) => {
    setSelectedPairId(pairId);
  };

  const updateComparison = (pairId: number) => {
    const pair = pairedData[pairId];
    
    if (pair && pair.before && pair.after && chartInstanceRef.current) {
      const before = pair.before;
      const after = pair.after;

      // Update Chart
      chartInstanceRef.current.data.datasets[0].data = [before.score, after.score];
      const allScores = [before.score, after.score];
      (chartInstanceRef.current.options.scales as any).y.min = Math.min(...allScores) - 10;
      (chartInstanceRef.current.options.scales as any).y.max = Math.max(...allScores) + 10;
      chartInstanceRef.current.update();
    }
  };

  useEffect(() => {
    if (chartRef.current && !chartInstanceRef.current) {
      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
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

    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
        chartInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (selectedPairId) {
      updateComparison(selectedPairId);
    }
  }, [selectedPairId]);

  const createDetailRow = (label: string, val1: number, val2: number) => {
    const change = val2 - val1;
    const color = change > 0 ? 'text-green-400' : (change < 0 ? 'text-red-400' : 'text-gray-400');
    const icon = change > 0 ? '▲' : (change < 0 ? '▼' : '');
    const changeText = change !== 0 ? `<span class="${color}">${icon} ${Math.abs(change).toFixed(2)}</span>` : '<span class="text-gray-400">-</span>';
    
    return (
      <div key={label} className="flex justify-between items-center text-sm p-2 glass-card rounded-md">
        <span className="font-semibold text-gray-300">{label}</span>
        <div className="flex items-center space-x-3">
          <span className="text-gray-400">{val1}</span>
          <span className="text-gray-500">→</span>
          <span className="text-white font-bold">{val2}</span>
          <span dangerouslySetInnerHTML={{ __html: changeText }} />
        </div>
      </div>
    );
  };

  const selectedPair = selectedPairId ? pairedData[selectedPairId] : null;

  return (
    <div className="text-gray-100">
      {/* Header */}
      <header className="bg-gray-900/50 backdrop-blur-sm shadow-2xl sticky top-0 z-50 border-b border-cyan-500/20">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400 neon-glow">복용 전후 건강 변화</h1>
            <p className="text-sm text-gray-400">모든 데이터는 비식별 처리되어 안전하게 관리됩니다.</p>
          </div>
          <button 
            onClick={handleNewTest}
            className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-2 px-5 rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-cyan-500/50"
          >
            새로운 검사 시작
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        {/* Comparison Section */}
        {selectedPair && (
          <section className="mb-12 glass-card rounded-xl p-6 neon-border">
            <h2 className="text-2xl font-bold text-white mb-4">복용 전후 상세 비교</h2>
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
                {selectedPair.before && selectedPair.after && (
                  <>
                    {createDetailRow('심박수 (BPM)', selectedPair.before.heartrate, selectedPair.after.heartrate)}
                    {createDetailRow('심박변이도 (HRV)', selectedPair.before.hrv, selectedPair.after.hrv)}
                    {createDetailRow('음성 안정성', selectedPair.before.voiceStability, selectedPair.after.voiceStability)}
                  </>
                )}
              </div>
            </div>
          </section>
        )}

        {/* History List Section */}
        <section className="glass-card rounded-xl p-6 neon-border">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-white">나의 복용 기록</h2>
            <p className="text-sm text-gray-400">비교하고 싶은 기록을 선택하세요</p>
          </div>
          
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
            {Object.values(pairedData).map((pair: any) => {
              if (pair.before && pair.after) {
                return (
                  <div 
                    key={pair.before.pairId}
                    className={`glass-card p-4 rounded-lg flex items-center justify-between hover:bg-gray-700/50 transition-colors duration-200 cursor-pointer ${
                      selectedPairId === pair.before.pairId ? 'bg-gray-700/50' : ''
                    }`}
                    onClick={() => handleComparisonSelect(pair.before.pairId)}
                  >
                    <div className="flex items-center space-x-4">
                      <input 
                        type="radio" 
                        name="comparison_radio" 
                        checked={selectedPairId === pair.before.pairId}
                        onChange={() => handleComparisonSelect(pair.before.pairId)}
                        className="radio-custom h-5 w-5 bg-gray-800 border-gray-600 text-cyan-500 focus:ring-cyan-600"
                      />
                      <div>
                        <p className="font-bold text-white">{pair.before.date.substring(0, 10)} 복용 기록</p>
                        <p className="text-sm text-gray-400">
                          {pair.before.date.substring(11)} (복용 전) → {pair.after.date.substring(11)} (복용 후)
                        </p>
                      </div>
                    </div>
                    <div className="text-right flex items-center space-x-4">
                      <p className={`text-xl font-bold ${getScoreColor(pair.before.score)}`}>{pair.before.score}점</p>
                      <p className="text-gray-400">→</p>
                      <p className={`text-xl font-bold ${getScoreColor(pair.after.score)}`}>{pair.after.score}점</p>
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        </section>
      </main>
    </div>
  );
}
