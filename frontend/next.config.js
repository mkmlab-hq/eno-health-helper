/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // 랜딩페이지 최적화
  experimental: {
    optimizeCss: true
  },
  // SEO 최적화
  generateEtags: false,
  compress: true
}

module.exports = nextConfig 