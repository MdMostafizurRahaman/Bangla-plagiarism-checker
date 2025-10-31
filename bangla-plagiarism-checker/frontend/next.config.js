/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Enable TypeScript strict mode
  typescript: {
    tsconfigPath: './tsconfig.json',
  },
  
  // Configure API routes
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/:path*` : 'http://localhost:8000/:path*',
      },
    ];
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // Image optimization
  images: {
    domains: ['localhost'],
  },
  
  // Experimental features
  experimental: {
    // Remove appDir as it's no longer needed in Next.js 14
  },
};

module.exports = nextConfig;