'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui';
import { Card, CardContent, CardFooter } from '@/components/ui';

interface ErrorBoundaryProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorBoundary({ error, reset }: ErrorBoundaryProps) {
  useEffect(() => {
    // 에러 로깅 (실제 프로덕션에서는 Sentry 등으로 전송)
    console.error('Application Error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <Card variant="glass" className="border-red-400/20 shadow-2xl">
          <CardContent className="p-8">
            {/* 에러 아이콘 */}
            <div className="text-center mb-6">
              <div className="w-20 h-20 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-4">
                <svg className="w-12 h-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">앱 오류가 발생했습니다</h1>
              <p className="text-red-200 text-sm">
                예상치 못한 문제가 발생했습니다. 다시 시도해주세요.
              </p>
            </div>

            {/* 에러 상세 정보 (개발 모드에서만 표시) */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mb-6 p-4 bg-red-900/30 rounded-lg border border-red-400/20">
                <h3 className="text-sm font-semibold text-red-300 mb-2">에러 상세 정보:</h3>
                <div className="text-xs text-red-200 font-mono bg-black/20 p-3 rounded overflow-auto max-h-32">
                  <div><strong>Message:</strong> {error.message}</div>
                  {error.stack && (
                    <div className="mt-2">
                      <strong>Stack:</strong>
                      <pre className="whitespace-pre-wrap">{error.stack}</pre>
                    </div>
                  )}
                  {error.digest && (
                    <div className="mt-2">
                      <strong>Digest:</strong> {error.digest}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 추가 도움말 */}
            <div className="text-center">
              <p className="text-red-200 text-xs">
                문제가 지속되면 관리자에게 문의해주세요
              </p>
              <p className="text-red-300 text-xs mt-1">
                오류 ID: {error.digest || 'N/A'}
              </p>
            </div>
          </CardContent>

          {/* 액션 버튼들 */}
          <CardFooter className="flex flex-col sm:flex-row gap-3 px-8 pb-8">
            <Button
              variant="destructive"
              onClick={reset}
              fullWidth
              className="flex-1"
            >
              다시 시도
            </Button>
            <Button
              variant="secondary"
              onClick={() => window.location.href = '/'}
              fullWidth
              className="flex-1"
            >
              홈으로 이동
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
