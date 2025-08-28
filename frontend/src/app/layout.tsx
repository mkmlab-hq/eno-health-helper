import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import PWAInstaller from '@/components/PWAInstaller'
import { AuthProvider } from '@/context/AuthContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ENO Health Helper - AI 기반 건강 측정 도우미',
  description: 'rPPG와 음성 분석을 통한 정확한 건강 측정 및 분석 서비스',
  keywords: ['건강 측정', 'rPPG', '음성 분석', 'AI 건강', '건강 관리'],
  authors: [{ name: 'MKM Lab' }],
  creator: 'MKM Lab',
  publisher: 'MKM Lab',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://eno-health-helper.firebaseapp.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'ENO Health Helper - AI 기반 건강 측정 도우미',
    description: 'rPPG와 음성 분석을 통한 정확한 건강 측정 및 분석 서비스',
    url: 'https://eno-health-helper.firebaseapp.com',
    siteName: 'ENO Health Helper',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'ENO Health Helper',
      },
    ],
    locale: 'ko_KR',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ENO Health Helper - AI 기반 건강 측정 도우미',
    description: 'rPPG와 음성 분석을 통한 정확한 건강 측정 및 분석 서비스',
    images: ['/og-image.png'],
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
  verification: {
    google: 'your-google-verification-code',
  },
  manifest: '/manifest.json',
  other: {
    'mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-status-bar-style': 'black-translucent',
    'apple-mobile-web-app-title': 'ENO Health',
    'msapplication-TileColor': '#00d4ff',
    'msapplication-config': '/browserconfig.xml',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#00d4ff',
  colorScheme: 'dark',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="application-name" content="ENO Health Helper" />
        <meta name="apple-mobile-web-app-title" content="ENO Health" />
        <meta name="msapplication-TileColor" content="#00d4ff" />
        <meta name="msapplication-TileImage" content="/icons/icon-144x144.png" />
        <meta name="theme-color" content="#00d4ff" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        
        {/* PWA 관련 메타데이터 */}
        <meta name="description" content="AI 기반 건강 측정 및 분석 도우미" />
        <meta name="keywords" content="건강 측정, rPPG, 음성 분석, AI 건강, 건강 관리" />
        <meta name="author" content="MKM Lab" />
        
        {/* Open Graph 메타데이터 */}
        <meta property="og:title" content="ENO Health Helper - AI 기반 건강 측정 도우미" />
        <meta property="og:description" content="rPPG와 음성 분석을 통한 정확한 건강 측정 및 분석 서비스" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://eno-health-helper.firebaseapp.com" />
        <meta property="og:image" content="/og-image.png" />
        <meta property="og:site_name" content="ENO Health Helper" />
        <meta property="og:locale" content="ko_KR" />
        
        {/* Twitter 메타데이터 */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="ENO Health Helper - AI 기반 건강 측정 도우미" />
        <meta name="twitter:description" content="rPPG와 음성 분석을 통한 정확한 건강 측정 및 분석 서비스" />
        <meta name="twitter:image" content="/og-image.png" />
        
        {/* 추가 메타데이터 */}
        <meta name="robots" content="index, follow" />
        <meta name="googlebot" content="index, follow" />
        <link rel="canonical" href="https://eno-health-helper.firebaseapp.com" />
      </head>
      <body className={inter.className}>
        <AuthProvider>
          {children}
          <PWAInstaller />
        </AuthProvider>
      </body>
    </html>
  )
} 