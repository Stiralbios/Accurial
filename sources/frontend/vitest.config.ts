/// <reference types="vitest" />
import path from "node:path";

import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./app"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    include: ["../../tests/frontend/**/*.test.{ts,tsx}", "app/**/*.test.{ts,tsx}"],
    exclude: ["node_modules", "dist", "app/services/api/generated/**"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      exclude: [
        "node_modules/",
        "dist/",
        "app/services/api/generated/**",
        "app/routeTree.gen.ts",
        "**/*.test.{ts,tsx}",
        "**/*.config.{ts,js}",
        "vitest.setup.ts",
      ],
    },
  },
});
