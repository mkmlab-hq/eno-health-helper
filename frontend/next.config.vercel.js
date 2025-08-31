/** @type {import('next').NextConfig} */
const nextConfig = {
  // Vercel 배포용 설정
  output: 'standalone',
  
  // 기본 설정
  reactStrictMode: true,
  swcMinify: true,
  
  // 이미지 최적화 활성화
  images: {
    domains: ['localhost', 'eno.no1kmedi.com'],
    unoptimized: false,
  },
  
  // API 라우트 활성화
  experimental: {
    appDir: true,
  },
  
  // 빌드 시 경고 무시
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  
  // Vercel 최적화
  poweredByHeader: false,
  compress: true,
  
  // 환경 변수 설정
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
};

module.exports = nextConfig;
