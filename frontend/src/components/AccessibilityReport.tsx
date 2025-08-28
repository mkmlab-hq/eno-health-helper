'use client';

import React, { useState, useEffect } from 'react';
import AccessibilityTester, { AccessibilityReport, AccessibilityIssue } from '@/lib/accessibilityTester';

interface AccessibilityReportProps {
  onClose: () => void;
}

const AccessibilityReportComponent: React.FC<AccessibilityReportProps> = ({ onClose }) => {
  const [report, setReport] = useState<AccessibilityReport | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<AccessibilityIssue | null>(null);

  const runTest = async () => {
    setIsRunning(true);
    try {
      const tester = AccessibilityTester.getInstance();
      const result = await tester.runAccessibilityTest();
      setReport(result);
    } catch (error) {
      console.error('접근성 테스트 실행 실패:', error);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    runTest();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreStatus = (score: number) => {
    if (score >= 90) return '✅ 우수';
    if (score >= 70) return '⚠️ 양호';
    return '❌ 개선 필요';
  };

  const getImpactColor = (impact: AccessibilityIssue['impact']) => {
    switch (impact) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'serious': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'minor': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getImpactIcon = (impact: AccessibilityIssue['impact']) => {
    switch (impact) {
      case 'critical': return '🚨';
      case 'serious': return '⚠️';
      case 'moderate': return '⚡';
      case 'minor': return 'ℹ️';
      default: return '❓';
    }
  };

  if (!report) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">
              {isRunning ? '접근성 테스트를 실행하는 중...' : '접근성 테스트를 시작합니다...'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-6xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">♿ 접근성 테스트 결과</h2>
          <div className="flex space-x-3">
            <button
              onClick={runTest}
              disabled={isRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
            >
              {isRunning ? '테스트 중...' : '🔄 재테스트'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              닫기
            </button>
          </div>
        </div>

        {/* 접근성 점수 요약 */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="text-sm font-medium text-blue-800">전체 점수</h3>
            <p className={`text-3xl font-bold ${getScoreColor(report.score)}`}>
              {report.score}/100
            </p>
            <p className="text-sm text-blue-600">
              {getScoreStatus(report.score)}
            </p>
          </div>

          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <h3 className="text-sm font-medium text-red-800">심각한 문제</h3>
            <p className="text-2xl font-bold text-red-600">
              {report.criticalIssues}
            </p>
            <p className="text-sm text-red-600">개선 필요</p>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <h3 className="text-sm font-medium text-orange-800">중요한 문제</h3>
            <p className="text-2xl font-bold text-orange-600">
              {report.seriousIssues}
            </p>
            <p className="text-sm text-orange-600">우선 해결</p>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <h3 className="text-sm font-medium text-yellow-800">보통 문제</h3>
            <p className="text-2xl font-bold text-yellow-600">
              {report.moderateIssues}
            </p>
            <p className="text-sm text-yellow-600">점진적 개선</p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="text-sm font-medium text-blue-800">경미한 문제</h3>
            <p className="text-2xl font-bold text-blue-600">
              {report.minorIssues}
            </p>
            <p className="text-sm text-blue-600">선택적 개선</p>
          </div>
        </div>

        {/* 문제 목록 */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            발견된 접근성 문제 ({report.totalIssues}개)
          </h3>
          
          {report.issues.length === 0 ? (
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <p className="text-green-800 text-center font-medium">
                🎉 축하합니다! 접근성 문제가 발견되지 않았습니다.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {report.issues.map((issue) => (
                <div
                  key={issue.id}
                  className={`p-4 rounded-lg border cursor-pointer transition-colors hover:bg-gray-50 ${
                    selectedIssue?.id === issue.id ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => setSelectedIssue(issue)}
                >
                  <div className="flex items-start space-x-3">
                    <span className="text-xl">{getImpactIcon(issue.impact)}</span>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getImpactColor(issue.impact)}`}>
                          {issue.impact.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          {issue.type === 'error' ? '❌ 오류' : issue.type === 'warning' ? '⚠️ 경고' : 'ℹ️ 정보'}
                        </span>
                      </div>
                      <p className="font-medium text-gray-900 mb-1">{issue.message}</p>
                      {issue.selector && (
                        <p className="text-sm text-gray-600 font-mono bg-gray-100 px-2 py-1 rounded">
                          {issue.selector}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 선택된 문제 상세 정보 */}
        {selectedIssue && (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-3">
              문제 상세 정보
            </h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-700">문제 설명</h5>
                <p className="text-gray-600">{selectedIssue.message}</p>
              </div>
              <div>
                <h5 className="font-medium text-gray-700">해결 방법</h5>
                <p className="text-gray-600">{selectedIssue.help}</p>
              </div>
              {selectedIssue.helpUrl && (
                <div>
                  <h5 className="font-medium text-gray-700">참고 자료</h5>
                  <a
                    href={selectedIssue.helpUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    {selectedIssue.helpUrl}
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 테스트 정보 */}
        <div className="mt-6 text-sm text-gray-500 text-center">
          <p>테스트 실행 시간: {report.timestamp.toLocaleString()}</p>
          <p>총 {report.totalIssues}개의 접근성 문제가 발견되었습니다.</p>
        </div>
      </div>
    </div>
  );
};

export default AccessibilityReportComponent; 