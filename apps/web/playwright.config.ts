import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  use: {
    baseURL: process.env.NEXUS_WEB_ORIGIN ?? "http://127.0.0.1:3000",
    channel: process.env.NEXUS_BROWSER_CHANNEL,
  },
});
