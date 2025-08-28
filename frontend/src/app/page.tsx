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
        
        {/* 메인 액션 버튼들 */}
        <div className="space-y-6 mb-12">
          {/* 건강 측정 시작 - 주요 액션 */}
          <Link
            href="/measure"
            className="block w-full bg-gradient-to-r from-eno-600 to-eno-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-eno-500/25 hover:-translate-y-1"
          >
            🚀 건강 측정 시작하기
          </Link>
          
          {/* 카메라/마이크 테스트 */}
          <Link
            href="/test"
            className="block w-full bg-gray-700 hover:bg-gray-600 text-white px-8 py-3 rounded-xl font-medium transition-all duration-300 border border-gray-600 hover:border-eno-500"
          >
            📱 카메라/마이크 테스트
          </Link>
        </div>
        
        {/* 서비스 특징 */}
        <div className="glass-card rounded-2xl p-6 mb-8">
          <h3 className="text-white font-semibold text-lg mb-4 neon-text">
            ✨ 서비스 특징
          </h3>
          <div className="space-y-3 text-sm text-gray-300">
            <div className="flex items-center space-x-3">
              <span className="text-eno-400">🎯</span>
              <span>AI 기반 건강 분석</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-eno-400">🎵</span>
              <span>개인 맞춤형 치유 음악</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-eno-400">💬</span>
              <span>AI 건강 상담</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-eno-400">📊</span>
              <span>실시간 건강 모니터링</span>
            </div>
          </div>
        </div>
        
        {/* 시작 안내 */}
        <div className="text-center">
          <p className="text-gray-400 text-sm mb-2">
            간단한 카메라/마이크 테스트 후
          </p>
          <p className="text-eno-400 font-medium">
            건강 측정을 시작하세요! 🎉
          </p>
        </div>
      </div>
    </div>
  );
} 