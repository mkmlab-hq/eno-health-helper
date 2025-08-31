/** @type {import('next').NextConfig} */
const nextConfig = {
  // Vercel 배포용 설정 - standalone 제거
  // output: 'standalone', // 이 줄 제거
  
  // 기본 설정
  reactStrictMode: true,
  swcMinify: true,
  
  // 이미지 최적화
  images: {
    domains: ['localhost', 'eno.no1kmedi.com'],
    unoptimized: false,
  },
  
  // 빌드 최적화
  poweredByHeader: false,
  compress: true,
};

module.exports = nextConfig;