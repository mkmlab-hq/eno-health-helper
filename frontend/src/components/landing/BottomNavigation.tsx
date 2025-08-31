'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  icon: string;
  label: string;
  href: string;
  description: string;
}

const navItems: NavItem[] = [
  {
    icon: '🏠',
    label: '홈',
    href: '/persona-diary',
    description: 'MKM12 동역학 구름'
  },
  {
    icon: '✍️',
    label: '기록',
    href: '/persona-diary/log',
    description: '일기 & 일정'
  },
  {
    icon: '📊',
    label: '분석',
    href: '/persona-diary/analysis',
    description: '디지털 지문'
  },
  {
    icon: '🧠',
    label: '어드바이저',
    href: '/persona-diary/advisor',
    description: 'AI 조언'
  }
];

export default function BottomNavigation() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-lg border-t border-slate-700">
      <div className="max-w-md mx-auto">
        <div className="grid grid-cols-4 gap-1 p-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center py-3 px-2 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-eno-400/20 text-eno-400 border border-eno-400/30'
                    : 'text-gray-400 hover:text-gray-300 hover:bg-slate-800/50'
                }`}
              >
                <span className="text-2xl mb-1">{item.icon}</span>
                <span className="text-xs font-medium">{item.label}</span>
                <span className="text-xs text-gray-500 mt-1">{item.description}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
