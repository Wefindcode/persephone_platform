import { fileURLToPath } from 'node:url';

const projectRoot = fileURLToPath(new URL('.', import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  webpack: (config) => {
    config.resolve.alias = config.resolve.alias ?? {};
    config.resolve.alias['@'] = projectRoot;
    return config;
  },
};

export default nextConfig;
