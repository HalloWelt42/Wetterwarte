// Service Worker der Wetterwarte: nur Mitteilungen (docs/WARNUNGEN.md). Er hat bewusst keinen fetch-Handler:
// zwischengespeichert wird nichts, die App kommt nach jedem Ausrollen frisch vom Server. Beim Aktivieren räumt er
// Zwischenspeicher eines alten Workers ab, der auf dieser Adresse noch aus der Zeit vor der Umstellung lag.
self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (ereignis) => {
  ereignis.waitUntil(
    (async () => {
      const namen = await caches.keys();
      await Promise.all(namen.map((name) => caches.delete(name)));
      await self.clients.claim();
    })(),
  );
});

// Nutzlast vom Melder (backend melder.py): titel, text, tag, url, stufe
self.addEventListener("push", (ereignis) => {
  let d = {};
  try {
    d = ereignis.data ? ereignis.data.json() : {};
  } catch {
    d = { text: ereignis.data ? ereignis.data.text() : "" };
  }
  ereignis.waitUntil(
    self.registration.showNotification(d.titel || "Wetterwarte", {
      body: d.text || "",
      tag: d.tag || undefined,
      renotify: Boolean(d.tag), // eine neue Regenstufe ersetzt die alte und meldet sich trotzdem
      icon: "/icon-192.png",
      lang: "de",
      requireInteraction: (d.stufe || 0) >= 3,
      data: { url: d.url || "/telefon" },
    }),
  );
});

// Antippen: ein offenes Fenster der App bekommt das Ziel als Nachricht (kein Neuladen), sonst öffnet sich die App.
self.addEventListener("notificationclick", (ereignis) => {
  ereignis.notification.close();
  const ziel = new URL(ereignis.notification.data?.url || "/telefon", self.location.origin).href;
  ereignis.waitUntil(
    (async () => {
      const fenster = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
      const app = fenster.find((f) => new URL(f.url).pathname.startsWith("/telefon")) || fenster[0];
      if (app) {
        app.postMessage({ art: "mitteilung", url: ziel });
        return app.focus();
      }
      return self.clients.openWindow(ziel);
    })(),
  );
});
