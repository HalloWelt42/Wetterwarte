// Meteocons (animierte Wetter-Icons) lokal aus dem npm-Paket, ohne CDN.
// Vite bindet die SVG-Dateien als URLs ein; meteocon(name) liefert die URL.
const dateien = import.meta.glob("/node_modules/@meteocons/svg/fill/*.svg", {
  eager: true,
  query: "?url",
  import: "default",
}) as Record<string, string>;

export function meteocon(name: string): string {
  return dateien[`/node_modules/@meteocons/svg/fill/${name}.svg`] ?? "";
}
