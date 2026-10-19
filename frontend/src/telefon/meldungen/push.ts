// Mitteilungen aufs Telefon (Web Push, docs/WARNUNGEN.md). Geht nur in einem sicheren Kontext (HTTPS) und auf dem
// iPhone nur aus der App auf dem Home-Bildschirm. Der Service Worker (public/sw.js) zeigt die Mitteilungen.
import { hole } from "../../kern/api";
import { aboLoeschen, aboSetzen, konto, sicheresKonto } from "./konto.svelte";

export type PushLage = "geht" | "unsicher" | "heimbildschirm" | "nicht-unterstuetzt" | "verweigert";

interface Schluessel {
  schluessel: string;
  sichere_adresse: string;
}

function istIos(): boolean {
  return /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

function vomHeimbildschirm(): boolean {
  return matchMedia("(display-mode: standalone)").matches || (navigator as Navigator & { standalone?: boolean }).standalone === true;
}

export function pushLage(): PushLage {
  if (!isSecureContext) return "unsicher";
  if (istIos() && !vomHeimbildschirm()) return "heimbildschirm";
  if (!("serviceWorker" in navigator) || !("PushManager" in window) || !("Notification" in window)) return "nicht-unterstuetzt";
  if (Notification.permission === "denied") return "verweigert";
  return "geht";
}

let schluesselStand: Promise<Schluessel> | null = null;
export function serverSchluessel(): Promise<Schluessel> {
  schluesselStand ??= hole<Schluessel>("/push/schluessel").catch((e) => {
    schluesselStand = null;
    throw e;
  });
  return schluesselStand;
}

function bytes(base64url: string): Uint8Array<ArrayBuffer> {
  const b64 = base64url.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (base64url.length % 4)) % 4);
  const roh = atob(b64);
  const ergebnis = new Uint8Array(new ArrayBuffer(roh.length));
  for (let i = 0; i < roh.length; i++) ergebnis[i] = roh.charCodeAt(i);
  return ergebnis;
}

function gleicherSchluessel(abo: PushSubscription, schluessel: Uint8Array): boolean {
  const vorhanden = abo.options.applicationServerKey;
  if (!vorhanden) return false;
  const a = new Uint8Array(vorhanden);
  return a.length === schluessel.length && a.every((b, i) => b === schluessel[i]);
}

async function anmeldung(): Promise<ServiceWorkerRegistration> {
  await navigator.serviceWorker.register("/sw.js");
  return navigator.serviceWorker.ready;
}

/** Abo beim Browser holen oder anlegen (mit dem Schlüssel des Servers) und dem Server melden. */
async function abonnieren(): Promise<void> {
  const reg = await anmeldung();
  const schluessel = bytes((await serverSchluessel()).schluessel);
  let abo = await reg.pushManager.getSubscription();
  if (abo && !gleicherSchluessel(abo, schluessel)) {
    await abo.unsubscribe();
    abo = null;
  }
  abo ??= await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: schluessel });
  await aboSetzen(abo.toJSON());
}

/** Im Tippen aufrufen: die Erlaubnis muss die erste Frage nach der Berührung sein (iPhone). Danach wird das Gerät
 *  bei Bedarf angelegt (der gezeigte Ort ist vorgewählt) und das Abo hinterlegt. */
export async function einschalten(ort: string): Promise<"ok" | "verweigert" | "fehler"> {
  const erlaubnis = await Notification.requestPermission();
  if (erlaubnis !== "granted") return "verweigert";
  try {
    await sicheresKonto(ort);
    await abonnieren();
    return "ok";
  } catch {
    return "fehler";
  }
}

export async function ausschalten(): Promise<void> {
  try {
    const reg = await navigator.serviceWorker.getRegistration("/");
    await (await reg?.pushManager.getSubscription())?.unsubscribe();
  } finally {
    await aboLoeschen();
  }
}

/** Beim Start: hat das Gerät Mitteilungen an, Worker und Abo auffrischen (der Browser kann das Abo erneuern). */
export async function abgleichen(): Promise<void> {
  if (!konto.daten?.push || pushLage() !== "geht" || Notification.permission !== "granted") return;
  try {
    await abonnieren();
  } catch {
    // ohne Netz: beim nächsten Start
  }
}
