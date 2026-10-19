// Globale Uhr: aktualisiert sich sekuendlich, geteilt von zeitabhaengigen Kacheln
// (z.B. Sonnenstand "Jetzt"). Eine Instanz statt einem Timer je Kachel.
export const uhr = $state<{ jetzt: Date }>({ jetzt: new Date() });

setInterval(() => {
  uhr.jetzt = new Date();
}, 1000);
