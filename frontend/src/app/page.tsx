'use client';

import { useState, useEffect } from 'react';
import { QrCode, Camera, Mic, Activity, Heart, Volume2, TrendingUp } from 'lucide-react';
import { checkHealth, getMeasurementHistory, HealthStatus, MeasurementHistory } from './api/health';

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [measurementHistory, setMeasurementHistory] = useState<MeasurementHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 컴포넌트 마운트 시 API 상태 확인
  useEffect(() => {
    checkApiHealth();
    loadMeasurementHistory();
  }, []);

  // API 헬스체크
  const checkApiHealth = async () => {
    try {
      setLoading(true);
      const status = await checkHealth();
      setHealthStatus(status);
      setError(null);
    } catch (err) {
      setError('백엔드 API 연결 실패');
      console.error('API Health check failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // 측정 기록 로드
  const loadMeasurementHistory = async () => {
    try {
      const history = await getMeasurementHistory();
      setMeasurementHistory(history);
    } catch (err) {
      console.error('Failed to load measurement history:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                <span className="text-indigo-600">엔오</span>건강도우미
                <span className="text-sm text-gray-500 ml-2">by MKM Lab</span>
              </h1>
            </div>
            
            {/* API 상태 표시 */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${healthStatus ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {loading ? '연결 중...' : healthStatus ? 'API 연결됨' : 'API 연결 안됨'}
                </span>
              </div>
              <button
                onClick={checkApiHealth}
                disabled={loading}
                className="px-3 py-1 text-sm bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 disabled:opacity-50"
              >
                새로고침
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            <span className="text-blue-600">엔오 건강 도우미</span>와 함께하는 건강한 변화
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">
            MKM Lab의 첨단 AI 기술로 구현된 RPPG(원격 광전용맥파)와 음성 분석을 통해 
            심박수, 스트레스 지수, 음성 특성을 과학적으로 측정하고 건강 상태를 종합적으로 분석합니다.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-2xl mx-auto">
            <p className="text-blue-800 font-medium">
              💡 <strong>MKM Lab 기술력:</strong> 의료기기 수준의 신호 처리 알고리즘, 
              실시간 생체신호 분석, AI 기반 건강 상태 평가
            </p>
          </div>
        </div>

        {/* API 상태 정보 */}
        {healthStatus && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">백엔드 API 상태</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{healthStatus.status}</div>
                <div className="text-sm text-gray-600">상태</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{healthStatus.service}</div>
                <div className="text-sm text-gray-600">서비스명</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {new Date(healthStatus.timestamp).toLocaleString('ko-KR')}
                </div>
                <div className="text-sm text-gray-600">마지막 업데이트</div>
              </div>
            </div>
          </div>
        )}

        {/* 측정 기록 정보 */}
        {measurementHistory && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">측정 기록 현황</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">{measurementHistory.total}</div>
                <div className="text-sm text-gray-600">총 측정 수</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{measurementHistory.limit}</div>
                <div className="text-sm text-gray-600">페이지당 표시</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{measurementHistory.offset}</div>
                <div className="text-sm text-gray-600">현재 오프셋</div>
              </div>
            </div>
          </div>
        )}

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {/* QR 스캔 */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer" 
               onClick={() => window.location.href = '/health-measurement-v3.html'}>
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
              <QrCode className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">건강 측정 시작</h3>
            <p className="text-gray-600">
              클릭하여 바로 건강 측정을 시작하세요. RPPG 및 음성 분석을 통해 
              종합적인 건강 상태를 확인할 수 있습니다.
            </p>
            <div className="mt-3 text-blue-600 text-sm font-medium">
              → 지금 시작하기
            </div>
          </div>

          {/* RPPG 측정 */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
              <Camera className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">RPPG 측정</h3>
            <p className="text-gray-600">
              MKM Lab의 의료기기 수준 알고리즘으로 카메라를 통해 
              심박수, HRV, 스트레스 지수를 정확하게 측정합니다.
            </p>
          </div>

          {/* 음성 분석 */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
              <Mic className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">음성 분석</h3>
            <p className="text-gray-600">
              AI 기반 음성 특성 분석으로 F0, 지터, 시머, HNR을 정밀하게 측정하여 
              건강 상태를 종합적으로 평가합니다.
            </p>
          </div>

          {/* 건강 지표 */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-lg mb-4">
              <Heart className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">건강 지표</h3>
            <p className="text-gray-600">
              MKM Lab의 AI 알고리즘으로 심박수, HRV, 스트레스 지수 등 
              종합적인 건강 지표를 실시간으로 제공합니다.
            </p>
          </div>

          {/* 음성 특성 */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-lg mb-4">
              <Volume2 className="h-6 w-6 text-yellow-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">음성 특성</h3>
            <p className="text-gray-600">
              MKM Lab의 고급 신호 처리 기술로 F0, 지터, 시머, HNR 등 
              음성의 과학적 특성을 정밀하게 분석합니다.
            </p>
          </div>

          {/* 트렌드 분석 */}
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-indigo-100 rounded-lg mb-4">
              <TrendingUp className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">트렌드 분석</h3>
            <p className="text-gray-600">
              MKM Lab의 머신러닝 기술로 시간에 따른 건강 지표 변화를 
              지능적으로 추적하고 예측 분석을 제공합니다.
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-800 mb-3">⚠️ 중요 안내사항</h3>
          <div className="space-y-2 text-sm text-yellow-700">
            <p>• 이 애플리케이션은 의학적 진단을 대체하지 않습니다.</p>
            <p>• 측정 결과는 참고용이며, 건강상 문제가 있을 경우 전문의와 상담하세요.</p>
            <p>• 개인정보는 서버에 저장되지 않으며, 측정 완료 후 즉시 삭제됩니다.</p>
            <p>• 의료기기 인증을 받지 않은 소프트웨어입니다.</p>
          </div>
        </div>
      </main>
    </div>
  );
} 