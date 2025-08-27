"use client";

import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
          <div className="w-12 h-12 text-white">🩺</div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-4">엔오건강도우미</h2>
        <p className="text-gray-300 mb-6">건강 측정 서비스에 오신 것을 환영합니다</p>
        
        <div className="space-y-4">
          <Link
            href="/test"
            className="block bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors"
          >
            카메라/마이크 테스트
          </Link>
          
          <Link
            href="/measure"
            className="block bg-green-500 text-white px-8 py-3 rounded-lg hover:bg-green-600 transition-colors"
          >
            건강 측정 시작
          </Link>
        </div>
      </div>
    </div>
  );
} 