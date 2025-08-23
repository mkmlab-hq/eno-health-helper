/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  experimental: {
    optimizeCss: true
  },
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // SEO 최적화
  generateEtags: false,
  compress: true
}

module.exports = nextConfig