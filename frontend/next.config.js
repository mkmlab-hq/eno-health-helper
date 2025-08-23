/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
<<<<<<< HEAD
  experimental: {
    appDir: true,
  },
=======
  trailingSlash: true,
>>>>>>> 7f3f26ec1c67bf4806addae8f0afc8488a161832
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