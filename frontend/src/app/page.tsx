"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import UserFeedback from '@/components/UserFeedback';
import PerformanceDashboard from '@/components/PerformanceDashboard';
import AccessibilityReportComponent from '@/components/AccessibilityReport';
import { feedbackService, FeedbackData } from '@/lib/feedbackService';

export default function Home() {
  const [showFeedback, setShowFeedback] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  const [showAccessibility, setShowAccessibility] = useState(false);
  // feedbackService는 이미 import된 싱글톤 인스턴스

  const handleFeedbackSubmit = async (feedback: any) => {
    try {
      // UserFeedback에서 받은 데이터를 FeedbackService 형식으로 변환
      const feedbackData = {
        userId: 'anonymous',
        type: 'general' as const,
        title: `${feedback.category} 피드백`,
        description: feedback.comment,
        priority: 'medium' as const,
        status: 'open' as const
      };
      
      await feedbackService.createFeedback(feedbackData);
      alert('피드백이 성공적으로 제출되었습니다!');
    } catch (error) {
      console.error('피드백 제출 오류:', error);
      alert('피드백 제출 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
          <div className="w-12 h-12 text-white">🩺</div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-4">엔오건강도우미</h2>
        <p className="text-gray-300 mb-6">건강 측정 서비스에 오신 것을 환영합니다</p>
        
        <div className="space-y-4">
          <Link
            href="/test"
            className="block bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors"
          >
            카메라/마이크 테스트
          </Link>
          
          <Link
            href="/measure"
            className="block bg-green-500 text-white px-8 py-3 rounded-lg hover:bg-green-600 transition-colors"
          >
            건강 측정 시작
          </Link>

          <button
            onClick={() => setShowFeedback(true)}
            className="block bg-purple-500 text-white px-8 py-3 rounded-lg hover:bg-purple-600 transition-colors mx-auto"
          >
            💬 사용자 피드백
          </button>

          <button
            onClick={() => setShowPerformance(true)}
            className="block bg-indigo-500 text-white px-8 py-3 rounded-lg hover:bg-indigo-600 transition-colors mx-auto"
          >
            📊 성능 모니터링
          </button>

          <button
            onClick={() => setShowAccessibility(true)}
            className="block bg-teal-500 text-white px-8 py-3 rounded-lg hover:bg-teal-600 transition-colors mx-auto"
          >
            ♿ 접근성 테스트
          </button>
        </div>

        {/* 피드백 통계 표시 */}
        <div className="mt-8 p-4 bg-white bg-opacity-10 rounded-lg">
          <h3 className="text-white text-lg font-semibold mb-2">피드백 통계</h3>
          <div className="text-gray-300 text-sm">
            {(() => {
              const stats = feedbackService.getFeedbackStats();
              return (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p>총 피드백: {stats.total}개</p>
                    <p>해결된 이슈: {stats.resolved}개</p>
                  </div>
                  <div>
                    <p>열린 이슈: {stats.open}개</p>
                    <p>전체 이슈: {stats.total}개</p>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      </div>

      {/* 피드백 모달 */}
      {showFeedback && (
        <UserFeedback
          onSubmit={handleFeedbackSubmit}
          onClose={() => setShowFeedback(false)}
        />
      )}

      {/* 성능 모니터링 대시보드 */}
      {showPerformance && (
        <PerformanceDashboard
          onClose={() => setShowPerformance(false)}
        />
      )}

      {/* 접근성 테스트 결과 */}
      {showAccessibility && (
        <AccessibilityReportComponent
          onClose={() => setShowAccessibility(false)}
        />
      )}
    </div>
  );
} 