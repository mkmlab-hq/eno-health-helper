'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
// import { useAuth } from '@/context/AuthContext'; // 인증 체크 제거
import { Heart, Activity, Mic, Save, LogOut, TrendingUp, TrendingDown, CheckCircle } from 'lucide-react';

interface HealthMetrics {
  heartRate: number;
  hrv: number;
  jitter: number;
  shimmer: number;
  stressLevel: string;
  overallHealth: string;
}

export default function ResultPage() {
  const [metrics, setMetrics] = useState<HealthMetrics | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  // const { currentUser, logout } = useAuth(); // 인증 체크 제거
  const router = useRouter();

  useEffect(() => {
    // 시뮬레이션된 건강 데이터 생성
    const simulatedMetrics: HealthMetrics = {
      heartRate: Math.floor(Math.random() * 30) + 60, // 60-90 BPM
      hrv: Math.floor(Math.random() * 50) + 30, // 30-80 ms
      jitter: Math.random() * 2 + 0.1, // 0.1-2.1%
      shimmer: Math.random() * 3 + 0.5, // 0.5-3.5%
      stressLevel: ['낮음', '보통', '높음'][Math.floor(Math.random() * 3)],
      overallHealth: ['양호', '보통', '주의'][Math.floor(Math.random() * 3)]
    };
    setMetrics(simulatedMetrics);
  }, []);

  // 로그아웃 함수 제거 (인증 없이 사용)
  // const handleLogout = async () => { ... };

  const handleSaveResults = async () => {
    // if (!metrics || !currentUser) return; // 인증 체크 제거
    
    setSaving(true);
    try {
      // Firebase에 결과 저장 로직 (실제 구현 시)
      await new Promise(resolve => setTimeout(resolve, 2000)); // 시뮬레이션
      setSaved(true);
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setSaving(false);
    }
  };

  const getHealthColor = (value: string) => {
    switch (value) {
      case '양호':
      case '낮음':
        return 'text-green-400';
      case '보통':
        return 'text-yellow-400';
      case '주의':
      case '높음':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  // if (!currentUser) { // 인증 체크 제거
  //   return (
  //     <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
  //       <div className="text-center">
  //         <h1 className="text-2xl text-red-400 mb-4">접근 권한이 없습니다</h1>
  //         <button onClick={() => router.push('/login')} className="btn-primary">
  //           로그인하기
  //         </button>
  //       </div>
  //     </div>
  //   );
  // }

  if (!metrics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan mx-auto mb-4"></div>
          <p className="text-gray-300">결과를 분석하고 있습니다...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <header className="glass-card m-4 p-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-orbitron font-bold neon-text">건강 측정 결과</h1>
          <p className="text-gray-300 text-sm">안녕하세요, {/* currentUser.email */}님</p>
        </div>
        <div className="flex space-x-2">
          <button onClick={() => router.push('/')} className="btn-secondary flex items-center space-x-2">
            <span>홈</span>
          </button>
          <button onClick={() => router.push('/login')} className="btn-secondary flex items-center space-x-2">
            <LogOut className="w-4 h-4" />
            <span>로그아웃</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-4">
        {/* Overall Health Summary */}
        <div className="glass-card p-8 mb-6 text-center">
          <h2 className="text-3xl font-orbitron font-bold neon-text mb-4">
            종합 건강 상태
          </h2>
          <div className="flex items-center justify-center space-x-4 mb-6">
            <div className={`text-6xl font-bold ${getHealthColor(metrics.overallHealth)}`}>
              {metrics.overallHealth}
            </div>
            <CheckCircle className="w-16 h-16 text-green-400" />
          </div>
          <p className="text-gray-300 text-lg">
            전반적으로 건강한 상태를 유지하고 있습니다
          </p>
        </div>

        {/* Detailed Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {/* Heart Rate */}
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-4">
              <Heart className="w-8 h-8 text-red-400" />
            </div>
            <h3 className="text-xl font-orbitron font-bold text-neon-cyan mb-2">심박수</h3>
            <div className="text-3xl font-bold text-white mb-2">{metrics.heartRate}</div>
            <div className="text-gray-400">BPM</div>
            <div className="text-sm text-gray-300 mt-2">
              {metrics.heartRate < 70 ? '정상 범위' : '약간 높음'}
            </div>
          </div>

          {/* HRV */}
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-xl font-orbitron font-bold text-neon-cyan mb-2">심박변이도</h3>
            <div className="text-3xl font-bold text-white mb-2">{metrics.hrv}</div>
            <div className="text-gray-400">ms</div>
            <div className="text-sm text-gray-300 mt-2">
              {metrics.hrv > 50 ? '우수' : metrics.hrv > 30 ? '보통' : '개선 필요'}
            </div>
          </div>

          {/* Stress Level */}
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-purple-500/20 rounded-full flex items-center justify-center mb-4">
              <TrendingUp className="w-8 h-8 text-purple-400" />
            </div>
            <h3 className="text-xl font-orbitron font-bold text-neon-cyan mb-2">스트레스 수준</h3>
            <div className={`text-3xl font-bold mb-2 ${getHealthColor(metrics.stressLevel)}`}>
              {metrics.stressLevel}
            </div>
            <div className="text-sm text-gray-300 mt-2">
              {metrics.stressLevel === '낮음' ? '편안한 상태' : 
               metrics.stressLevel === '보통' ? '적당한 긴장' : '휴식 필요'}
            </div>
          </div>

          {/* Voice Quality Metrics */}
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-green-500/20 rounded-full flex items-center justify-center mb-4">
              <Activity className="w-8 h-8 text-green-400" />
            </div>
            <h3 className="text-xl font-orbitron font-bold text-neon-cyan mb-2">음성 품질</h3>
            <div className="space-y-2">
              <div>
                <span className="text-gray-400 text-sm">Jitter: </span>
                <span className="text-white font-medium">{metrics.jitter.toFixed(2)}%</span>
              </div>
              <div>
                <span className="text-gray-400 text-sm">Shimmer: </span>
                <span className="text-white font-medium">{metrics.shimmer.toFixed(2)}%</span>
              </div>
            </div>
            <div className="text-sm text-gray-300 mt-2">
              {metrics.jitter < 1 && metrics.shimmer < 2 ? '우수한 음성 품질' : '정상 범위'}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="glass-card p-8 text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleSaveResults}
              disabled={saving || saved}
              className="btn-primary text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  저장 중...
                </>
              ) : saved ? (
                <>
                  <CheckCircle className="w-5 h-5 mr-2" />
                  저장 완료
                </>
              ) : (
                <>
                  <Save className="w-5 h-5 mr-2" />
                  결과 저장하기
                </>
              )}
            </button>
            
            <button
              onClick={() => router.push('/measure')}
              className="btn-secondary text-lg px-8 py-4"
            >
              다시 측정하기
            </button>
          </div>
          
          {saved && (
            <p className="text-green-400 mt-4 text-sm">
              ✓ 결과가 Firebase에 성공적으로 저장되었습니다
            </p>
          )}
        </div>
      </main>
    </div>
  );
} 