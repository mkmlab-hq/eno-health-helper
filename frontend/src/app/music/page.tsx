'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/navigation';
import MusicGenerator from '../../components/MusicGenerator';
import { EmotionData } from '../../lib/sunoAI';

export default function MusicPage() {
  const { currentUser, logout } = useAuth();
  const router = useRouter();
  const [emotionData, setEmotionData] = useState<EmotionData | null>(null);

  // 로그인 상태 확인
  useEffect(() => {
    if (!currentUser) {
      router.push('/login');
      return;
    }

    // 임시 감정 데이터 생성 (실제로는 건강 측정 결과에서 가져와야 함)
    setEmotionData({
      heartRate: 75,
      stressLevel: 'medium',
      voiceTone: 120,
      hrv: 45,
      userId: currentUser.uid,
    });
  }, [currentUser, router]);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('로그아웃 실패:', error);
    }
  };

  const handleMusicGenerated = (music: any) => {
    console.log('음악 생성 완료:', music);
    // 여기서 Firebase에 음악 정보 저장 가능
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl text-red-400 mb-4">접근 권한이 없습니다</h1>
          <button onClick={() => router.push('/login')} className="btn-primary">
            로그인하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <header className="glass-card m-4 p-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-orbitron font-bold neon-text">엔오건강도우미</h1>
          <p className="text-gray-300 text-sm">안녕하세요, {currentUser.email}님</p>
        </div>
        <div className="flex space-x-4">
          <button 
            onClick={() => router.push('/measure')} 
            className="btn-secondary"
          >
            건강 측정하기
          </button>
          <button onClick={handleLogout} className="btn-secondary">
            로그아웃
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-4">
        {emotionData ? (
          <MusicGenerator 
            emotionData={emotionData}
            onMusicGenerated={handleMusicGenerated}
          />
        ) : (
          <div className="glass-card p-8 text-center animate-fade-in">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan mx-auto mb-4"></div>
            <p className="text-gray-300">감정 데이터를 불러오는 중...</p>
          </div>
        )}
      </main>
    </div>
  );
} 