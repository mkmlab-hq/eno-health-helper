/** @type {import('next').NextConfig} */
const nextConfig = {
  // 정적 사이트 빌드 설정
  output: 'export',
  trailingSlash: false,
  
  // 기본 설정
  reactStrictMode: true,
  swcMinify: true,
  
  // 이미지 최적화
  images: {
    domains: ['localhost', 'eno.no1kmedi.com'],
    unoptimized: true, // 정적 사이트용으로 변경
  },
  
  // 빌드 최적화
  poweredByHeader: false,
  compress: true,
};

module.exports = nextConfig;