/** @type {import('next').NextConfig} */
const nextConfig = {
  // Vercel 배포용 설정
  output: 'standalone',
  
  // 기본 설정
  reactStrictMode: true,
  swcMinify: true,
  
  // 이미지 최적화
  images: {
    domains: ['localhost', 'eno.no1kmedi.com'],
    unoptimized: false,
  },
  
  // API 라우트 활성화
  experimental: {
    appDir: true,
  },
  
  // 빌드 최적화
  poweredByHeader: false,
  compress: true,
  
  // 환경 변수
  // env: {
  //   NODE_ENV: process.env.NODE_ENV,
  // },
};

module.exports = nextConfig;