'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui';
import { Card, CardContent, CardFooter } from '@/components/ui';

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  useEffect(() => {
    // 전역 에러 로깅
    console.error('Global Application Error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900 flex items-center justify-center p-6">
      <div className="max-w-lg w-full">
        <Card variant="glass" className="border-red-400/20 shadow-2xl">
          <CardContent className="p-8">
            {/* 치명적 에러 아이콘 */}
            <div className="text-center mb-6">
              <div className="w-24 h-24 mx-auto bg-red-600/30 rounded-full flex items-center justify-center mb-6">
                <svg className="w-16 h-16 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-white mb-3">치명적 시스템 오류</h1>
              <p className="text-red-200 text-base">
                애플리케이션에 심각한 문제가 발생했습니다.
              </p>
            </div>

            {/* 에러 상세 정보 */}
            <div className="mb-6 p-4 bg-red-900/40 rounded-lg border border-red-400/30">
              <h3 className="text-sm font-semibold text-red-300 mb-2">에러 정보:</h3>
              <div className="text-xs text-red-200 font-mono bg-black/30 p-3 rounded overflow-auto max-h-40">
                <div><strong>Type:</strong> Global Error</div>
                <div><strong>Message:</strong> {error.message}</div>
                {error.digest && (
                  <div><strong>Digest:</strong> {error.digest}</div>
                )}
                {error.stack && (
                  <div className="mt-2">
                    <strong>Stack Trace:</strong>
                    <pre className="whitespace-pre-wrap text-xs">{error.stack}</pre>
                  </div>
                )}
              </div>
            </div>

            {/* 긴급 연락처 */}
            <div className="text-center">
              <p className="text-red-200 text-sm font-semibold mb-2">
                🚨 긴급 상황입니다
              </p>
              <p className="text-red-300 text-xs">
                이 오류가 지속되면 즉시 시스템 관리자에게 연락하세요
              </p>
              <p className="text-red-400 text-xs mt-2">
                오류 ID: {error.digest || 'GLOBAL-ERROR'}
              </p>
            </div>
          </CardContent>

          {/* 복구 옵션 */}
          <CardFooter className="space-y-3 px-8 pb-8">
            <Button
              variant="destructive"
              size="lg"
              onClick={reset}
              fullWidth
            >
              애플리케이션 재시작
            </Button>
            <Button
              variant="secondary"
              onClick={() => window.location.reload()}
              fullWidth
            >
              페이지 새로고침
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
