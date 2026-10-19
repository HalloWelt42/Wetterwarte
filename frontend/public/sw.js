// Wetterwarte nutzt keinen Service Worker. Diese Datei räumt einen alten Worker ab, der auf
// derselben Adresse noch aus der Zeit vor der Umstellung registriert ist: Der Browser holt bei
// der Aktualisierungsprüfung diese Fassung, sie löscht alle Zwischenspeicher, meldet sich ab und
// lädt offene Fenster neu, damit sie wieder direkt vom Server kommen.
self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (ereignis) => {
  ereignis.waitUntil(
    (async () => {
      const namen = await caches.keys();
      await Promise.all(namen.map((name) => caches.delete(name)));
      await self.registration.unregister();
      const fenster = await self.clients.matchAll({ type: "window" });
      for (const f of fenster) f.navigate(f.url);
    })(),
  );
});
