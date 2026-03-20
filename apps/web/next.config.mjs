/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@newsalpha/shared"],
  experimental: {
    typedRoutes: false
  }
};

export default nextConfig;

