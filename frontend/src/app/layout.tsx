import type { Metadata } from 'next'
import { AuthProvider } from '@/context/AuthContext'
import './globals.css'

export const metadata: Metadata = {
  title: '엔오건강도우미 - AI 기반 건강 측정',
  description: 'rPPG와 음성 분석을 통한 정확한 건강 측정 서비스',
  themeColor: '#0ea5e9',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>
        <a href="#main-content" className="skip-link">본문으로 건너뛰기</a>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
} 