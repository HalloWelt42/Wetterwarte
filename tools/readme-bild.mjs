// README-Bild (.github/bilder/geraete.png): Desktop und Telefon der echten App in gezeichneten Geräten
// (mockups/praesentation.html). Chrome kopflos über das DevTools-Protokoll, ohne weitere Pakete (Node 22).
//
// Vorher: eine App mit frischer Datenbank, also nur den Demo-Orten (keine persönlichen Orte), etwa der Probelauf
// des Produktionsaufbaus, und der Entwurfsserver (./wetter mockup). Chrome startet das Skript selbst.
//
//   node tools/readme-bild.mjs --app http://localhost:6181 --ort koeln
//
// Das Telefon zeigt die Lage "Leichter Regen in 30 Minuten" (Lageband, Regenkachel, Mitteilung), damit das Bild
// die aktiven Warnungen zeigt; alle übrigen Werte sind die echten des Orts. Ton bleibt aus.
import { spawn } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
const argumente = Object.fromEntries(process.argv.slice(2).join(" ").split("--").filter(Boolean).map((a) => a.trim().split(/\s+/)));
const APP = argumente.app ?? "http://localhost:6181";
const ENTWURF = argumente.entwurf ?? "http://localhost:6159";
const ORT = argumente.ort ?? "koeln";
const CHROME = argumente.chrome ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9350;

const warte = (ms) => new Promise((r) => setTimeout(r, ms));
const profil = mkdtempSync(join(tmpdir(), "readme-bild-"));
// Software-WebGL (SwiftShader), damit Karten auch kopflos gezeichnet werden
const chrome = spawn(CHROME, ["--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--mute-audio", "--hide-scrollbars", `--remote-debugging-port=${PORT}`,
  "--remote-allow-origins=*", `--user-data-dir=${profil}`, "--no-first-run", "about:blank"], { stdio: "ignore" });

async function verbinden() {
  for (let i = 0; i < 50; i++) {
    try {
      const seiten = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
      const seite = seiten.find((s) => s.type === "page");
      if (seite) return seite.webSocketDebuggerUrl;
    } catch {
      // Chrome startet noch
    }
    await warte(200);
  }
  throw new Error("Chrome antwortet nicht");
}

