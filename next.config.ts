import type { NextConfig } from "next";
import withPWA from "@ducanh2912/next-pwa";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  turbopack: {
    root: __dirname,
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "learn.microsoft.com" },
      { protocol: "https", hostname: "graph.microsoft.com" },
    ],
  },
};

export default withPWA({
  dest: "public",
  // Do NOT cache navigation HTML — auth pages must always load fresh from network
  cacheOnFrontEndNav: false,
  aggressiveFrontEndNavCaching: false,
  reloadOnOnline: true,
  disable: process.env.NODE_ENV === "development",
  workboxOptions: {
    disableDevLogs: true,
    // Force new service worker to activate immediately on all clients
    skipWaiting: true,
    clientsClaim: true,
    // Exclude auth + API routes from any caching
    exclude: [/\/auth\//, /\/api\//],
  },
})(nextConfig);
