import type { NextConfig } from "next";

const config: NextConfig = {
  agentRules: false,
  async rewrites() {
    const origin = process.env.NEXUS_API_ORIGIN ?? "http://127.0.0.1:8000";
    return ["model-sources", "workspaces"].map(resource => ({
      source: `/api/v1/${resource}/:path*`,
      destination: `${origin}/api/v1/${resource}/:path*`,
    }));
  },
};

export default config;