const ws = new WebSocket(await verbinden());
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let n = 0;
const offen = new Map();
const warnungen = new Set();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && offen.has(m.id)) { offen.get(m.id)(m.result); offen.delete(m.id); }
  // Warnungen der Seite mit ausgeben (etwa eine Karte, die nicht angelegt werden konnte)
  if (m.method === "Runtime.consoleAPICalled" && ["warning", "error"].includes(m.params.type)) warnungen.add(m.params.args.map((a) => a.value ?? a.description ?? "").join(" ").slice(0, 200));
  if (m.method === "Runtime.exceptionThrown") warnungen.add(String(m.params.exceptionDetails.exception?.description ?? "").slice(0, 200));
});
const cdp = (method, params = {}) => new Promise((r) => { const id = ++n; offen.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const auswerten = async (ausdruck) => (await cdp("Runtime.evaluate", { expression: ausdruck, awaitPromise: true, returnByValue: true })).result?.value;

async function aufnehmen(datei, clip) {
  const { data } = await cdp("Page.captureScreenshot", { format: "png", ...(clip ? { clip: { ...clip, scale: 1 } } : {}) });
  mkdirSync(dirname(datei), { recursive: true });
  writeFileSync(datei, Buffer.from(data, "base64"));
  console.log("geschrieben:", datei.replace(WURZEL + "/", ""));
}

async function laden(url, ms) {
  await cdp("Page.navigate", { url });
  await warte(ms);
}

/** Warten, bis der Ausdruck wahr ist (höchstens 40 Sekunden), dann noch kurz für Bilder und Übergänge. */
async function bisDa(ausdruck, beschreibung) {
  for (let i = 0; i < 160; i++) {
    if (await auswerten(ausdruck)) {
      await warte(1500);
      return;
    }
    await warte(250);
  }
  throw new Error(`nicht fertig geladen: ${beschreibung}`);
}

await cdp("Page.enable");
await cdp("Runtime.enable");

// Die Lage, die das Bild zeigt: Regen in 30 Minuten, auf beiden Geräten gleich
const jetzt = Date.now();
const regenWerte = [0, 0, 0, 0, 0, 0, 0.4, 0.8, 1.2, 1.6, 1.4, 1.1, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0, 0, 0, 0, 0, 0];
const lage = [{
  art: "niederschlag", schluessel: "niederschlag", klasse: "regen_leicht", rang: 0, stufe: 1, beginn: new Date(jetzt + 30 * 60000).toISOString(),
  laeuft: false, vorlauf_min: 30, vorlaufstufe: 30, quelle: "radar", titel: "Leichter Regen in 30 Minuten",
  text: "Es wird in deiner Region in 30 Minuten leicht regnen.", bausteine: ["regen_leicht_30"],
}];
const regen = { schritt_min: 5, werte: regenWerte, beginn_min: 30, ende_min: 90, max_mm_h: 1.6, quelle: "radar" };
const kachel = { text: "Regen in 30 Minuten", balken: regenWerte.map((w) => (w ? Math.round((w / 1.6) * 100) : 3)), schritt_min: 5, quelle: "radar" };
await cdp("Page.addScriptToEvaluateOnNewDocument", { source: `
  const echt = window.fetch.bind(window);
  window.fetch = async (url, opt) => {
    const r = await echt(url, opt);
    const pfad = String(url);
    if (!/\\/wetter\\/(kompakt|complete|basis)\\//.test(pfad) || !r.ok) return r;
    const j = await r.json();
    if (pfad.includes("/kompakt/")) { j.data.lage = ${JSON.stringify(lage)}; j.data.regen = ${JSON.stringify(regen)}; }
    else if (j.data && "nowcast" in j.data) j.data.nowcast = ${JSON.stringify(kachel)};
    return new Response(JSON.stringify(j), { status: 200, headers: { "Content-Type": "application/json" } });
  };` });

// Gerätewerte vorab auf einer schlichten Seite derselben Herkunft setzen: jede Ansicht wird dann nur einmal geladen.
// Ein zweites Laden derselben Seite sperrt kopflos das Software-WebGL, dann zeigte die Karte nur ihren Hinweis.
await laden(`${APP}/api/v1/health`, 800);
await auswerten(`for (const [k, v] of Object.entries({ "willkommen.gesehen": true, ansicht: "desktop", "telefon.nacht": "aus", "telefon.ansagen": false, "telefon.stufe": "normal" })) localStorage.setItem("wetterwarte." + k, JSON.stringify(v))`);

// 1. Desktop, 1600 x 1000 mit doppelter Dichte
await cdp("Emulation.setDeviceMetricsOverride", { width: 1600, height: 1000, deviceScaleFactor: 2, mobile: false });
await laden(`${APP}/?ort=${ORT}`, 500);
await bisDa(`document.body.innerText.includes("aktualisiert") && !document.body.innerText.includes("lädt")`, "Desktop");
// Profil Garten: ohne Kartenkachel, denn kopflos bildet Chrome die WebGL-Fläche im Bild nicht ab
await auswerten(`[...document.querySelectorAll("button")].find((b) => b.innerText.trim() === "Garten")?.click()`);
await warte(1000);
await bisDa(`document.body.innerText.includes("POLLENFLUG") && !document.body.innerText.includes("lädt")`, "Desktop, Profil Garten");
await aufnehmen(join(WURZEL, "mockups/praesentation/desktop.png"));

// 2. Telefon, 390 x 844 mit dreifacher Dichte, Tagbetrieb, Ansagen aus
await cdp("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 3, mobile: true });
await cdp("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
await laden(`${APP}/telefon?ort=${ORT}`, 500);
await bisDa(`!!document.querySelector(".warnband.lage") && document.querySelectorAll(".k").length > 4`, "Telefon");
const uhr = await auswerten(`new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })`);
const ortName = await auswerten(`document.querySelector(".kopf .name, .kopf-ort")?.textContent?.trim() ?? ""`);
await aufnehmen(join(WURZEL, "mockups/praesentation/telefon.png"));

// 3. Präsentation 2400 x 1400, freigestellt
await cdp("Emulation.setTouchEmulationEnabled", { enabled: false });
await cdp("Emulation.setDeviceMetricsOverride", { width: 2400, height: 1400, deviceScaleFactor: 1, mobile: false });
await cdp("Emulation.setDefaultBackgroundColorOverride", { color: { r: 0, g: 0, b: 0, a: 0 } });
const p = new URLSearchParams({ uhr, titel: `${ortName || "Köln"}: ${lage[0].titel}`, text: lage[0].text });
await laden(`${ENTWURF}/mockups/praesentation.html?${p}`, 2500);
await aufnehmen(join(WURZEL, ".github/bilder/geraete.png"), { x: 0, y: 0, width: 2400, height: 1400 });

if (warnungen.size) console.log("Warnungen der Seiten:\n  " + [...warnungen].join("\n  "));
ws.close();
chrome.kill();
await warte(300);
rmSync(profil, { recursive: true, force: true });
