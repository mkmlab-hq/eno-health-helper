import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '엔오건강도우미 - ENO Health Helper',
  description: '엔오플렉스 건강기능식품 전용 동반 서비스로, 복용 전후 생체신호 변화를 측정하여 개인화된 웰니스 가이드를 제공합니다.',
  keywords: '엔오건강도우미, ENO Health Helper, 건강 측정, RPPG, 음성 분석, 웰니스',
  authors: [{ name: 'MKM Lab' }],
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no',
  themeColor: '#0ea5e9',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: '엔오건강도우미',
  },
  openGraph: {
    title: '엔오건강도우미',
    description: '엔오플렉스 건강기능식품 전용 동반 서비스',
    url: 'https://eno.no1kmedi.com',
    siteName: '엔오건강도우미',
    locale: 'ko_KR',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '엔오건강도우미',
    description: '엔오플렉스 건강기능식품 전용 동반 서비스',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="엔오건강도우미" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="msapplication-TileColor" content="#0ea5e9" />
        <meta name="msapplication-TileImage" content="/icons/icon-144x144.png" />
      </head>
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-eno-50 to-eno-100">
          {children}
        </div>
        
        {/* PWA 서비스 워커 등록 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('SW 등록 성공:', registration.scope);
                    })
                    .catch(function(error) {
                      console.log('SW 등록 실패:', error);
                    });
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
} 