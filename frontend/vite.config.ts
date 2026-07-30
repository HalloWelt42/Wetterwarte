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
        // Welt-Kacheln (hell/dunkel/Satellit) vom lightningmap-Dienst.
        "/kachel": {
          target: env.KACHEL_HOST || "http://192.168.178.49:8100",
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/kachel/, "/api/tile"),
        },
      },
    },
  };
});
