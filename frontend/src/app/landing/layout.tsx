import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MKM LAB - AI 기반 초개인화 건강 관리의 새로운 패러다임',
  description: 'MKM Lab은 AI를 통해 당신의 고유한 생체, 행동, 그리고 세상의 데이터를 융합하여, 세상에 단 하나뿐인 디지털 지문을 창조합니다.',
  keywords: 'AI, 건강관리, rPPG, 음성분석, 디지털지문, MKM Lab, 엔오건강도우미',
  authors: [{ name: 'MKM Lab' }],
  creator: 'MKM Lab',
  publisher: 'MKM Lab',
  robots: 'index, follow',
  openGraph: {
    title: 'MKM LAB - AI 기반 초개인화 건강 관리',
    description: '당신의 순간을 자산으로, 디지털 지문을 새로운 화폐로',
    type: 'website',
    locale: 'ko_KR',
    siteName: 'MKM LAB',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MKM LAB - AI 기반 초개인화 건강 관리',
    description: '당신의 순간을 자산으로, 디지털 지문을 새로운 화폐로',
  },
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0ea5e9',
}

export default function LandingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head>
        <link rel="canonical" href="https://mkmlab.space" />
        <link rel="icon" href="/favicon.ico" />
        <meta name="google-site-verification" content="your-verification-code" />
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}
