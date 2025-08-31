import React from 'react';
import BottomNavigation from '@/components/landing/BottomNavigation';

export default function PersonaDiaryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900">
      {/* 메인 컨텐츠 */}
      <main className="pb-24">
        {children}
      </main>
      
      {/* 하단 네비게이션 */}
      <BottomNavigation />
    </div>
  );
}
