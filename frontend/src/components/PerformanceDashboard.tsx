'use client';

import React, { useState, useEffect } from 'react';
import PerformanceMonitor, { PerformanceReport } from '@/lib/performanceMonitor';

interface PerformanceDashboardProps {
  onClose: () => void;
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ onClose }) => {
  const [performanceReport, setPerformanceReport] = useState<PerformanceReport | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = () => {
    setIsRefreshing(true);
    const monitor = PerformanceMonitor.getInstance();
    const report = monitor.getPerformanceReport();
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
            <p className={`text-2xl font-bold ${getPerformanceColor(performanceReport.pageLoadTime, 1000)}`}>
              {performanceReport.pageLoadTime}ms
            </p>
            <p className="text-sm text-blue-600">
              {getPerformanceStatus(performanceReport.pageLoadTime, 1000)}
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <h3 className="text-sm font-medium text-green-800">평균 API 응답 시간</h3>
            <p className={`text-2xl font-bold ${getPerformanceColor(performanceReport.averageApiResponseTime, 500)}`}>
              {performanceReport.averageApiResponseTime}ms
            </p>
            <p className="text-sm text-green-600">
              {getPerformanceStatus(performanceReport.averageApiResponseTime, 500)}
            </p>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <h3 className="text-sm font-medium text-purple-800">평균 사용자 상호작용</h3>
            <p className={`text-2xl font-bold ${getPerformanceColor(performanceReport.averageUserInteractionTime, 100)}`}>
              {performanceReport.averageUserInteractionTime}ms
            </p>
            <p className="text-sm text-purple-600">
              {getPerformanceStatus(performanceReport.averageUserInteractionTime, 100)}
            </p>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <h3 className="text-sm font-medium text-orange-800">총 메트릭 수</h3>
            <p className="text-2xl font-bold text-orange-600">
              {performanceReport.totalMetrics}
            </p>
            <p className="text-sm text-orange-600">수집된 데이터</p>
          </div>
        </div>

        {/* 상세 성능 분석 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* API 응답 시간 분포 */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📡 API 응답 시간 분포</h3>
            <div className="space-y-2">
              {performanceReport.apiResponseTimes.length > 0 ? (
                performanceReport.apiResponseTimes.slice(-10).map((time, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">API 호출 {index + 1}:</span>
                    <span className={`font-medium ${getPerformanceColor(time, 500)}`}>
                      {time}ms
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-sm">아직 API 호출 데이터가 없습니다.</p>
              )}
            </div>
          </div>

          {/* 사용자 상호작용 시간 분포 */}
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">👆 사용자 상호작용 시간 분포</h3>
            <div className="space-y-2">
              {performanceReport.userInteractionTimes.length > 0 ? (
                performanceReport.userInteractionTimes.slice(-10).map((time, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">상호작용 {index + 1}:</span>
                    <span className={`font-medium ${getPerformanceColor(time, 100)}`}>
                      {time}ms
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-sm">아직 사용자 상호작용 데이터가 없습니다.</p>
              )}
            </div>
          </div>
        </div>

        {/* 성능 권장사항 */}
        <div className="mt-6 bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">💡 성능 최적화 권장사항</h3>
          <ul className="text-sm text-yellow-700 space-y-1">
            {performanceReport.pageLoadTime > 1000 && (
              <li>• 페이지 로드 시간이 1초를 초과합니다. 이미지 최적화를 고려해보세요.</li>
            )}
            {performanceReport.averageApiResponseTime > 500 && (
              <li>• API 응답 시간이 500ms를 초과합니다. 백엔드 최적화가 필요합니다.</li>
            )}
            {performanceReport.averageUserInteractionTime > 100 && (
              <li>• 사용자 상호작용 응답 시간이 100ms를 초과합니다. UI 최적화를 고려해보세요.</li>
            )}
            {performanceReport.pageLoadTime <= 1000 && performanceReport.averageApiResponseTime <= 500 && (
              <li>• 현재 성능이 양호합니다! 계속 모니터링하세요.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard; 