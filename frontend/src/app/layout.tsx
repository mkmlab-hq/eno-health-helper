import type { Metadata } from 'next'
import { AuthProvider } from '@/context/AuthContext'
import './globals.css'
import { Noto_Sans_KR, Orbitron } from 'next/font/google'

const notoSans = Noto_Sans_KR({ subsets: ['latin'], weight: ['400','500','700','900'], display: 'swap', variable: '--font-noto' })
const orbitron = Orbitron({ subsets: ['latin'], weight: ['400','700','900'], display: 'swap', variable: '--font-orbitron' })

export const metadata: Metadata = {
  title: '엔오건강도우미 - AI 기반 건강 측정',
  description: 'rPPG와 음성 분석을 통한 정확한 건강 측정 서비스',
  icons: {
    icon: '/icons/favicon.ico'
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className={`${notoSans.variable} ${orbitron.variable}`}>
      <body className="font-[var(--font-noto)]">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
} 