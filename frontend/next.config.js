/** @type {import('next').NextConfig} */
const nextConfig = {
  // 기본 설정만 유지
  experimental: {
    // 실험적 기능 비활성화
  },
  
  // 이미지 도메인 설정
  images: {
    domains: ['localhost'],
  },
  
  // 보안 헤더 설정
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig; 