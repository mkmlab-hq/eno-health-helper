import React from 'react';
import Link from 'next/link';
import MKM12Demo from '@/components/landing/MKM12Demo';
import PersonaDiary from '@/components/landing/PersonaDiary';
import ChartAssistant from '@/components/landing/ChartAssistant';

export default function LandingPage() {
  return (
    <div className="bg-slate-950 min-h-screen">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glassmorphism">
        <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold font-orbitron text-white">MKM LAB</div>
          <div className="hidden md:flex space-x-8 text-gray-300">
            <a href="#vision" className="hover:text-sky-400 transition">비전</a>
            <a href="#tech" className="hover:text-sky-400 transition">핵심 기술</a>
            <a href="#demo" className="hover:text-sky-400 transition">MKM12 체험</a>
            <a href="#products" className="hover:text-sky-400 transition">서비스</a>
            <a href="#contact" className="hover:text-sky-400 transition">연락처</a>
          </div>
        </nav>
      </header>

      <main>
        {/* Hero Section */}
        <section id="vision" className="hero-bg min-h-screen flex items-center justify-center text-center pt-20">
          <div className="container mx-auto px-6">
            <h1 className="text-4xl md:text-6xl font-black text-white mb-4 leading-tight font-orbitron">
              500년의 지혜,<br />AI로 건강의 미래를 열다
            </h1>
            <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto mb-8">
              MKM Lab은 전통 사상의학을 최첨단 AI 기술로 재해석하여, 당신의 고유한 건강 상태를 정밀하게 분석하고 초개인화된 솔루션을 제공합니다.
            </p>
            <Link href="/measure" className="bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-8 rounded-full text-lg transition-transform transform hover:scale-105">
              서비스 바로가기
            </Link>
          </div>
        </section>

        {/* Tech Section */}
        <section id="tech" className="py-20">
          <div className="container mx-auto px-6">
            <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
              핵심 기술
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-slate-800 p-6 rounded-lg">
                <h3 className="text-xl font-bold text-white mb-4">rPPG 기술</h3>
                <p className="text-gray-300">
                  카메라만으로 심박수, 심박변이도를 측정하는 비침습 기술
                </p>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <h3 className="text-xl font-bold text-white mb-4">음성 분석</h3>
                <p className="text-gray-300">
                  AI가 음성의 미세한 변화를 분석하여 건강 상태를 진단
                </p>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <h3 className="text-xl font-bold text-white mb-4">MKM12 이론</h3>
                <p className="text-gray-300">
                  4가지 힘과 3가지 모드를 통한 동역학적 건강 분석
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* MKM12 Demo Section - 새로운 섹션 추가 */}
        <section id="demo" className="min-h-screen relative">
          <MKM12Demo className="w-full h-screen" />
        </section>

        {/* Products Section */}
        <section id="products" className="py-20">
          <div className="container mx-auto px-6">
            <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
              서비스 포트폴리오
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              {/* ENO Health Helper */}
              <div className="glass-card p-8 rounded-xl flex flex-col items-center border-2 border-sky-400 shadow-2xl shadow-sky-500/20">
                <div className="text-4xl mb-4">🩺</div>
                <h3 className="text-2xl font-bold text-white mb-2">엔오건강도우미</h3>
                <p className="text-gray-400 flex-grow mb-6">AI rPPG와 음성 분석을 통해 당신의 건강 상태를 35초 만에 측정하고 모니터링합니다.</p>
                <Link href="/measure" className="w-full bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-6 rounded-lg transition text-center">
                  측정 시작하기
                </Link>
              </div>
              
              {/* Persona Diary */}
              <div className="glass-card p-8 rounded-xl flex flex-col items-center">
                <div className="text-4xl mb-4">📔</div>
                <h3 className="text-2xl font-bold text-white mb-2">페르소나 다이어리</h3>
                <p className="text-gray-400 flex-grow mb-6">당신의 일상과 감정을 기록하고, MKM-12 페르소나 이론에 기반한 맞춤형 건강 관리를 제공합니다.</p>
                <Link href="/persona-diary" className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition">
                  일기 시작하기
                </Link>
              </div>
              
              {/* AI Chart Assistant */}
              <div className="glass-card p-8 rounded-xl flex flex-col items-center">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="text-2xl font-bold text-white mb-2">AI 차트 어시스턴트</h3>
                <p className="text-gray-400 flex-grow mb-6">의료진을 위한 AI 보조 도구. 복잡한 환자 차트를 요약하고, 핵심 인사이트를 제공합니다.</p>
                <Link href="/chart-assistant" className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition">
                  차트 분석하기
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section id="contact" className="py-20">
          <div className="container mx-auto px-6 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-8">
              연락처
            </h2>
            <p className="text-gray-300 mb-4">
              MKM Lab과 함께 건강의 미래를 만들어가세요
            </p>
            <a href="mailto:contact@mkmlab.space" className="text-sky-400 hover:text-sky-300">
              contact@mkmlab.space
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}
