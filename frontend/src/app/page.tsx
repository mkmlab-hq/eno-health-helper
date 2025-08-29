"use client";

import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900">
      {/* 헤더 네비게이션 */}
      <header className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* 로고 및 브랜딩 */}
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center shadow-neon-cyan">
              <div className="w-6 h-6 text-white neon-glow">🩺</div>
            </div>
            <div>
              <h1 className="text-2xl font-orbitron font-bold text-white neon-text">
                엔오건강도우미
              </h1>
              <p className="text-sm text-gray-300 font-noto">AI 기반 건강 측정 도우미</p>
            </div>
          </div>
          
          {/* 메인 네비게이션 메뉴 */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/" className="text-gray-300 hover:text-eno-400 transition-colors font-noto">
              🏠 홈
            </Link>
            <Link href="/measure" className="text-gray-300 hover:text-eno-400 transition-colors font-noto">
              📱 건강 측정
            </Link>
            <Link href="/dashboard" className="text-gray-300 hover:text-eno-400 transition-colors font-noto">
              📊 대시보드
            </Link>
            <Link href="/music" className="text-gray-300 hover:text-eno-400 transition-colors font-noto">
              🎵 치유 음악
            </Link>
          </nav>
          
          {/* 사용자 액션 */}
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-300 hover:text-eno-400 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <button className="p-2 text-gray-300 hover:text-eno-400 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5z" />
              </svg>
            </button>
            <button className="w-10 h-10 bg-gradient-to-r from-eno-500 to-eno-400 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="relative z-10 px-6 pb-20">
        <div className="max-w-7xl mx-auto">
          {/* 히어로 섹션 */}
          <section className="text-center py-20">
            <h2 className="text-6xl md:text-7xl font-orbitron font-bold mb-6">
              <span className="neon-text">AI 기반 건강 측정</span>
              <br/>
              <span className="text-eno-400">초개인화 건강 통찰</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12 font-noto leading-relaxed">
              rPPG와 음성 분석을 통한 정확한 건강 측정으로<br/>
              <span className="text-eno-400 font-semibold">개인 맞춤형 건강 관리</span>를 경험하세요
            </p>
            
            {/* 메인 CTA 버튼 */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/measure"
                className="glass-button text-lg px-8 py-4 flex items-center space-x-3 group"
              >
                <span className="text-2xl">❤️</span>
                <span>건강 측정 시작하기</span>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              
              <Link
                href="/dashboard"
                className="glass-button bg-gradient-to-r from-eno-600 to-eno-500 text-lg px-8 py-4 flex items-center space-x-3 group"
              >
                <span className="text-2xl">📊</span>
                <span>건강 대시보드</span>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
            </div>
          </section>

          {/* 성과 통계 섹션 */}
          <div className="glass-card p-8 mb-16 max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl font-orbitron font-bold mb-4 neon-text">
                  🚀 성과 현황
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-yellow-400 text-xl">⭐</span>
                    <span className="text-gray-300">등급 및 성과: <span className="text-eno-400 font-semibold">Legendary</span></span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-green-400 text-xl">🎯</span>
                    <span className="text-gray-300">총 기록: <span className="text-eno-400 font-semibold">7개</span></span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-orange-400 text-xl">⚡</span>
                    <span className="text-gray-300">생성된: <span className="text-eno-400 font-semibold">12개</span></span>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <div className="relative w-32 h-32 mx-auto mb-4">
                  <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                    <path className="text-gray-700" fill="none" stroke="currentColor" strokeWidth="2" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                    <path className="text-eno-400" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="85, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-orbitron font-bold text-eno-400">85</span>
                  </div>
                </div>
                <p className="text-gray-300 font-noto">전체 완성도</p>
              </div>
            </div>
          </div>

          {/* 핵심 기능 소개 */}
          <section className="mb-20">
            <h3 className="text-3xl font-orbitron font-bold text-center mb-12 neon-text">
              🎯 핵심 기능 소개
            </h3>
            <div className="grid md:grid-cols-2 gap-8">
              {/* rPPG 건강 측정 */}
              <div className="glass-card p-8 cursor-pointer group">
                <div className="text-center mb-6">
                  <div className="w-20 h-20 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-neon-cyan transition-shadow">
                    <span className="text-4xl">❤️</span>
                  </div>
                  <h4 className="text-2xl font-orbitron font-bold mb-2 neon-text">rPPG 건강 측정</h4>
                  <p className="text-gray-300 font-noto">카메라 기반 비접촉 건강 분석</p>
                </div>
                <div className="space-y-3 mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-eno-400 rounded-full"></div>
                    <span className="text-gray-300 text-sm">rPPG 기반 정밀 건강 측정</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-eno-400 rounded-full"></div>
                    <span className="text-gray-300 text-sm">AI 생성 건강 기록과 음악</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-eno-400 rounded-full"></div>
                    <span className="text-gray-300 text-sm">실시간 건강 상태 모니터링</span>
                  </div>
                </div>
                <div className="text-center">
                  <Link href="/measure" className="text-eno-400 text-sm font-semibold group-hover:text-eno-300 transition-colors">
                    시작하기 →
                  </Link>
                </div>
              </div>

              {/* 음성 품질 분석 */}
              <div className="glass-card p-8 cursor-pointer group">
                <div className="text-center mb-6">
                  <div className="w-20 h-20 bg-gradient-to-r from-eno-600 to-eno-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:shadow-neon-cyan transition-shadow">
                    <span className="text-4xl">🎙️</span>
                  </div>
                  <h4 className="text-2xl font-orbitron font-bold mb-2 neon-text">음성 품질 분석</h4>
                  <p className="text-gray-300 font-noto">음성 기반 건강 상태 분석</p>
                </div>
                <div className="space-y-3 mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-eno-600 rounded-full"></div>
                    <span className="text-gray-300 text-sm">음성 상태와 음성 기록</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-eno-600 rounded-full"></div>
                    <span className="text-gray-300 text-sm">AI 기반 음성 분석 및 추천</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-eno-600 rounded-full"></div>
                    <span className="text-gray-300 text-sm">개인 맞춤형 건강 음악</span>
                  </div>
                </div>
                <div className="text-center">
                  <Link href="/measure" className="text-eno-600 text-sm font-semibold group-hover:text-eno-500 transition-colors">
                    시작하기 →
                  </Link>
                </div>
              </div>
            </div>
          </section>

          {/* AI 융합 분석 시스템 */}
          <section className="mb-20">
            <div className="glass-card p-8 text-center">
              <div className="w-24 h-24 bg-gradient-to-r from-eno-500 to-eno-400 rounded-3xl flex items-center justify-center mx-auto mb-6">
                <span className="text-5xl">🧠</span>
              </div>
              <h3 className="text-3xl font-orbitron font-bold mb-6 neon-text">AI 융합 분석 시스템</h3>
              <p className="text-lg text-gray-300 mb-8 max-w-4xl mx-auto font-noto leading-relaxed">
                <span className="text-eno-400 font-semibold">rPPG 건강 측정</span>과 <span className="text-eno-600 font-semibold">음성 품질 분석</span>을 통한<br/>
                AI의 융합 분석으로 개인 맞춤형 <span className="text-green-400 font-semibold">건강 통찰</span>을 제공합니다
              </p>
              <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                <div className="text-center">
                  <div className="w-16 h-16 bg-eno-400/20 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🎯</span>
                  </div>
                  <h4 className="font-orbitron font-semibold mb-2">정밀 분석</h4>
                  <p className="text-sm text-gray-400">rPPG + 음성 데이터 융합</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-eno-600/20 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">✨</span>
                  </div>
                  <h4 className="font-orbitron font-semibold mb-2">개인 맞춤</h4>
                  <p className="text-sm text-gray-400">AI 기반 개인별 건강 분석</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-green-400/20 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h4 className="font-orbitron font-semibold mb-2">지속적 추천</h4>
                  <p className="text-sm text-gray-400">건강 결과 기반 맞춤형 활동</p>
                </div>
              </div>
            </div>
          </section>

          {/* 향후 기능 */}
          <section className="mb-20">
            <h3 className="text-3xl font-orbitron font-bold text-center mb-12 text-eno-400">
              🚀 향후 기능
            </h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* AI 상담사 */}
              <div className="glass-card p-6 cursor-pointer group">
                <div className="w-16 h-16 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center mb-4 group-hover:shadow-neon-cyan transition-shadow">
                  <span className="text-3xl">💬</span>
                </div>
                <h4 className="text-xl font-orbitron font-semibold mb-3">AI 상담사</h4>
                <p className="text-gray-400 text-sm mb-4">건강 데이터 기반 맞춤형 상담으로 개인별 건강 관리 방안 제시</p>
                <span className="text-eno-400 text-sm font-semibold group-hover:text-eno-300 transition-colors">준비 중 →</span>
              </div>

              {/* AI 음악 추천 */}
              <div className="glass-card p-6 cursor-pointer group">
                <div className="w-16 h-16 bg-gradient-to-r from-eno-600 to-eno-500 rounded-2xl flex items-center justify-center mb-4 group-hover:shadow-neon-cyan transition-shadow">
                  <span className="text-3xl">🎵</span>
                </div>
                <h4 className="text-xl font-orbitron font-semibold mb-3">AI 음악 추천</h4>
                <p className="text-gray-400 text-sm mb-4">현재 상태에 맞는 AI 음악 생성으로 치유와 휴식을 위한 맞춤형 음악</p>
                <span className="text-eno-600 text-sm font-semibold group-hover:text-eno-500 transition-colors">준비 중 →</span>
              </div>

              {/* 건강 게임 */}
              <div className="glass-card p-6 cursor-pointer group">
                <div className="w-16 h-16 bg-green-400/20 rounded-2xl flex items-center justify-center mb-4 group-hover:shadow-neon-cyan transition-shadow">
                  <span className="text-3xl">🎮</span>
                </div>
                <h4 className="text-xl font-orbitron font-semibold mb-3">건강 게임</h4>
                <p className="text-gray-400 text-sm mb-4">측정 결과를 활용한 맞춤형 게임으로 건강한 활동을 재미있게</p>
                <span className="text-green-400 text-sm font-semibold group-hover:text-green-300 transition-colors">준비 중 →</span>
              </div>

              {/* NFT 건강 프로젝트 */}
              <div className="glass-card p-6 cursor-pointer group">
                <div className="w-16 h-16 bg-gradient-to-r from-eno-600 to-eno-500 rounded-2xl flex items-center justify-center mb-4 group-hover:shadow-neon-cyan transition-shadow">
                  <span className="text-3xl">🎨</span>
                </div>
                <h4 className="text-xl font-orbitron font-semibold mb-3">NFT 건강 프로젝트</h4>
                <p className="text-gray-400 text-sm mb-4">건강 데이터를 기반으로 한 개인별 NFT 프로젝트 생성</p>
                <span className="text-eno-600 text-sm font-semibold group-hover:text-eno-500 transition-colors">준비 중 →</span>
              </div>

              {/* 건강 대시보드 */}
              <div className="glass-card p-6 cursor-pointer group">
                <div className="w-16 h-16 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center mb-4 group-hover:shadow-neon-cyan transition-shadow">
                  <span className="text-3xl">📊</span>
                </div>
                <h4 className="text-xl font-orbitron font-semibold mb-3">건강 대시보드</h4>
                <p className="text-gray-400 text-sm mb-4">개인별 건강 변화 추이를 시각화하여 건강 관리의 방향성 제시</p>
                <span className="text-eno-400 text-sm font-semibold group-hover:text-eno-300 transition-colors">준비 중 →</span>
              </div>

              {/* 건강 커뮤니티 */}
              <div className="glass-card p-6 cursor-pointer group">
                <div className="w-16 h-16 bg-green-400/20 rounded-2xl flex items-center justify-center mb-4 group-hover:shadow-neon-cyan transition-shadow">
                  <span className="text-3xl">👥</span>
                </div>
                <h4 className="text-xl font-orbitron font-semibold mb-3">건강 커뮤니티</h4>
                <p className="text-gray-400 text-sm mb-4">공통된 건강 관심사를 가진 사용자들과 상호 지원 및 정보 공유</p>
                <span className="text-green-400 text-sm font-semibold group-hover:text-green-300 transition-colors">준비 중 →</span>
              </div>
            </div>
          </section>

          {/* 시작 안내 */}
          <section className="text-center">
            <div className="glass-card p-12 max-w-4xl mx-auto">
              <h3 className="text-4xl font-orbitron font-bold mb-6 neon-text">
                🚀 지금 시작하세요!
              </h3>
              <p className="text-xl text-gray-300 mb-8 font-noto">
                AI가 분석하는 개인 맞춤형 건강 관리의 시작<br/>
                개인별 건강 통찰을 위한 건강 일기를 만들어보세요
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/measure"
                  className="glass-button text-lg px-8 py-4 flex items-center justify-center space-x-3 group"
                >
                  <span className="text-2xl">❤️</span>
                  <span>건강 측정 시작</span>
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
                <Link
                  href="/dashboard"
                  className="glass-button bg-gradient-to-r from-eno-600 to-eno-500 text-lg px-8 py-4 flex items-center justify-center space-x-3 group"
                >
                  <span className="text-2xl">🧠</span>
                  <span>AI 분석 시작</span>
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* 푸터 */}
      <footer className="relative z-10 mt-20 py-12 border-t border-gray-800/50">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-gradient-to-r from-eno-500 to-eno-400 rounded-lg flex items-center justify-center">
              <span className="text-white text-lg">🩺</span>
            </div>
            <span className="text-xl font-orbitron font-bold neon-text">엔오건강도우미</span>
          </div>
          <p className="text-gray-400 mb-6 font-noto">
            AI 기반 건강 측정과 분석을 통한 개인 맞춤형 건강 관리 서비스
          </p>
          <div className="flex justify-center space-x-6 text-sm text-gray-500">
            <span>© 2025 MKM Lab</span>
            <span>•</span>
            <span>개인정보처리방침</span>
            <span>•</span>
            <span>이용약관</span>
            <span>•</span>
            <span>고객지원</span>
          </div>
        </div>
      </footer>
    </div>
  );
} 