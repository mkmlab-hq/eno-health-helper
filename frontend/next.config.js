/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizeCss: true,
    optimizePackageImports: [
      'lucide-react'
    ]
  },
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // SEO 최적화
  generateEtags: false,
  compress: true,
  poweredByHeader: false,
}

module.exports = nextConfig