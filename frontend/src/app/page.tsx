'use client';

import { useState } from 'react';
import { QRCode, Camera, Mic, TrendingUp, Shield, Heart } from 'lucide-react';

export default function HomePage() {
  const [productId, setProductId] = useState<string | null>(null);

  const handleQRScan = (scannedProductId: string) => {
    setProductId(scannedProductId);
  };

  const startMeasurement = () => {
    // 측정 페이지로 이동
    window.location.href = '/measurement';
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-eno-700">🏥 엔오건강도우미</h1>
              <p className="text-sm text-gray-600">ENO Health Helper</p>
            </div>
            <div className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
              의료 진단 아님 · 참고용
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            엔오플렉스와 함께하는<br />
            <span className="text-eno-600">건강한 변화</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            복용 전후 생체신호 변화를 측정하여 개인화된 웰니스 가이드를 제공합니다.
            QR 코드를 스캔하고 건강 측정을 시작해보세요.
          </p>
        </div>

        {/* QR Scanner Section */}
        <div className="card max-w-md mx-auto mb-12">
          <div className="text-center mb-6">
            <div className="w-20 h-20 bg-eno-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <QRCode className="w-10 h-10 text-eno-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              QR 코드 스캔
            </h3>
            <p className="text-gray-600 text-sm">
              엔오플렉스 포장지의 QR 코드를 스캔하세요
            </p>
          </div>
          
          {!productId ? (
            <button className="btn-primary w-full">
              <QRCode className="w-5 h-5 mr-2 inline" />
              QR 스캔 시작
            </button>
          ) : (
            <div className="text-center">
              <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg mb-4">
                ✅ 제품 인식 완료
              </div>
              <button onClick={startMeasurement} className="btn-primary w-full">
                건강 측정 시작
              </button>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="card text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Camera className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">RPPG 분석</h3>
            <p className="text-gray-600 text-sm">
              얼굴 혈류 변화를 실시간으로 분석하여 맥박과 심박변이도를 측정합니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mic className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">음성 분석</h3>
            <p className="text-gray-600 text-sm">
              음성의 주파수, 지터, 쉬머, 조화대잡음비를 분석하여 음성 특성을 평가합니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">변화 추적</h3>
            <p className="text-gray-600 text-sm">
              복용 전후 변화를 시각화하고 개인화된 웰니스 가이드를 제공합니다.
            </p>
          </div>
        </div>

        {/* Info Section */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">측정 준비사항</h3>
          <div className="grid md:grid-cols-3 gap-6 text-sm">
            <div>
              <h4 className="font-medium text-eno-600 mb-2 flex items-center">
                <Shield className="w-4 h-4 mr-2" />
                개인정보 보호
              </h4>
              <ul className="text-gray-600 space-y-1">
                <li>• 영상/음성 로컬 처리</li>
                <li>• 원본 데이터 저장 안함</li>
                <li>• 분석 결과만 제공</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-eno-600 mb-2 flex items-center">
                <Camera className="w-4 h-4 mr-2" />
                환경 조건
              </h4>
              <ul className="text-gray-600 space-y-1">
                <li>• 충분한 조명 확보</li>
                <li>• 주변 소음 최소화</li>
                <li>• 안정된 자세 유지</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-eno-600 mb-2 flex items-center">
                <Heart className="w-4 h-4 mr-2" />
                측정 시간
              </h4>
              <ul className="text-gray-600 space-y-1">
                <li>• 총 소요시간: 30-100초</li>
                <li>• RPPG: 20-60초</li>
                <li>• 음성: 10-40초</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>© 2024 MKM Lab. All rights reserved.</p>
            <p className="mt-1">엔오건강도우미는 의료 진단을 대체하지 않습니다.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 