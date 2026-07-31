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
      // same-origin: /api ans Backend, /karte an den lokalen Kartenserver (osmlocal).
      // So werden Karten-Kacheln same-origin geladen (kein CORS noetig).
      proxy: {
        "/api": { target: `http://localhost:${backendPort}`, changeOrigin: true },
        "/karte": {
          target: env.KARTEN_HOST || "http://192.168.178.49:8121",
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/karte/, "/api/v1"),
        },
        // Welt-Kacheln ueber den cachenden Backend-Endpunkt (Offline-Cache).
        "/kachel": {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/kachel/, "/api/v1/kachel"),
        },
        // Live-Blitze (bbox-Abfrage) vom lightningmap-Dienst.
        "/blitze": {
          target: env.KACHEL_HOST || "http://192.168.178.49:8100",
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/blitze/, "/api/strikes"),
        },
        // Live-Blitz-WebSocket (fuer die optionale Wellen-Simulation).
        "/ws-blitze": {
          target: env.KACHEL_HOST || "http://192.168.178.49:8100",
          changeOrigin: true,
          ws: true,
          rewrite: (p) => p.replace(/^\/ws-blitze/, "/ws"),
        },
      },
    },
  };
});
