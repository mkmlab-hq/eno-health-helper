import React from 'react';

interface ProgressStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

interface ProgressStepsProps {
  steps: ProgressStep[];
  currentStep?: number;
}

export default function ProgressSteps({ steps, currentStep = 0 }: ProgressStepsProps) {
  return (
    <div className="w-full max-w-md mx-auto">
      <div className="space-y-4">
        {steps.map((step, index) => {
          const isActive = step.status === 'active';
          const isCompleted = step.status === 'completed';
          const isError = step.status === 'error';
          
          return (
            <div key={step.id} className="flex items-start space-x-3">
              {/* 단계 번호/아이콘 */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${
                isCompleted 
                  ? 'bg-green-500 text-white' 
                  : isActive 
                    ? 'bg-blue-500 text-white animate-pulse' 
                    : isError
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-500'
              }`}>
                {isCompleted ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : isError ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>

              {/* 단계 내용 */}
              <div className="flex-1 min-w-0">
                <h4 className={`text-sm font-medium transition-colors duration-300 ${
                  isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : isError ? 'text-red-600' : 'text-gray-500'
                }`}>
                  {step.title}
                </h4>
                <p className={`text-xs mt-1 transition-colors duration-300 ${
                  isActive ? 'text-blue-500' : isCompleted ? 'text-green-500' : isError ? 'text-red-500' : 'text-gray-400'
                }`}>
                  {step.description}
                </p>
              </div>

              {/* 상태 표시 */}
              {isActive && (
                <div className="flex-shrink-0">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 전체 진행률 바 */}
      <div className="mt-6">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>진행률</span>
          <span>{Math.round(((currentStep + 1) / steps.length) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out rounded-full"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
