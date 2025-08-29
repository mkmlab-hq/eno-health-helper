"use client";

import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 flex items-center justify-center p-4">
      <div className="text-center max-w-md w-full">
        {/* 로고 및 브랜딩 */}
        <div className="w-24 h-24 bg-gradient-to-r from-eno-500 to-eno-400 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
          <div className="w-12 h-12 text-white neon-glow">🩺</div>
        </div>
        
        <h1 className="text-4xl font-bold text-white mb-4 neon-text">
          엔오건강도우미
        </h1>
        
        <p className="text-gray-300 mb-12 text-lg">
          AI 기반 초개인화 건강 통찰 서비스
        </p>
        
        {/* 메인 액션 버튼 - 카메라/마이크 테스트 제거 */}
        <div className="mb-12">
          <Link
            href="/measure"
            className="block w-full bg-gradient-to-r from-eno-600 to-eno-500 text-white px-8 py-6 rounded-xl font-semibold text-xl transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-eno-500/25 hover:-translate-y-1 transform"
          >
            🚀 건강 측정 시작하기
          </Link>
        </div>
        
        {/* 서비스 특징 - 더 시각적으로 개선 */}
        <div className="glass-card rounded-2xl p-6 mb-8">
          <h3 className="text-white font-semibold text-lg mb-4 neon-text">
            ✨ 서비스 특징
          </h3>
          <div className="space-y-4 text-sm text-gray-300">
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-700/50 transition-colors">
              <span className="text-2xl">🎯</span>
              <span className="font-medium">AI 기반 건강 분석</span>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-700/50 transition-colors">
              <span className="text-2xl">🎵</span>
              <span className="font-medium">개인 맞춤형 치유 음악</span>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-700/50 transition-colors">
              <span className="text-2xl">💬</span>
              <span className="font-medium">AI 건강 상담</span>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-700/50 transition-colors">
              <span className="text-2xl">📊</span>
              <span className="font-medium">실시간 건강 모니터링</span>
            </div>
          </div>
        </div>
        
        {/* 시작 안내 - 더 간단하게 */}
        <div className="text-center">
          <p className="text-eno-400 font-medium text-lg">
            바로 시작하세요! 🎉
          </p>
        </div>
      </div>
    </div>
  );
} 