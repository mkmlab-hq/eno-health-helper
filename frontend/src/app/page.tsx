"use client";

import { useState, useEffect } from 'react';
import { QrCode, Camera, Mic, TrendingUp, Shield, Heart, Brain, Music, Palette } from 'lucide-react';
import dynamic from 'next/dynamic';
const MotionDiv = dynamic(() => import('@/components/utils/MotionDiv').then(m => m.MotionDiv), { ssr: false });
import { apiClient } from '@/lib/api';

export default function Home() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [productId, setProductId] = useState(null);

  useEffect(() => {
    const testAPI = async () => {
      try {
        const isConnected = await apiClient.testConnection();
        if (isConnected) {
          console.log('✅ 백엔드 API 연결 성공!');
          setIsConnected(true);
        } else {
          console.log('❌ 백엔드 API 연결 실패');
          setIsConnected(false);
        }
      } catch (error) {
        console.error('API 연결 테스트 오류:', error);
        setIsConnected(false);
      }
    };
    testAPI();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* 사이버펑크 배경 패턴 */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,191,255,0.1),transparent_50%)]"></div>
      
      {/* 네비게이션 */}
      <nav className="fixed top-0 w-full bg-black/20 backdrop-blur-md border-b border-blue-500/30 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                    MKM LAB
                  </h1>
                  <p className="text-xs text-blue-300">AI DIGITAL ECOSYSTEM</p>
                </div>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#technology" className="text-gray-300 hover:text-blue-400 transition-colors font-medium">
                7대 기술
              </a>
              <a href="#services" className="text-gray-300 hover:text-blue-400 transition-colors font-medium">
                서비스
              </a>
              <a href="#vision" className="text-gray-300 hover:text-blue-400 transition-colors font-medium">
                비전
              </a>
              <a href="/landing" className="text-gray-300 hover:text-blue-400 transition-colors font-medium">
                회사 소개
              </a>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                isConnected 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-red-500/20 text-red-400 border border-red-500/30'
              }`}>
                {isConnected ? '🟢 API 연결됨' : '🔴 API 연결 안됨'}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8 pt-24">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            엔오플렉스와 함께하는<br />
            <span className="text-blue-400">건강한 변화</span>
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            복용 전후 생체신호 변화를 측정하여 개인화된 웰니스 가이드를 제공합니다.
            QR 코드를 스캔하고 건강 측정을 시작해보세요.
          </p>
        </div>

        {/* QR Scanner Section */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 max-w-md mx-auto mb-12">
          <div className="text-center mb-6">
            <div className="w-20 h-20 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <QrCode className="w-10 h-10 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              QR 코드 스캔
            </h3>
            <p className="text-gray-300 text-sm">
              엔오플렉스 포장지의 QR 코드를 스캔하세요
            </p>
          </div>
          
          {!productId ? (
            <button className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 transform hover:scale-105">
              <QrCode className="w-5 h-5 mr-2 inline" />
              QR 스캔 시작
            </button>
          ) : (
            <div className="text-center">
              <div className="bg-green-500/20 text-green-400 px-4 py-2 rounded-lg mb-4 border border-green-500/30">
                ✅ 제품 인식 완료
              </div>
            </div>
          )}
        </div>

        {/* 핵심 기능 소개 */}
        <MotionDiv className="mb-16">
          <h2 className="text-2xl font-semibold text-white mb-8">4대 핵심 기능</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {/* rPPG 건강 측정 */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-blue-500/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mb-4">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">rPPG 건강 측정</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                카메라를 통해 얼굴의 미세한 혈류 변화를 분석하여, 심박수, 심박변이도, 스트레스 수준을 비접촉으로 정밀하게 측정합니다.
              </p>
              <div className="mt-3 text-xs text-blue-400 font-medium">비접촉 정밀 측정</div>
            </div>

            {/* 음성 품질 분석 */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-blue-500/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mb-4">
                <Music className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">음성 품질 분석</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                목소리의 미세한 떨림(Jitter, Shimmer) 등 음성 지표를 통해 건강 상태 및 스트레스 수준을 분석합니다.
              </p>
              <div className="mt-3 text-xs text-green-400 font-medium">다차원적 건강 분석</div>
            </div>

            {/* AI 기반 '기질' 분석 */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-blue-500/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mb-4">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">AI 기반 '기질' 분석</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                rPPG와 음성 데이터를 융합하여, 당신의 현재 상태를 4가지 주요 '디지털 기질'로 분석하고, 사상의학 기반의 맞춤형 건강 조언을 제공합니다.
              </p>
              <div className="mt-3 text-xs text-purple-400 font-medium">의미 있는 해석 제공</div>
            </div>

            {/* AI 생성 '감정의 사운드트랙' */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-blue-500/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-4">
                <Palette className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">AI 생성 '감정의 사운드트랙'</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                분석된 당신의 현재 감정과 기질에 맞춰, 세상에 단 하나뿐인 '감정의 사운드트랙'을 AI가 실시간으로 작곡해 드립니다. 당신의 건강은 이제 예술이 됩니다.
              </p>
              <div className="mt-3 text-xs text-orange-400 font-medium">데이터-예술 융합</div>
            </div>
          </div>
        </MotionDiv>

        {/* 사용 방법 */}
        <MotionDiv className="mb-16">
          <h2 className="text-2xl font-semibold text-white mb-8">사용 방법</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">QR코드 스캔</h3>
              <p className="text-gray-400 text-sm">엔오플렉스 포장지의 QR코드를 스캔하세요</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">무료 측정</h3>
              <p className="text-gray-400 text-sm">rPPG와 음성을 동시에 측정하세요</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">결과 확인</h3>
              <p className="text-gray-400 text-sm">AI 분석 결과를 즉시 확인하세요</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-white">4</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">회원가입</h3>
              <p className="text-gray-400 text-sm">결과 저장을 위해 간단한 회원가입을 진행하세요</p>
            </div>
          </div>
        </MotionDiv>

        {/* CTA */}
        <MotionDiv className="text-center">
          <h2 className="text-2xl font-semibold text-white mb-6">지금 바로 시작하세요</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            AI 기술로 정확하고 편리한 건강 측정을 경험하고, 당신만의 감정의 사운드트랙을 만들어보세요
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <a href="/fusion-analysis" className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-105">
              <Heart className="w-5 h-5 mr-2" />
              무료로 시작하기
            </a>
            {currentUser && (
              <a href="/dashboard" className="inline-flex items-center px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl border border-white/20 transition-all duration-300">
                <TrendingUp className="w-5 h-5 mr-2" />
                나의 건강 기록
              </a>
            )}
          </div>
        </MotionDiv>
      </main>
    </div>
  );
} 