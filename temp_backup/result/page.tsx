'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { signOutUser, saveMeasurement } from '../../../lib/firebase';

interface MeasurementResult {
  bpm: number;
  hrv: number;
  jitter: number;
  shimmer: number;
  timestamp: Date;
  stressLevel: 'low' | 'medium' | 'high';
  healthScore: number;
  recommendations: string[];
}

export default function ResultPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [measurementResult, setMeasurementResult] = useState<MeasurementResult | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState('');

  // 인증 상태 확인
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // 측정 결과 생성 (실제로는 측정 페이지에서 전달받아야 함)
  useEffect(() => {
    if (user && !measurementResult) {
      // 시뮬레이션된 측정 결과 생성
      const mockResult: MeasurementResult = {
        bpm: Math.floor(Math.random() * 30) + 60,
        hrv: Math.floor(Math.random() * 20) + 30,
        jitter: Math.random() * 2 + 0.5,
        shimmer: Math.random() * 3 + 1,
        timestamp: new Date(),
        stressLevel: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low',
        healthScore: Math.floor(Math.random() * 30) + 70,
        recommendations: [
          '규칙적인 운동을 통해 심혈관 건강을 개선하세요',
          '충분한 수면을 취하여 스트레스를 줄이세요',
          '건강한 식습관을 유지하세요',
          '정기적인 건강 검진을 받으세요'
        ]
      };
      setMeasurementResult(mockResult);
    }
  }, [user, measurementResult]);

  // 로그아웃 처리
  const handleLogout = async () => {
    try {
      await signOutUser();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // 결과 저장
  const handleSaveResult = async () => {
    if (!user || !measurementResult) return;

    setIsSaving(true);
    setError('');

    try {
      await saveMeasurement(user.uid, {
        ...measurementResult,
        timestamp: measurementResult.timestamp.toISOString()
      });
      setSaveSuccess(true);
      
      // 3초 후 성공 메시지 숨기기
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      setError('결과 저장에 실패했습니다. 다시 시도해주세요.');
      console.error('Save error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // 스트레스 레벨에 따른 색상 및 텍스트
  const getStressLevelInfo = (level: string) => {
    switch (level) {
      case 'low':
        return { color: 'text-green-400', bg: 'bg-green-900/20', border: 'border-green-500/30', text: '낮음' };
      case 'medium':
        return { color: 'text-yellow-400', bg: 'bg-yellow-900/20', border: 'border-yellow-500/30', text: '보통' };
      case 'high':
        return { color: 'text-red-400', bg: 'bg-red-900/20', border: 'border-red-500/30', text: '높음' };
      default:
        return { color: 'text-slate-400', bg: 'bg-slate-900/20', border: 'border-slate-500/30', text: '알 수 없음' };
    }
  };

  // 건강 점수에 따른 색상
  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-blue-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-400 rounded-full animate-spin border-t-transparent mx-auto mb-4"></div>
          <p className="text-slate-300">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!user || !measurementResult) {
    return null;
  }

  const stressInfo = getStressLevelInfo(measurementResult.stressLevel);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 헤더 */}
      <header className="bg-slate-800/50 backdrop-blur-xl border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                엔오건강도우미
              </h1>
              <span className="text-slate-400">|</span>
              <span className="text-slate-300 font-noto-sans">측정 결과</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-slate-300 text-sm">
                {user.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors duration-200"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* 성공/에러 메시지 */}
          {saveSuccess && (
            <div className="p-4 bg-green-900/20 border border-green-500/30 rounded-lg text-green-400 text-center">
              측정 결과가 성공적으로 저장되었습니다! 🎉
            </div>
          )}
          
          {error && (
            <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-lg text-red-400 text-center">
              {error}
            </div>
          )}

          {/* 측정 시간 */}
          <div className="text-center">
            <p className="text-slate-400 text-sm">
              측정 시간: {measurementResult.timestamp.toLocaleString('ko-KR')}
            </p>
          </div>

          {/* 주요 지표 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20 text-center">
              <div className="text-cyan-400 text-4xl mb-2">💓</div>
              <h3 className="text-slate-300 font-semibold mb-2">심박수</h3>
              <p className="text-3xl font-bold text-cyan-400">{measurementResult.bpm}</p>
              <p className="text-slate-400 text-sm">BPM</p>
            </div>
            
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20 text-center">
              <div className="text-sky-400 text-4xl mb-2">📊</div>
              <h3 className="text-slate-300 font-semibold mb-2">심박변이도</h3>
              <p className="text-3xl font-bold text-sky-400">{measurementResult.hrv}</p>
              <p className="text-slate-400 text-sm">ms</p>
            </div>
            
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20 text-center">
              <div className="text-purple-400 text-4xl mb-2">🎵</div>
              <h3 className="text-slate-300 font-semibold mb-2">Jitter</h3>
              <p className="text-3xl font-bold text-purple-400">{measurementResult.jitter.toFixed(1)}</p>
              <p className="text-slate-400 text-sm">%</p>
            </div>
            
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20 text-center">
              <div className="text-pink-400 text-4xl mb-2">🎶</div>
              <h3 className="text-slate-300 font-semibold mb-2">Shimmer</h3>
              <p className="text-3xl font-bold text-pink-400">{measurementResult.shimmer.toFixed(1)}</p>
              <p className="text-slate-400 text-sm">%</p>
            </div>
          </div>

          {/* 종합 분석 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* 스트레스 레벨 */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-slate-200 mb-4">스트레스 레벨</h3>
              <div className={`p-4 rounded-lg ${stressInfo.bg} border ${stressInfo.border}`}>
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">현재 스트레스:</span>
                  <span className={`text-xl font-bold ${stressInfo.color}`}>
                    {stressInfo.text}
                  </span>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-slate-700 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-300 ${
                        stressInfo.color === 'text-green-400' ? 'bg-green-400' :
                        stressInfo.color === 'text-yellow-400' ? 'bg-yellow-400' : 'bg-red-400'
                      }`}
                      style={{ 
                        width: `${stressInfo.text === '낮음' ? 30 : stressInfo.text === '보통' ? 60 : 90}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* 종합 건강 점수 */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-slate-200 mb-4">종합 건강 점수</h3>
              <div className="text-center">
                <div className={`text-6xl font-bold ${getHealthScoreColor(measurementResult.healthScore)} mb-2`}>
                  {measurementResult.healthScore}
                </div>
                <div className="text-slate-400">/ 100점</div>
                <div className="mt-4">
                  <div className="w-full bg-slate-700 rounded-full h-4">
                    <div 
                      className={`h-4 rounded-full transition-all duration-300 ${
                        getHealthScoreColor(measurementResult.healthScore).replace('text-', 'bg-')
                      }`}
                      style={{ width: `${measurementResult.healthScore}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 건강 권장사항 */}
          <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-slate-200 mb-4">건강 권장사항</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {measurementResult.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start space-x-3 p-4 bg-slate-800/30 rounded-lg border border-slate-600">
                  <div className="text-green-400 text-xl mt-1">✓</div>
                  <p className="text-slate-300">{recommendation}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 액션 버튼 */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <button
              onClick={handleSaveResult}
              disabled={isSaving}
              className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold text-xl rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? '저장 중...' : '결과 저장하기'}
            </button>
            
            <button
              onClick={() => router.push('/measure')}
              className="px-8 py-4 bg-slate-600 text-white font-bold text-xl rounded-xl hover:bg-slate-700 transition-all duration-200"
            >
              다시 측정하기
            </button>
            
            <button
              onClick={() => router.push('/')}
              className="px-8 py-4 bg-slate-700 text-white font-bold text-xl rounded-xl hover:bg-slate-600 transition-all duration-200"
            >
              홈으로 돌아가기
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
