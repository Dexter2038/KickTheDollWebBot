import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8001",
        rewriteWsOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
    cors: {
      origin: "http://localhost:8001",
      methods: ["POST", "GET"],
      allowedHeaders: ["Content-Type", "application/json"],
    },
  },
  build: {
    outDir: "build",
    assetsDir: "assets",
    emptyOutDir: true,
  },
});
