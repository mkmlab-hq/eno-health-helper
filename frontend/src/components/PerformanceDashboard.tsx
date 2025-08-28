'use client';

import React, { useState, useEffect } from 'react';
import { performanceMonitor, PerformanceReport } from '@/lib/performanceMonitor';

interface PerformanceDashboardProps {
  onClose: () => void;
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ onClose }) => {
  const [performanceReport, setPerformanceReport] = useState<PerformanceReport | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = () => {
    setIsRefreshing(true);
    performanceMonitor.startMonitoring();
    const report = performanceMonitor.generateReport();
    setPerformanceReport(report);
    setIsRefreshing(false);
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 5000); // 5초마다 갱신
    return () => clearInterval(interval);
  }, []);

  if (!performanceReport) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">성능 데이터를 수집하는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  const getPerformanceColor = (value: number, threshold: number) => {
    if (value <= threshold) return 'text-green-600';
    if (value <= threshold * 1.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceStatus = (value: number, threshold: number) => {
    if (value <= threshold) return '✅ 양호';
    if (value <= threshold * 1.5) return '⚠️ 주의';
    return '❌ 개선 필요';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-6xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">📊 성능 모니터링 대시보드</h2>
          <div className="flex space-x-3">
            <button
              onClick={refreshData}
              disabled={isRefreshing}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
            >
              {isRefreshing ? '갱신 중...' : '🔄 갱신'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              닫기
            </button>
          </div>
        </div>

        {/* 전체 성능 요약 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="text-sm font-medium text-blue-800">페이지 로드 시간</h3>
            <p className={`text-2xl font-bold ${getPerformanceColor(performanceReport.metrics.pageLoadTime, 1000)}`}>
              {performanceReport.metrics.pageLoadTime}ms
            </p>
            <p className="text-sm text-blue-600">
              {getPerformanceStatus(performanceReport.metrics.pageLoadTime, 1000)}
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <h3 className="text-sm font-medium text-green-800">First Contentful Paint</h3>
            <p className={`text-2xl font-bold ${getPerformanceColor(performanceReport.metrics.firstContentfulPaint, 1800)}`}>
              {performanceReport.metrics.firstContentfulPaint}ms
            </p>
            <p className="text-sm text-green-600">
              {getPerformanceStatus(performanceReport.metrics.firstContentfulPaint, 1800)}
            </p>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <h3 className="text-sm font-medium text-purple-800">Largest Contentful Paint</h3>
            <p className={`text-2xl font-bold ${getPerformanceColor(performanceReport.metrics.largestContentfulPaint, 2500)}`}>
              {performanceReport.metrics.largestContentfulPaint}ms
            </p>
            <p className="text-sm text-purple-600">
              {getPerformanceStatus(performanceReport.metrics.largestContentfulPaint, 2500)}
            </p>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <h3 className="text-sm font-medium text-orange-800">네트워크 요청</h3>
            <p className="text-2xl font-bold text-orange-600">
              {performanceReport.metrics.networkRequests}
            </p>
            <p className="text-sm text-orange-600">수집된 데이터</p>
          </div>
        </div>

        {/* 상세 성능 분석 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 성능 메트릭 상세 */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 성능 메트릭 상세</h3>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-600">DOM 로드 완료:</span>
                <span className="font-medium">{performanceReport.metrics.domContentLoaded}ms</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">First Input Delay:</span>
                <span className="font-medium">{performanceReport.metrics.firstInputDelay}ms</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="text-sm text-gray-600">Layout Shift:</span>
                <span className="font-medium">{performanceReport.metrics.cumulativeLayoutShift.toFixed(3)}</span>
              </div>
            </div>
          </div>

          {/* 권장사항 */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 성능 권장사항</h3>
            <div className="space-y-2">
              {performanceReport.recommendations.length > 0 ? (
                performanceReport.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                    <span className="text-sm text-gray-600">{rec}</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-sm">현재 성능이 양호합니다!</p>
              )}
            </div>
          </div>
        </div>

        {/* 성능 등급 */}
        <div className="mt-6 bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">📈 성능 등급</h3>
          <div className="text-center">
            <div className={`text-4xl font-bold mb-2 ${
              performanceReport.grade === 'A' ? 'text-green-600' :
              performanceReport.grade === 'B' ? 'text-blue-600' :
              performanceReport.grade === 'C' ? 'text-yellow-600' :
              performanceReport.grade === 'D' ? 'text-orange-600' : 'text-red-600'
            }`}>
              {performanceReport.grade}
            </div>
            <p className="text-sm text-blue-600">
              총점: {performanceReport.score}/100
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard; 