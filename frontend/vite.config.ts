import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// In development the API runs on :8000; the proxy keeps cookies same-origin.
// 127.0.0.1 (not "localhost") on purpose: on some Node/Windows setups "localhost" resolves to IPv6 ::1 first, while
// uvicorn listens on IPv4 127.0.0.1, which makes every /api call (login, register) fail with ECONNREFUSED.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, host: "127.0.0.1", proxy: { "/api": { target: "http://127.0.0.1:8000", changeOrigin: false } } },
  build: { outDir: "dist", sourcemap: false },
});
