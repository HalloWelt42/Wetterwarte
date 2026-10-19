// Schlanker API-Helfer. Same-origin ueber den Vite-Proxy (/api -> Backend).
// Das Backend antwortet im Umschlag { data, meta }; hier wird data zurueckgegeben.

/** Meta eines Datenbereichs: wie verlässlich die Daten sind (siehe backend bereiche.py). */
export interface Meta {
  version: string;
  status?: "ok" | "alt" | "fehlt";
  stand?: string | null;
}

/** Wie hole, aber mit meta (Status und Stand eines Datenbereichs). */
export async function holeMitMeta<T>(pfad: string, signal?: AbortSignal): Promise<{ data: T; meta: Meta }> {
  const antwort = await fetch(`/api/v1${pfad}`, { signal });
  if (!antwort.ok) throw new Error(`GET ${pfad}: ${antwort.status}`);
  return (await antwort.json()) as { data: T; meta: Meta };
}

export async function hole<T>(pfad: string): Promise<T> {
  const antwort = await fetch(`/api/v1${pfad}`);
  if (!antwort.ok) throw new Error(`GET ${pfad}: ${antwort.status}`);
  const inhalt = await antwort.json();
  return inhalt.data as T;
}

export async function sende<T>(
  pfad: string,
  methode: "POST" | "PUT" | "DELETE",
  koerper?: unknown,
): Promise<T> {
  const antwort = await fetch(`/api/v1${pfad}`, {
    method: methode,
    headers: { "Content-Type": "application/json" },
    body: koerper === undefined ? undefined : JSON.stringify(koerper),
  });
  if (!antwort.ok) throw new Error(`${methode} ${pfad}: ${antwort.status}`);
  const inhalt = await antwort.json();
  return inhalt.data as T;
}
