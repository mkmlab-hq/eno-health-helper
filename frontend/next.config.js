/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js 14에서는 appDir이 기본적으로 활성화됨
  // experimental.appDir 옵션 제거
  output: 'export', // 정적 내보내기 (PWA 배포용)
  trailingSlash: true, // 정적 호스팅 호환성
  images: {
    unoptimized: true // 정적 내보내기 시 이미지 최적화 비활성화
  }
}

module.exports = nextConfig 