'use client';

import React from 'react';

export default function Hero() {
  return (
    <section id="vision" className="hero-bg min-h-screen flex items-center justify-center text-center pt-20">
      <div className="container mx-auto px-6">
        <h1 className="text-4xl md:text-6xl font-black text-white mb-4 leading-tight font-orbitron">
          500년의 지혜,<br />AI로 건강의 미래를 열다
        </h1>
        <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto mb-8">
          MKM Lab은 전통 사상의학을 최첨단 AI 기술로 재해석하여, 당신의 고유한 건강 상태를 정밀하게 분석하고 초개인화된 솔루션을 제공합니다.
        </p>
        <a 
          href="#products" 
          className="bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-8 rounded-full text-lg transition-transform transform hover:scale-105"
        >
          서비스 바로가기
        </a>
      </div>
    </section>
  );
}
