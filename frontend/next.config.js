/** @type {import('next').NextConfig} */
const nextConfig = {
  // 정적 내보내기 설정
  output: 'export',
  trailingSlash: true,
  
  // 기본 설정만 유지
  reactStrictMode: true,
  
  // 카메라와 마이크 권한 허용
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Permissions-Policy',
            value: 'camera=(self), microphone=(self), geolocation=(self)',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;