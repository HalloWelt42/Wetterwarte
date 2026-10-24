// Rauchtest: jede Ansicht der App im echten Aufbau öffnen und alles einsammeln, was schiefgeht: Ausnahmen,
// Konsolenfehler und -warnungen, Meldungen des Browsers (etwa Sicherheitsrichtlinien), die "Issues" der
// Entwicklerwerkzeuge (etwa Eingabefelder ohne id und name) und jede Anfrage mit Status ab 400 oder ohne Antwort. Nur lesend und stumm (Ansagen bleiben aus, keine Mitteilungen).
//
//   node tools/rauchtest.mjs --app http://localhost:6181        Probelauf des Produktionsaufbaus vor dem Ausrollen
//   node tools/rauchtest.mjs --app http://<server>:8061         Betrieb nach dem Ausrollen (./wetter rauchtest)
//
// Jede Ansicht bekommt einen eigenen Chrome (kopflos, Software-WebGL): ein zweites Laden sperrt dort WebGL, dann
// meldete die Karte einen Fehler, der keiner der App ist. Ausgang 1, sobald es einen Befund gibt.
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const argumente = Object.fromEntries(process.argv.slice(2).join(" ").split("--").filter(Boolean).map((a) => a.trim().split(/\s+/)));
const APP = (argumente.app ?? "http://localhost:6181").replace(/\/$/, "");
const CHROME = argumente.chrome ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const RUHE_MS = Number(argumente.ruhe ?? 6000); // nach dem Laden so lange weiter beobachten (Karte, Radar, Takt)

const warte = (ms) => new Promise((r) => setTimeout(r, ms));

const ort = (await (await fetch(`${APP}/api/v1/orte`)).json()).data[0]?.slug ?? "";
const DESKTOP = { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false };
const TELEFON = { width: 390, height: 844, deviceScaleFactor: 2, mobile: true };
const ANSICHTEN = [
  ["Desktop Übersicht", `/?ort=${ort}`, DESKTOP],
  ["Desktop Karte", `/?ansicht=karte&ort=${ort}`, DESKTOP],
  ["Desktop Aufzeichnung", `/?ansicht=aufzeichnung&ort=${ort}`, DESKTOP],
  ["Desktop Archiv", `/?ansicht=archiv&ort=${ort}`, DESKTOP],
  ["Desktop Telefon-Layout", `/?ansicht=telefon&ort=${ort}`, DESKTOP],
  ["Telefon Wetter", `/telefon?ort=${ort}`, TELEFON],
  ["Telefon Karte", `/telefon?ansicht=karte&ort=${ort}`, TELEFON],
  ["Telefon Gesundheit", `/telefon?ansicht=gesundheit&ort=${ort}`, TELEFON],
  ["Telefon Mehr", `/telefon?ansicht=mehr&ort=${ort}`, TELEFON],
  ["Telefon Was kommt", `/telefon?ort=${ort}&blatt=lage`, TELEFON],
  ["Telefon Meldungen", `/telefon?ort=${ort}&blatt=meldungen`, TELEFON],
  ["Telefon Warnungen", `/telefon?ort=${ort}&blatt=warnungen`, TELEFON],
  ["Telefon Kachelformen", `/telefon?ort=${ort}&blatt=schaukasten`, TELEFON],
];

