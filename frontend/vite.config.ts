import { readFileSync, writeFileSync } from "node:fs";
import { defineConfig, loadEnv, type Plugin } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import fassungDatei from "../version.json";
import telefonKatalog from "../gemeinsam/telefon-katalog.json";
import wettercodes from "../gemeinsam/wettercodes.json";
import meldungen from "../gemeinsam/meldungen.json";

// Fassung der Oberfläche aus der einzigen Quelle (version.json); weicht die des Servers ab, lädt die Oberfläche neu
// (src/lib/fassung.svelte.ts). Als Import zählt version.json zu den Abhängigkeiten der Konfiguration: ändert sie
// sich, startet der Entwicklungsserver von selbst neu, und eingebaute und Server-Fassung bleiben gleich.
const FASSUNG = fassungDatei.version;

// Zwei Einstiege: index.html (Desktop) und telefon.html (Telefon, eigenes Bündel). Im Betrieb liefert
// nginx /telefon aus telefon.html; in der Entwicklung übernimmt das dieses kleine Plugin.
function telefonAdresse(): Plugin {
  return {
    name: "telefon-adresse",
    configureServer(server) {
      server.middlewares.use((anfrage, _antwort, weiter) => {
        const req = anfrage as unknown as { url?: string };
        if (req.url === "/telefon" || req.url?.startsWith("/telefon?")) req.url = req.url.replace("/telefon", "/telefon.html");
        weiter();
      });
    },
  };
}

// App-Symbol eingebettet statt verlinkt: Über die sichere Adresse (Hauszertifikat) holt das iPhone ein verlinktes
// Symbol für den Home-Bildschirm nicht und zeigt nur den Anfangsbuchstaben; alle Apps mit Hauszertifikat sind
// betroffen, die über http nicht. Eingebettet braucht es keinen Abruf. Quelle bleiben die PNG in public/
// (tools/symbole.py); beim Bau werden apple-touch-icon in den Seiten und die Symbole "any" in den Manifesten zu
// data:-Adressen.
function symbolEinbetten(): Plugin {
  const daten = (datei: string) => `data:image/png;base64,${readFileSync(new URL(`./public/${datei}`, import.meta.url)).toString("base64")}`;
  return {
    name: "symbol-einbetten",
    apply: "build",
    transformIndexHtml: (html) => html.replace('href="/apple-touch-icon.png"', `href="${daten("apple-touch-icon.png")}"`),
    writeBundle(optionen) {
      for (const name of ["telefon.webmanifest", "site.webmanifest"]) {
        const ziel = `${optionen.dir}/${name}`;
        const manifest = JSON.parse(readFileSync(ziel, "utf-8"));
        for (const symbol of manifest.icons ?? []) {
          if (symbol.purpose !== "maskable") symbol.src = daten(symbol.src.replace(/^\//, ""));
        }
        writeFileSync(ziel, JSON.stringify(manifest));
      }
    },
  };
}

// Ports stammen aus der projekt-eindeutigen .env im Projektwurzelverzeichnis.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "..", "");
  const frontendPort = Number(env.FRONTEND_PORT) || 6151;
  const backendPort = Number(env.BACKEND_PORT) || 6150;
  return {
    plugins: [svelte(), telefonAdresse(), symbolEinbetten()],
    define: {
      __FASSUNG__: JSON.stringify(FASSUNG),
      // Mit dem Backend geteilte Dateien (gemeinsam/): einzige Wahrheit, beim Bau eingebaut.
      __TELEFON_KATALOG__: JSON.stringify(telefonKatalog),
      __WETTERCODES__: JSON.stringify(wettercodes),
      // Meldearten, Einstellmöglichkeiten und Sätze der Ansagen (docs/WARNUNGEN.md)
      __MELDUNGEN__: JSON.stringify(meldungen),
    },
    build: {
      rollupOptions: {
        input: {
          desktop: new URL("./index.html", import.meta.url).pathname,
          telefon: new URL("./telefon.html", import.meta.url).pathname,
        },
      },
    },
    server: {
      port: frontendPort,
      strictPort: true,
      // same-origin: /api ans Backend, /karte an den lokalen Kartenserver (osmlocal).
      // So werden Karten-Kacheln same-origin geladen (kein CORS noetig). Adressen von Kartendienst und
      // Blitz-Dienst wie im Betrieb aus OSMLOCAL_KARTEN und LIGHTNING_BASE (.env im Hauptordner).
      proxy: {
        "/api": { target: `http://localhost:${backendPort}`, changeOrigin: true },
        "/karte": {
          target: env.OSMLOCAL_KARTEN || "http://localhost:8121",
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
          target: env.LIGHTNING_BASE || "http://localhost:8100",
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/blitze/, "/api/strikes"),
        },
        // Live-Blitz-WebSocket (fuer die optionale Wellen-Simulation).
        "/ws-blitze": {
          target: env.LIGHTNING_BASE || "http://localhost:8100",
          changeOrigin: true,
          ws: true,
          rewrite: (p) => p.replace(/^\/ws-blitze/, "/ws"),
        },
      },
    },
  };
});
