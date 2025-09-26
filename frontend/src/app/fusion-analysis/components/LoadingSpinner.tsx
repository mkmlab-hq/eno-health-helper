import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'purple';
  text?: string;
  showProgress?: boolean;
  progress?: number;
}

export default function LoadingSpinner({ 
  size = 'md', 
  color = 'blue', 
  text = '로딩 중...',
  showProgress = false,
  progress = 0 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  };

  const colorClasses = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    purple: 'border-purple-500'
  };

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className="flex flex-col items-center justify-center">
      {/* 메인 스피너 */}
      <div className="relative">
        <div className={`${sizeClasses[size]} border-4 border-gray-200 rounded-full animate-spin ${colorClasses[color]}`}></div>
        
        {/* 내부 원형 애니메이션 */}
        <div className={`absolute inset-2 border-2 border-transparent border-t-${colorClasses[color].split('-')[1]}-300 rounded-full animate-spin`} 
             style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        
        {/* 중앙 점 */}
        <div className={`absolute inset-4 bg-${colorClasses[color].split('-')[1]}-500 rounded-full animate-pulse`}></div>
      </div>

      {/* 텍스트 */}
      {text && (
        <p className={`mt-4 text-gray-600 ${textSizes[size]} font-medium`}>
          {text}
        </p>
      )}

      {/* 진행률 바 */}
      {showProgress && (
        <div className="mt-4 w-32 bg-gray-200 rounded-full h-2 overflow-hidden">
          <div 
            className={`h-full bg-${colorClasses[color].split('-')[1]}-500 transition-all duration-300 ease-out rounded-full`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
    </div>
  );
}
