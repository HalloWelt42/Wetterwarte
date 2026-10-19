// Eindeutige Kennungen für Kacheln. crypto.randomUUID gibt es nur in sicherem Kontext (https,
// localhost); im Heimnetz über http fehlt es. getRandomValues gibt es überall.
export function uuid(): string {
  const b = crypto.getRandomValues(new Uint8Array(16));
  b[6] = (b[6] & 0x0f) | 0x40; // Version 4
  b[8] = (b[8] & 0x3f) | 0x80; // Variante RFC 4122
  const h = [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

/** Kachel-ID: Typ plus UUID, global eindeutig über alle Profile. */
export function kachelId(typ: string): string {
  return `${typ}-${uuid()}`;
}
