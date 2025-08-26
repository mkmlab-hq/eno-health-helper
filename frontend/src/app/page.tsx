"use client";

import { useEffect } from 'react';

export default function Home() {
  // 바로 측정 페이지로 리다이렉트
  useEffect(() => {
    window.location.href = '/measure';
  }, []);

  // 로딩 화면 (리다이렉트 중)
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
          <div className="w-12 h-12 text-white">🩺</div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-4">엔오건강도우미</h2>
        <p className="text-gray-300 mb-6">건강 측정을 시작합니다...</p>
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      </div>
    </div>
  );
} 