'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Heart, Activity, Mic, Save, TrendingUp, TrendingDown, CheckCircle, UserPlus } from 'lucide-react';
import { signInWithGoogle, signInWithKakao } from '@/lib/firebase';

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
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [signupData, setSignupData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    nickname: '',
    age: '',
    gender: 'male'
  });
  const router = useRouter();

  useEffect(() => {
    // 카카오 SDK 초기화
    // initKakao(); // 카카오 SDK 초기화는 이제 Firebase에서 처리
    
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

  const handleSaveResults = async () => {
    setShowSignupModal(true); // 회원가입 모달 표시
  };

  // 구글 로그인 처리
  const handleGoogleSignIn = async () => {
    try {
      setSaving(true);
      const user = await signInWithGoogle();
      console.log('Google sign-in successful:', user);
      
      // 결과 저장 및 대시보드로 이동
      await handleSocialSignupSuccess(user);
    } catch (error) {
      console.error('Google sign-in failed:', error);
      alert('구글 로그인에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // 카카오 로그인 처리
  const handleKakaoSignIn = async () => {
    try {
      setSaving(true);
      const result = await signInWithKakao();
      console.log('Kakao sign-in successful:', result);
      
      // 결과 저장 및 대시보드로 이동
      await handleSocialSignupSuccess(result.user);
    } catch (error) {
      console.error('Kakao sign-in failed:', error);
      alert('카카오 로그인에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // 소셜 로그인 성공 후 처리
  const handleSocialSignupSuccess = async (user: any) => {
    try {
      // 결과 저장 로직 (실제 구현 시)
      await new Promise(resolve => setTimeout(resolve, 1000)); // 시뮬레이션
      setSaved(true);
      setShowSignupModal(false);
      
      // 회원가입 완료 후 Before/After 비교 페이지로 이동
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000);
    } catch (error) {
      console.error('Result save failed:', error);
    }
  };

  const handleSignup = async () => {
    if (signupData.password !== signupData.confirmPassword) {
      alert('비밀번호가 일치하지 않습니다.');
      return;
    }

    setSaving(true);
    try {
      // 회원가입 및 결과 저장 로직 (실제 구현 시)
      await new Promise(resolve => setTimeout(resolve, 2000)); // 시뮬레이션
      setSaved(true);
      setShowSignupModal(false);
      
      // 회원가입 완료 후 Before/After 비교 페이지로 이동
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000);
    } catch (error) {
      console.error('Signup failed:', error);
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
          <p className="text-gray-300 text-sm">안녕하세요, 게스트님</p>
        </div>
        <div className="flex space-x-2">
          <button onClick={() => router.push('/')} className="btn-secondary flex items-center space-x-2">
            <span>홈</span>
          </button>
          <button onClick={() => router.push('/measure')} className="btn-secondary flex items-center space-x-2">
            <span>다시 측정</span>
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
                  처리 중...
                </>
              ) : saved ? (
                <>
                  <CheckCircle className="w-5 h-5 mr-2" />
                  저장 완료
                </>
              ) : (
                <>
                  <Save className="w-5 h-5 mr-2" />
                  결과 저장 및 회원가입
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
              ✓ 회원가입 완료! Before/After 비교 페이지로 이동합니다...
            </p>
          )}
        </div>
      </main>

      {/* 회원가입 모달 */}
      {showSignupModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="glass-card p-8 max-w-md mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold text-neon-cyan mb-6 text-center">
              🎯 회원가입 및 결과 저장
            </h3>
            
            {/* 소셜 로그인 버튼들 */}
            <div className="space-y-3 mb-6">
              <button 
                onClick={handleGoogleSignIn}
                disabled={saving}
                className="w-full bg-white text-gray-900 py-3 px-4 rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 inline mr-2" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google로 1초 가입
              </button>
              
              <button 
                onClick={handleKakaoSignIn}
                disabled={saving}
                className="w-full bg-yellow-400 text-gray-900 py-3 px-4 rounded-lg font-medium hover:bg-yellow-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5 inline mr-2" viewBox="0 0 24 24">
                  <path fill="#000000" d="M12 3C6.48 3 2 6.48 2 12s4.48 9 9 9c1.66 0 3.22-.5 4.5-1.36L19.59 21l.41-.41L20.59 20l-1.36-1.36C21.5 17.22 22 15.66 22 14c0-5.52-4.48-10-10-10z"/>
                </svg>
                카카오톡으로 1초 가입
              </button>
            </div>

            <div className="text-center text-gray-400 mb-4">
              또는
            </div>
            
            {/* 기존 이메일 회원가입 폼 */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">이메일</label>
                <input
                  type="email"
                  value={signupData.email}
                  onChange={(e) => setSignupData(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-neon-cyan focus:border-transparent"
                  placeholder="your@email.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">비밀번호</label>
                <input
                  type="password"
                  value={signupData.password}
                  onChange={(e) => setSignupData(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-neon-cyan focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">비밀번호 확인</label>
                <input
                  type="password"
                  value={signupData.confirmPassword}
                  onChange={(e) => setSignupData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-neon-cyan focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">닉네임</label>
                <input
                  type="text"
                  value={signupData.nickname}
                  onChange={(e) => setSignupData(prev => ({ ...prev, nickname: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-neon-cyan focus:border-transparent"
                  placeholder="닉네임을 입력하세요"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">나이</label>
                  <input
                    type="number"
                    value={signupData.age}
                    onChange={(e) => setSignupData(prev => ({ ...prev, age: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-neon-cyan focus:border-transparent"
                    placeholder="25"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">성별</label>
                  <select
                    value={signupData.gender}
                    onChange={(e) => setSignupData(prev => ({ ...prev, gender: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-neon-cyan focus:border-transparent"
                  >
                    <option value="male">남성</option>
                    <option value="female">여성</option>
                    <option value="other">기타</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 회원가입 버튼 */}
            <div className="flex space-x-4 justify-center">
              <button
                onClick={() => setShowSignupModal(false)}
                className="btn-secondary px-6 py-3"
              >
                취소
              </button>
              <button
                onClick={handleSignup}
                disabled={saving}
                className="btn-primary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? '처리 중...' : '회원가입 완료'}
              </button>
            </div>

            {/* 안내 메시지 */}
            <p className="text-xs text-gray-500 text-center mt-4">
              소셜 로그인으로 1초 만에 가입하거나, 이메일로 회원가입 후 Before/After 비교 대시보드를 이용할 수 있습니다.
            </p>
          </div>
        </div>
      )}
    </div>
  );
} 