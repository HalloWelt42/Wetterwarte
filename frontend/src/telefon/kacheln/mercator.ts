// Web-Mercator für Kartenkacheln mit 256 Pixeln: Längen- und Breitengrad zu Weltpixeln einer
// Zoomstufe (Ursprung oben links, wie bei den Kachelnummern z/x/y).

export const KACHEL_PX = 256;

export function weltPixel(lon: number, lat: number, zoom: number): { x: number; y: number } {
  const welt = KACHEL_PX * 2 ** zoom;
  const phi = (lat * Math.PI) / 180;
  return {
    x: ((lon + 180) / 360) * welt,
    y: ((1 - Math.log(Math.tan(phi) + 1 / Math.cos(phi)) / Math.PI) / 2) * welt,
  };
}
