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
      },
    },
    cors: {
      origin: "http://localhost:8001",
      methods: ["POST", "GET"],
      allowedHeaders: ["Content-Type", "application/json"],
    },
  },
  build: {
    outDir: "../app/assets/",
    assetsDir: "./",
    emptyOutDir: true,
  },
});
