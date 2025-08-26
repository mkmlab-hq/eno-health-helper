import React from 'react';
import Link from 'next/link';
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
          <div className="container mx-auto px-6 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-12 font-orbitron">핵심 기술력</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="glassmorphism p-6 rounded-lg transition-all duration-300 feature-card">
                <h3 className="text-xl font-bold text-sky-400 mb-2">rPPG 건강 측정</h3>
                <p className="text-gray-400 text-sm">카메라를 통해 심박수, HRV, 스트레스 수준을 비접촉으로 정밀하게 측정하는 기술</p>
              </div>
              <div className="glassmorphism p-6 rounded-lg transition-all duration-300 feature-card">
                <h3 className="text-xl font-bold text-sky-400 mb-2">음성 품질 분석</h3>
                <p className="text-gray-400 text-sm">목소리의 미세 떨림(Jitter, Shimmer)을 분석하여 건강 상태 및 스트레스를 추론하는 기술</p>
              </div>
              <div className="glassmorphism p-6 rounded-lg transition-all duration-300 feature-card">
                <h3 className="text-xl font-bold text-sky-400 mb-2">AI 기반 기질 분석</h3>
                <p className="text-gray-400 text-sm">57만개 동적 데이터를 통해 4가지 '디지털 기질'을 발견하고 사상의학과 연결하는 기술</p>
              </div>
            </div>
          </div>
        </section>

        {/* Products Section */}
        <section id="products" className="py-20 bg-slate-900">
          <div className="container mx-auto px-6 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-12 font-orbitron">서비스 포트폴리오</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* ENO Health Helper */}
              <div className="glassmorphism p-8 rounded-xl flex flex-col items-center border-2 border-sky-400 shadow-2xl shadow-sky-500/20">
                <div className="text-4xl mb-4">🩺</div>
                <h3 className="text-2xl font-bold text-white mb-2">엔오건강도우미</h3>
                <p className="text-gray-400 flex-grow mb-6">AI rPPG와 음성 분석을 통해 당신의 건강 상태를 35초 만에 측정하고 모니터링합니다.</p>
                <a href="https://eno.no1kmedi.com" target="_blank" rel="noopener noreferrer" className="w-full bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-6 rounded-lg transition text-center">
                  측정 시작하기
                </a>
              </div>
              {/* Persona Diary */}
              <div className="glassmorphism p-8 rounded-xl flex flex-col items-center">
                <div className="text-4xl mb-4">📔</div>
                <h3 className="text-2xl font-bold text-white mb-2">페르소나 다이어리</h3>
                <p className="text-gray-400 flex-grow mb-6">당신의 일상과 감정을 기록하고, MKM-12 페르소나 이론에 기반한 맞춤형 건강 관리를 제공합니다.</p>
                <a href="#" className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition">자세히 보기</a>
              </div>
              {/* AI Chart Assistant */}
              <div className="glassmorphism p-8 rounded-xl flex flex-col items-center">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="text-2xl font-bold text-white mb-2">AI 차트 어시스턴트</h3>
                <p className="text-gray-400 flex-grow mb-6">의료진을 위한 AI 보조 도구. 복잡한 환자 차트를 요약하고, 핵심 인사이트를 제공합니다.</p>
                <a href="#" className="w-full bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition">자세히 보기</a>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer id="contact" className="py-12 bg-slate-950">
        <div className="container mx-auto px-6 text-center text-gray-500 text-xs leading-relaxed">
          <p className="font-bold text-gray-400 mb-2">MKM Lab <span className="font-normal text-gray-600">(분자한의학 연구소 Brand)</span></p>
          <p>주식회사 목소리네트워크 | 사업자등록번호: 628-86-01742</p>
          <p>주소: 경기도 광명시 광명로 880</p>
          <p>Email: <a href="mailto:moksorinw@no1kmedi.com" className="hover:text-sky-400 transition">moksorinw@no1kmedi.com</a></p>
          <p className="mt-4">&copy; 2025 MKM Lab. All rights reserved.</p>
        </div>
      </footer>


      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Orbitron:wght@700&display=swap" rel="stylesheet" />
    </div>
  );
}
