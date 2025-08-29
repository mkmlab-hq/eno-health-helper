'use client';

import React, { useState, useEffect } from 'react';

// 임시 인터페이스 정의 (실제 파일이 없어서)
interface AccessibilityIssue {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  element?: string;
  impact: 'critical' | 'serious' | 'moderate' | 'minor';
  recommendation: string;
}

interface AccessibilityReport {
  score: number;
  totalIssues: number;
  criticalIssues: number;
  seriousIssues: number;
  moderateIssues: number;
  minorIssues: number;
  issues: AccessibilityIssue[];
  timestamp: string;
}

// 임시 접근성 테스터 (실제 파일이 없어서)
const accessibilityTester = {
  async runAccessibilityTest(): Promise<AccessibilityReport> {
    // 임시 데이터 반환
    return {
      score: 85,
      totalIssues: 5,
      criticalIssues: 1,
      seriousIssues: 2,
      moderateIssues: 1,
      minorIssues: 1,
      issues: [
        {
          id: '1',
          type: 'error',
          message: '색상 대비 부족',
          element: '버튼',
          impact: 'critical',
          recommendation: '색상 대비를 4.5:1 이상으로 개선하세요'
        }
      ],
      timestamp: new Date().toISOString()
    };
  }
};

// 영향도 설명 함수
const getImpactDescription = (impact: string): string => {
  switch (impact) {
    case 'critical': return '심각한 문제';
    case 'serious': return '중요한 문제';
    case 'moderate': return '보통 문제';
    case 'minor': return '경미한 문제';
    default: return '알 수 없음';
  }
};

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
      const result = await accessibilityTester.runAccessibilityTest();
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

  const getTypeColor = (type: AccessibilityIssue['type']) => {
    switch (type) {
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: AccessibilityIssue['type']) => {
    switch (type) {
      case 'error': return '🚨';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
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
            <h3 className="text-sm font-medium text-red-800">에러</h3>
            <p className="text-2xl font-bold text-red-600">
              {report.criticalIssues}
            </p>
            <p className="text-sm text-red-600">즉시 수정 필요</p>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <h3 className="text-sm font-medium text-orange-800">경고</h3>
            <p className="text-2xl font-bold text-orange-600">
              {report.seriousIssues}
            </p>
            <p className="text-sm text-orange-600">우선 해결</p>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <h3 className="text-sm font-medium text-yellow-800">정보</h3>
            <p className="text-2xl font-bold text-yellow-600">
              {report.moderateIssues}
            </p>
            <p className="text-sm text-yellow-600">참고사항</p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="text-sm font-medium text-blue-800">전체 이슈</h3>
            <p className="text-2xl font-bold text-blue-600">
              {report.totalIssues}
            </p>
            <p className="text-sm text-blue-600">발견된 문제</p>
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
                    <span className="text-xl">{getTypeIcon(issue.type)}</span>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getTypeColor(issue.type)}`}>
                          {issue.type.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          {issue.type === 'error' ? '❌ 오류' : issue.type === 'warning' ? '⚠️ 경고' : 'ℹ️ 정보'}
                        </span>
                      </div>
                      <p className="font-medium text-gray-900 mb-1">{issue.message}</p>
                      <p className="text-sm text-gray-600 font-mono bg-gray-100 px-2 py-1 rounded">
                        {issue.element || 'N/A'}
                      </p>
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
                <p className="text-gray-600">{selectedIssue.recommendation}</p>
              </div>
              <div>
                <h5 className="font-medium text-gray-700">영향도</h5>
                <p className="text-gray-600">{selectedIssue.impact} - {getImpactDescription(selectedIssue.impact)}</p>
              </div>
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