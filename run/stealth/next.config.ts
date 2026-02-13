import type { NextConfig } from "next";

const apiBase = process.env.FRONT_API_REWRITE_BASE_URL ?? "http://api:8080";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
      {
        source: "/hello",
        destination: `${apiBase}/hello`,
      },
    ];
  },
};

export default nextConfig;
