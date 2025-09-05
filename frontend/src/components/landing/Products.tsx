'use client';

import React from 'react';

export default function Products() {
  return (
    <section id="products" className="py-20 bg-slate-900">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-12 font-orbitron">서비스 포트폴리오</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* ENO Health Helper */}
          <div className="glassmorphism p-8 rounded-xl flex flex-col items-center border-2 border-sky-400 shadow-2xl shadow-sky-500/20">
            <div className="text-4xl mb-4">🩺</div>
            <h3 className="text-2xl font-bold text-white mb-2">엔오건강도우미</h3>
            <p className="text-gray-400 flex-grow mb-6">
              AI rPPG와 음성 분석을 통해 당신의 건강 상태를 35초 만에 측정하고 모니터링합니다.
            </p>
            <a 
              href="#" 
              className="w-full bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              측정 시작하기
            </a>
          </div>
          
          {/* Persona Diary */}
          <div className="glassmorphism p-8 rounded-xl flex flex-col items-center">
            <div className="text-4xl mb-4">📔</div>
            <h3 className="text-2xl font-bold text-white mb-2">페르소나 다이어리</h3>
            <p className="text-gray-400 flex-grow mb-6">
              당신의 일상과 감정을 기록하고, MKM-12 페르소나 이론에 기반한 맞춤형 건강 관리를 제공합니다.
            </p>
            <a 
              href="#" 
              className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              자세히 보기
            </a>
          </div>
          
          {/* AI Chart Assistant */}
          <div className="glassmorphism p-8 rounded-xl flex flex-col items-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-2xl font-bold text-white mb-2">AI 차트 어시스턴트</h3>
            <p className="text-gray-400 flex-grow mb-6">
              의료진을 위한 AI 보조 도구. 복잡한 환자 차트를 요약하고, 핵심 인사이트를 제공합니다.
            </p>
            <a 
              href="/chart-assistant" 
              className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              자세히 보기
            </a>
          </div>
          
          {/* AI Chart Dowmi */}
          <div className="glassmorphism p-8 rounded-xl flex flex-col items-center border-2 border-eno-400 shadow-2xl shadow-eno-500/20">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-2xl font-bold text-white mb-2">AI 차트 도우미</h3>
            <p className="text-gray-400 flex-grow mb-6">
              의료진을 위한 완전한 AI 진단 도구. 차트 분석부터 SOAP 차트 생성까지 원스톱 솔루션.
            </p>
            <a 
              href="/chart-dowmi" 
              className="w-full bg-eno-500 hover:bg-eno-600 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              시작하기
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
