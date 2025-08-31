'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import MKM12Demo from '@/components/landing/MKM12Demo';

export default function PersonaDiaryHome() {
  const [currentPersona, setCurrentPersona] = useState('A1-태양형');
  const [energyLevel, setEnergyLevel] = useState(7);
  const [mood, setMood] = useState('활기참');

  return (
    <div className="min-h-screen">
      {/* 헤더 */}
      <header className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center shadow-neon-cyan">
              <div className="w-6 h-6 text-white neon-glow">📔</div>
            </div>
            <div>
              <h1 className="text-2xl font-orbitron font-bold text-white neon-text">
                페르소나 다이어리
              </h1>
              <p className="text-sm text-gray-300 font-noto">MKM12 기반 개인 AI 동반자</p>
            </div>
          </div>
          
          <Link 
            href="/"
            className="glass-button text-gray-300 hover:text-eno-400 transition-colors font-noto"
          >
            🏠 홈으로
          </Link>
        </div>
      </header>

      {/* MKM12 동역학 구름 섹션 */}
      <section className="relative min-h-[60vh]">
        <MKM12Demo className="w-full h-full" />
        
        {/* 오버레이 텍스트 */}
        <div className="absolute inset-0 flex items-center justify-center z-20">
          <div className="text-center text-white">
            <h2 className="text-4xl md:text-5xl font-orbitron font-bold mb-4 neon-text">
              35초, 당신의 내면을 읽는 시간
            </h2>
            <p className="text-xl text-gray-300 mb-8 font-noto">
              MKM12 동역학 구름이 당신의 현재 상태를 보여줍니다
            </p>
            <button className="glass-button text-lg px-8 py-4 font-semibold neon-glow">
              🔍 즉시 검사 시작
            </button>
          </div>
        </div>
      </section>

      {/* 오늘의 페르소나 요약 */}
      <section className="px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <h3 className="text-2xl font-orbitron font-bold text-white mb-8 neon-text text-center">
            🌟 오늘의 페르소나 요약
          </h3>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* 현재 페르소나 */}
            <div className="glass-card p-6 rounded-2xl text-center">
              <div className="text-4xl mb-4">👤</div>
              <h4 className="text-lg font-semibold text-white mb-2">현재 페르소나</h4>
              <p className="text-eno-400 font-bold text-xl">{currentPersona}</p>
              <p className="text-gray-400 text-sm mt-2">태양의 에너지가 강하게 느껴집니다</p>
            </div>

            {/* 에너지 레벨 */}
            <div className="glass-card p-6 rounded-2xl text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h4 className="text-lg font-semibold text-white mb-2">에너지 레벨</h4>
              <div className="text-3xl font-bold text-eno-400 mb-2">{energyLevel}/10</div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-eno-400 to-eno-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${energyLevel * 10}%` }}
                />
              </div>
            </div>

            {/* 오늘의 기분 */}
            <div className="glass-card p-6 rounded-2xl text-center">
              <div className="text-4xl mb-4">😊</div>
              <h4 className="text-lg font-semibold text-white mb-2">오늘의 기분</h4>
              <p className="text-eno-400 font-bold text-xl">{mood}</p>
              <p className="text-gray-400 text-sm mt-2">긍정적인 에너지가 넘칩니다</p>
            </div>
          </div>
        </div>
      </section>

      {/* 빠른 액션 */}
      <section className="px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <h3 className="text-2xl font-orbitron font-bold text-white mb-8 neon-text text-center">
            🚀 빠른 액션
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <Link 
              href="/persona-diary/log"
              className="glass-card p-8 rounded-2xl text-center hover:scale-105 transition-transform duration-300"
            >
              <div className="text-5xl mb-4">✍️</div>
              <h4 className="text-xl font-semibold text-white mb-2">오늘의 일기 작성</h4>
              <p className="text-gray-300">기분과 활동을 기록하고 MKM12 분석을 시작하세요</p>
            </Link>

            <Link 
              href="/persona-diary/analysis"
              className="glass-card p-8 rounded-2xl text-center hover:scale-105 transition-transform duration-300"
            >
              <div className="text-5xl mb-4">📊</div>
              <h4 className="text-xl font-semibold text-white mb-2">디지털 지문 확인</h4>
              <p className="text-gray-300">당신만의 고유한 MKM12 패턴을 발견하세요</p>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
