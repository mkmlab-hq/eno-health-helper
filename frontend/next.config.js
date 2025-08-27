/** @type {import('next').NextConfig} */
const nextConfig = {
  // 정적 내보내기 설정 (Firebase Hosting용)
  output: 'export',
  trailingSlash: true,
  distDir: 'out',
  
  // 기본 설정
  reactStrictMode: true,
  swcMinify: true,
  
  // 이미지 최적화 비활성화 (정적 내보내기에서는 지원하지 않음)
  images: {
    unoptimized: true,
  },
  
  // 정적 내보내기 시 동적 라우트 비활성화
  experimental: {
    appDir: true,
  },
  
  // 빌드 시 경고 무시
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
};

module.exports = nextConfig;