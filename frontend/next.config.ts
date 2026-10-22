import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Минимальный самодостаточный сервер для Docker-образа (.next/standalone).
  output: "standalone",
  poweredByHeader: false,
  // В Docker /api проксирует nginx. Для `npm run dev` без Docker
  // проксируем /api на локальный backend, чтобы адрес API был тем же.
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    const target = process.env.DEV_API_PROXY ?? "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${target}/api/:path*` }];
  },
};

export default nextConfig;
