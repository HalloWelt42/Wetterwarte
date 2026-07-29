import { defineConfig, loadEnv } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// Ports stammen aus der projekt-eindeutigen .env im Projektwurzelverzeichnis.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "..", "");
  const frontendPort = Number(env.FRONTEND_PORT) || 6151;
  const backendPort = Number(env.BACKEND_PORT) || 6150;
  return {
    plugins: [svelte()],
    server: {
      port: frontendPort,
      strictPort: true,
      // same-origin: /api wird an das Backend weitergereicht (kein CORS noetig).
      proxy: {
        "/api": { target: `http://localhost:${backendPort}`, changeOrigin: true },
      },
    },
  };
});
