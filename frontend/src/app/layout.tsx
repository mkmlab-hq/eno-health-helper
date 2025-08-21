import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '엔오건강도우미 - ENO Health Helper',
  description: '엔오플렉스 건강기능식품 전용 동반 서비스',
};

export default function RootLayout({
  children,
}: {
  children: any;
}) {
  return (
    <html lang="ko">
      <body>
        {children}
      </body>
    </html>
  );
} 