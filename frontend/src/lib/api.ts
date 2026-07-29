// Schlanker API-Helfer. Same-origin ueber den Vite-Proxy (/api -> Backend).
// Das Backend antwortet im Umschlag { data, meta }; hier wird data zurueckgegeben.

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
