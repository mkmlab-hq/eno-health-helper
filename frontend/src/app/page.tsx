'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Heart, Activity, Camera, Mic, ArrowRight, User, LogIn } from 'lucide-react';

export default function Home() {
  const { currentUser, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && currentUser) {
      router.push('/measure');
    }
  }, [currentUser, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan mx-auto mb-4"></div>
          <p className="text-gray-300">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan mx-auto mb-4"></div>
          <p className="text-gray-300">리디렉션 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <h1 className="text-6xl md:text-7xl font-orbitron font-bold neon-text mb-6 animate-fade-in">
              엔오건강도우미
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto animate-slide-up">
              AI 기반 rPPG와 음성 분석을 통해 정확한 건강 상태를 측정하고 모니터링하세요
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up">
              <button
                onClick={() => router.push('/signup')}
                className="btn-primary text-xl px-8 py-4"
              >
                <User className="w-6 h-6 mr-2 inline" />
                무료로 시작하기
              </button>
              <button
                onClick={() => router.push('/login')}
                className="btn-secondary text-xl px-8 py-4"
              >
                <LogIn className="w-6 h-6 mr-2 inline" />
                로그인
              </button>
              <button
                onClick={() => router.push('/fusion-analysis')}
                className="btn-tertiary text-xl px-8 py-4"
              >
                🧬 융합 분석 데모
              </button>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-neon-cyan/20 rounded-full animate-pulse-slow"></div>
        <div className="absolute top-40 right-20 w-16 h-16 bg-neon-sky/20 rounded-full animate-pulse-slow delay-1000"></div>
        <div className="absolute bottom-40 left-20 w-12 h-12 bg-neon-cyan/30 rounded-full animate-pulse-slow delay-2000"></div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-orbitron font-bold neon-text text-center mb-16">
          핵심 기능
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* rPPG 측정 */}
          <div className="glass-card p-8 text-center hover:scale-105 transition-transform duration-300">
            <div className="w-20 h-20 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-6">
              <Heart className="w-10 h-10 text-red-400" />
            </div>
            <h3 className="text-2xl font-orbitron font-bold text-neon-cyan mb-4">
              rPPG 건강 측정
            </h3>
            <p className="text-gray-300 mb-6">
              카메라를 통해 얼굴의 미세한 색상 변화를 분석하여 심박수, 심박변이도, 스트레스 수준을 정확하게 측정합니다
            </p>
            <div className="text-neon-cyan font-medium">
              <ArrowRight className="w-5 h-5 inline mr-2" />
              비접촉 측정
            </div>
          </div>

          {/* 융합 분석 */}
          <div className="glass-card p-8 text-center hover:scale-105 transition-transform duration-300">
            <div className="w-20 h-20 mx-auto bg-purple-500/20 rounded-full flex items-center justify-center mb-6">
              <div className="text-4xl">🧬</div>
            </div>
            <h3 className="text-2xl font-orbitron font-bold text-neon-cyan mb-4">
              AI 융합 분석
            </h3>
            <p className="text-gray-300 mb-6">
              rPPG와 음성을 동시에 분석하여 4대 디지털 기질을 정확하게 진단하는 혁신적인 AI 융합 기술
            </p>
            <div className="text-neon-cyan font-medium">
              <ArrowRight className="w-5 h-5 inline mr-2" />
              멀티모달 분석
            </div>
          </div>

          {/* 음성 분석 */}
          <div className="glass-card p-8 text-center hover:scale-105 transition-transform duration-300">
            <div className="w-20 h-20 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center mb-6">
              <Mic className="w-10 h-10 text-blue-400" />
            </div>
            <h3 className="text-2xl font-orbitron font-bold text-neon-cyan mb-4">
              음성 품질 분석
            </h3>
            <p className="text-gray-300 mb-6">
              음성의 Jitter, Shimmer 등 음성 품질 지표를 분석하여 전반적인 건강 상태와 피로도를 평가합니다
            </p>
            <div className="text-neon-cyan font-medium">
              <ArrowRight className="w-5 h-5 inline mr-2" />
              AI 음성 분석
            </div>
          </div>

          {/* 실시간 모니터링 */}
          <div className="glass-card p-8 text-center hover:scale-105 transition-transform duration-300">
            <div className="w-20 h-20 mx-auto bg-green-500/20 rounded-full flex items-center justify-center mb-6">
              <Activity className="w-10 h-10 text-green-400" />
            </div>
            <h3 className="text-2xl font-orbitron font-bold text-neon-cyan mb-4">
              실시간 모니터링
            </h3>
            <p className="text-gray-300 mb-6">
              측정 결과를 Firebase에 안전하게 저장하고, 건강 변화 추이를 체계적으로 관리할 수 있습니다
            </p>
            <div className="text-neon-cyan font-medium">
              <ArrowRight className="w-5 h-5 inline mr-2" />
              클라우드 저장
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-orbitron font-bold neon-text text-center mb-16">
          사용 방법
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-neon-cyan/20 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-neon-cyan">1</span>
            </div>
            <h4 className="text-lg font-orbitron font-bold text-white mb-2">계정 생성</h4>
            <p className="text-gray-400 text-sm">간단한 회원가입으로 시작하세요</p>
          </div>
          
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-neon-cyan/20 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-neon-cyan">2</span>
            </div>
            <h4 className="text-lg font-orbitron font-bold text-white mb-2">얼굴 촬영</h4>
            <p className="text-gray-400 text-sm">카메라를 정면으로 바라보세요</p>
          </div>
          
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-neon-cyan/20 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-neon-cyan">3</span>
            </div>
            <h4 className="text-lg font-orbitron font-bold text-white mb-2">음성 녹음</h4>
            <p className="text-gray-400 text-sm">"아" 소리를 10초간 발성하세요</p>
          </div>
          
          <div className="glass-card p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-neon-cyan/20 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-neon-cyan">4</span>
            </div>
            <h4 className="text-lg font-orbitron font-bold text-white mb-2">결과 확인</h4>
            <p className="text-gray-400 text-sm">AI 분석 결과를 확인하세요</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <div className="glass-card p-12">
          <h2 className="text-3xl font-orbitron font-bold neon-text mb-6">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            AI 기술로 정확하고 편리한 건강 측정을 경험해보세요
          </p>
          <button
            onClick={() => router.push('/signup')}
            className="btn-primary text-xl px-8 py-4"
          >
            무료로 시작하기
          </button>
        </div>
      </div>
    </div>
  );
} 