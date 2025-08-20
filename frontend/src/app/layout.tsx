import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '엔오건강도우미 - ENO Health Helper',
  description: '엔오플렉스 건강기능식품 전용 동반 서비스로, 복용 전후 생체신호 변화를 측정하여 개인화된 웰니스 가이드를 제공합니다.',
  keywords: '엔오건강도우미, ENO Health Helper, 건강 측정, RPPG, 음성 분석, 웰니스',
  authors: [{ name: 'MKM Lab' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0ea5e9',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-eno-50 to-eno-100">
          {children}
        </div>
      </body>
    </html>
  );
} 