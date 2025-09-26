'use client';

import React from 'react';

interface PerformanceDashboardProps {
  onClose: () => void;
}

export default function PerformanceDashboard({ onClose }: PerformanceDashboardProps) {
  // 임시로 비활성화 - 빌드 오류 수정 후 활성화 예정
  return (
    <div className="p-4 text-center text-gray-500">
      성능 대시보드 기능이 일시적으로 비활성화되었습니다.
    </div>
  );
} 