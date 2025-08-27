'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  signInWithGoogle, 
  signInWithKakao, 
  signInWithEmail,
  getCurrentUser,
  onAuthStateChange
} from '@/lib/firebase';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // 인증 상태 확인
  useEffect(() => {
    const unsubscribe = onAuthStateChange((user) => {
      if (user) {
        setIsLoggedIn(true);
        router.push('/dashboard');
      } else {
        setIsLoggedIn(false);
      }
    });

    return () => unsubscribe();
  }, [router]);

  // 이미 로그인된 경우 대시보드로 리다이렉트
  if (isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">로그인 중...</p>
        </div>
      </div>
    );
  }

  // 구글 로그인
  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await signInWithGoogle();
      if (result.success) {
        console.log('Google 로그인 성공:', result.user);
        router.push('/dashboard');
      } else {
        setError(result.error || 'Google 로그인에 실패했습니다.');
      }
    } catch (error) {
      setError('Google 로그인 중 오류가 발생했습니다.');
      console.error('Google 로그인 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 카카오 로그인
  const handleKakaoLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await signInWithKakao();
      if (result.success) {
        console.log('카카오 로그인 성공:', result.user);
        router.push('/dashboard');
      } else {
        setError(result.error || '카카오 로그인에 실패했습니다.');
      }
    } catch (error) {
      setError('카카오 로그인 중 오류가 발생했습니다.');
      console.error('카카오 로그인 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 이메일 로그인
  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('이메일과 비밀번호를 입력해주세요.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const result = await signInWithEmail(email, password);
      if (result.success) {
        console.log('이메일 로그인 성공:', result.user);
        router.push('/dashboard');
      } else {
        setError(result.error || '로그인에 실패했습니다.');
      }
    } catch (error) {
      setError('로그인 중 오류가 발생했습니다.');
      console.error('이메일 로그인 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="glass-card rounded-2xl p-8 text-center">
          
          {/* Header */}
          <div className="mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🩺</span>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">엔오건강도우미</h1>
            <p className="text-gray-300">로그인하여 건강 측정을 시작하세요</p>
          </div>

          {/* Social Login Buttons */}
          <div className="space-y-3 mb-8">
            <button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="w-full bg-white text-gray-800 py-3 px-4 rounded-lg hover:bg-gray-100 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span className="text-xl">🔍</span>
              <span>Google로 로그인</span>
            </button>
            
            <button
              onClick={handleKakaoLogin}
              disabled={isLoading}
              className="w-full bg-yellow-400 text-gray-800 py-3 px-4 rounded-lg hover:bg-yellow-300 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span className="text-xl">💬</span>
              <span>카카오로 로그인</span>
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-800 text-gray-400">또는</span>
            </div>
          </div>

          {/* Email Login Form */}
          <form onSubmit={handleEmailLogin} className="space-y-4">
            <div>
              <input
                type="email"
                placeholder="이메일"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                required
              />
            </div>
            
            <div>
              <input
                type="password"
                placeholder="비밀번호"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-3 px-4 rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all duration-300 disabled:opacity-50"
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </button>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-500 rounded text-red-300">
              {error}
            </div>
          )}

          {/* Links */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              계정이 없으신가요?{' '}
              <Link href="/signup" className="text-blue-400 hover:text-blue-300">
                회원가입
              </Link>
            </p>
          </div>

          {/* Back to Home */}
          <div className="mt-6">
            <Link
              href="/"
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← 홈으로 돌아가기
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 