async function pruefe(name, pfad, ansicht, port) {
  const profil = mkdtempSync(join(tmpdir(), "rauchtest-"));
  const chrome = spawn(CHROME, ["--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--mute-audio",
    `--remote-debugging-port=${port}`, "--remote-allow-origins=*", `--user-data-dir=${profil}`, "--no-first-run", "about:blank"], { stdio: "ignore" });
  const befunde = new Set();
  try {
    let adresse;
    for (let i = 0; i < 60 && !adresse; i++) {
      try {
        adresse = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((s) => s.type === "page")?.webSocketDebuggerUrl;
      } catch {
        // Chrome startet noch
      }
      if (!adresse) await warte(200);
    }
    const ws = new WebSocket(adresse);
    await new Promise((r) => ws.addEventListener("open", r, { once: true }));
    let n = 0;
    const offen = new Map();
    const anfragen = new Map();
    ws.addEventListener("message", (e) => {
      const m = JSON.parse(e.data);
      if (m.id && offen.has(m.id)) { offen.get(m.id)(m.result); offen.delete(m.id); }
      const p = m.params;
      if (m.method === "Network.requestWillBeSent") anfragen.set(p.requestId, `${p.request.method} ${p.request.url}`);
      if (m.method === "Runtime.exceptionThrown") befunde.add(`Ausnahme: ${(p.exceptionDetails.exception?.description ?? p.exceptionDetails.text).split("\n")[0]}`);
      if (m.method === "Runtime.consoleAPICalled" && ["error", "warning", "assert"].includes(p.type)) {
        befunde.add(`Konsole ${p.type}: ${p.args.map((a) => a.value ?? a.description ?? "").join(" ").split("\n")[0].slice(0, 200)}`);
      }
      // Hinweise des Software-Grafiktreibers im Testbrowser ("GL Driver Message ... GPU stall") sind keine der App
      if (m.method === "Log.entryAdded" && ["error", "warning"].includes(p.entry.level) && !/GL Driver Message/.test(p.entry.text)) {
        befunde.add(`Browser ${p.entry.level}: ${p.entry.text.slice(0, 200)}`);
      }
      if (m.method === "Network.responseReceived" && p.response.status >= 400) befunde.add(`HTTP ${p.response.status}: ${p.response.url}`);
      if (m.method === "Audits.issueAdded") {
        const d = p.issue.details ?? {};
        const art = d.genericIssueDetails?.errorType ?? Object.keys(d)[0] ?? "";
        befunde.add(`Issue ${p.issue.code}: ${art}`);
      }
      if (m.method === "Network.loadingFailed" && !p.canceled && p.errorText !== "net::ERR_ABORTED") {
        befunde.add(`Anfrage gescheitert (${p.errorText}): ${anfragen.get(p.requestId) ?? p.requestId}`);
      }
    });
    const cdp = (method, params = {}) => new Promise((r) => { const id = ++n; offen.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
    await Promise.all([cdp("Page.enable"), cdp("Runtime.enable"), cdp("Log.enable"), cdp("Network.enable"), cdp("Audits.enable")]);
    await cdp("Emulation.setDeviceMetricsOverride", ansicht);
    if (ansicht.mobile) await cdp("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
    // Begrüßung und Weiche zur Telefonansicht vorab erledigen, damit jede Ansicht nur einmal lädt
    await cdp("Page.navigate", { url: `${APP}/api/v1/health` });
    await warte(500);
    await cdp("Runtime.evaluate", { expression: `localStorage.setItem("wetterwarte.willkommen.gesehen", "true"); localStorage.setItem("wetterwarte.ansicht", JSON.stringify(${JSON.stringify(ansicht.mobile ? "telefon" : "desktop")}))` });
    befunde.clear();
    await cdp("Page.navigate", { url: APP + pfad });
    for (let i = 0; i < 80; i++) {
      await warte(250);
      const fertig = await cdp("Runtime.evaluate", { expression: "document.readyState", returnByValue: true });
      if (fertig.result?.value === "complete") break;
    }
    await warte(RUHE_MS);
    ws.close();
  } finally {
    const beendet = new Promise((r) => chrome.once("exit", r));
    chrome.kill();
    await Promise.race([beendet, warte(5000)]);
    try {
      rmSync(profil, { recursive: true, force: true, maxRetries: 10, retryDelay: 300 });
    } catch {
      // Hilfsprozesse von Chrome schreiben noch: der Ordner liegt im Zwischenordner des Systems
    }
  }
  return [...befunde];
}

let gesamt = 0;
for (const [i, [name, pfad, ansicht]] of ANSICHTEN.entries()) {
  const befunde = await pruefe(name, pfad, ansicht, 9400 + i);
  gesamt += befunde.length;
  console.log(`${befunde.length ? "FEHLER" : "ok    "} ${name}${befunde.length ? "\n  " + befunde.join("\n  ") : ""}`);
}
console.log(gesamt ? `\n${gesamt} Befunde in ${ANSICHTEN.length} Ansichten (${APP})` : `\nkeine Befunde in ${ANSICHTEN.length} Ansichten (${APP})`);
process.exit(gesamt ? 1 : 0);
