import type { NextConfig } from "next";

const config: NextConfig = {
  agentRules: false,
  async rewrites() {
    return [{
      source: "/api/v1/model-sources/:path*",
      destination: `${process.env.NEXUS_API_ORIGIN ?? "http://127.0.0.1:8000"}/api/v1/model-sources/:path*`,
    }];
  },
};

export default config;
