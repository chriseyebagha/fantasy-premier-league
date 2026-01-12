import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/fantasy',
  trailingSlash: true,
  async rewrites() {
    return [
      {
        source: '/api/engine/:path*',
        destination: 'http://127.0.0.1:5001/api/:path*',
      },
    ];
  },
};

export default nextConfig;
