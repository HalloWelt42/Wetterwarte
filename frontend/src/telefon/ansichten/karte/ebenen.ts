// Quellen und Ebenen der Telefonkarte. Nur Typen aus MapLibre, die Bibliothek selbst lädt Karte.svelte
// nach. Farben kommen aus den CSS-Variablen der Ansicht (leseFarben), damit der Nachtbetrieb mitzieht.
// Reihenfolge von unten nach oben: Grundkarte, Detailkarte, Regenradar, Warnungen, Wind, Blitze.
import type { ExpressionSpecification, GeoJSONSource, ImageSource, Map as Karte, RasterTileSource } from "maplibre-gl";
import type { KartenWahl } from "./wahl.svelte";

export type Ecken = [[number, number], [number, number], [number, number], [number, number]];

const LEER: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [] };

export const grundKacheln = (dunkel: boolean): string[] => [`/kachel/${dunkel ? "dark" : "light"}/{z}/{x}/{y}`];
const DETAIL_KACHELN = ["/kachel/voyager/{z}/{x}/{y}"];

/** Ebenen je Schalter (Grundkarte und Detailkarte schalten anders, siehe setzeGrund und setzeDetail). */
export const EBENEN_VON = {
  warnungen: ["warn-flaeche", "warn-linie"],
  wind: ["wind"],
  blitze: ["blitze"],
  radar: ["radar"],
} as const;

export interface Farben {
  text: string;
  grund: string;
  warn: [string, string, string, string];
  wind: [string, string, string, string, string]; // Stufen 0 bis 4
}

export function leseFarben(el: HTMLElement): Farben {
  const s = getComputedStyle(el);
  const v = (name: string) => s.getPropertyValue(name).trim();
  return {
    text: v("--text"),
    grund: v("--grund"),
    warn: [v("--w1"), v("--w2"), v("--w3"), v("--w4")],
    wind: [v("--text-3"), v("--t-kalt"), v("--t-kuehl"), v("--t-heiss"), v("--t-extrem")],
  };
}

// Amtliche Stufen der Warnpolygone (Eigenschaft SEVERITY) auf die Warnstufen 1 bis 4.
const warnFarbe = (f: Farben) =>
  ["match", ["get", "SEVERITY"], "Minor", f.warn[0], "Moderate", f.warn[1], "Severe", f.warn[2], "Extreme", f.warn[3], f.warn[0]] as unknown as ExpressionSpecification;

// Blitze nach Alter in Minuten: frisch hell, dann über die Warnfarben abklingend.
const blitzFarbe = (f: Farben) =>
  ["interpolate", ["linear"], ["get", "min"], 0, f.text, 5, f.warn[0], 20, f.warn[1], 60, f.warn[2]] as unknown as ExpressionSpecification;

/** Windpfeil als Bild (zeigt in die Richtung, in die der Wind weht, nach dem Drehen um 180 Grad). */
function windPfeil(farbe: string, rand: string): ImageData {
  const s = 26;
  const c = document.createElement("canvas");
  c.width = s;
  c.height = s;
  const x = c.getContext("2d")!;
  x.translate(s / 2, s / 2);
  x.lineCap = "round";
  x.lineJoin = "round";
  const pfeil = () => {
    x.beginPath();
    x.moveTo(0, 8);
    x.lineTo(0, -8);
    x.moveTo(-4, -3);
    x.lineTo(0, -9);
    x.lineTo(4, -3);
    x.stroke();
  };
  x.globalAlpha = 0.6;
  x.strokeStyle = rand;
  x.lineWidth = 3.6;
  pfeil();
  x.globalAlpha = 1;
  x.strokeStyle = farbe;
  x.lineWidth = 2;
  pfeil();
  return x.getImageData(0, 0, s, s);
}

function windBilder(map: Karte, f: Farben): void {
  f.wind.forEach((farbe, i) => {
    const bild = windPfeil(farbe, f.grund);
    if (map.hasImage(`wind${i}`)) map.updateImage(`wind${i}`, bild);
    else map.addImage(`wind${i}`, bild);
  });
}

const sicht = (an: boolean) => (an ? "visible" : "none");

/** Alle Ebenen außer dem Regenradar anlegen (nach "load"; das Radar folgt mit dem ersten Bild). */
export function legeEbenenAn(map: Karte, wahl: KartenWahl, f: Farben): void {
  map.addSource("detail", { type: "raster", tiles: DETAIL_KACHELN, tileSize: 256 });
  map.addLayer({ id: "detail", type: "raster", source: "detail", layout: { visibility: sicht(wahl.detail) }, paint: detailFarbe(wahl.dunkel) });

  map.addSource("warnungen", { type: "geojson", data: LEER });
  map.addLayer({ id: "warn-flaeche", type: "fill", source: "warnungen", layout: { visibility: sicht(wahl.warnungen) }, paint: { "fill-color": warnFarbe(f), "fill-opacity": 0.25 } });
  map.addLayer({ id: "warn-linie", type: "line", source: "warnungen", layout: { visibility: sicht(wahl.warnungen) }, paint: { "line-color": warnFarbe(f), "line-width": 1.4, "line-opacity": 0.85 } });

  windBilder(map, f);
  map.addSource("wind", { type: "geojson", data: LEER });
  map.addLayer({
    id: "wind",
    type: "symbol",
    source: "wind",
    layout: {
      "icon-image": ["match", ["get", "stufe"], 0, "wind0", 1, "wind1", 2, "wind2", 3, "wind3", 4, "wind4", "wind1"],
      "icon-rotate": ["+", ["get", "richtung"], 180],
      "icon-rotation-alignment": "map",
      "icon-size": ["interpolate", ["linear"], ["get", "tempo"], 0, 0.6, 45, 1.2],
      "icon-allow-overlap": true,
      "icon-ignore-placement": true,
      visibility: sicht(wahl.wind),
    },
  });

  map.addSource("blitze", { type: "geojson", data: LEER });
  map.addLayer({
    id: "blitze",
    type: "circle",
    source: "blitze",
    layout: { visibility: sicht(wahl.blitze) },
    paint: {
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 4, 2.5, 9, 5],
      "circle-color": blitzFarbe(f),
      "circle-opacity": 0.9,
      "circle-stroke-color": f.grund,
      "circle-stroke-width": 0.6,
    },
  });
}

/** Farben neu setzen (Wechsel zwischen Tag und Nachtbetrieb). */
export function faerbe(map: Karte, f: Farben): void {
  map.setPaintProperty("warn-flaeche", "fill-color", warnFarbe(f));
  map.setPaintProperty("warn-linie", "line-color", warnFarbe(f));
  map.setPaintProperty("blitze", "circle-color", blitzFarbe(f));
  map.setPaintProperty("blitze", "circle-stroke-color", f.grund);
  windBilder(map, f);
}

export function zeige(map: Karte, ids: readonly string[], an: boolean): void {
  for (const id of ids) if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", sicht(an));
}

export function setzeDaten(map: Karte, quelle: string, daten: GeoJSON.FeatureCollection): void {
  (map.getSource(quelle) as GeoJSONSource | undefined)?.setData(daten);
}

export function setzeGrund(map: Karte, dunkel: boolean): void {
  (map.getSource("grund") as RasterTileSource | undefined)?.setTiles(grundKacheln(dunkel));
}

// Detailkarte mit Deckkraft über der Grundkarte. Über der dunklen Grundkarte umgekehrt und grau, damit
// sie dunkel bleibt und Beschriftung und Straßen hell erscheinen.
function detailFarbe(dunkel: boolean) {
  return dunkel
    ? { "raster-opacity": 0.75, "raster-saturation": -1, "raster-brightness-min": 1, "raster-brightness-max": 0 }
    : { "raster-opacity": 0.7, "raster-saturation": 0, "raster-brightness-min": 0, "raster-brightness-max": 1 };
}

export function setzeDetail(map: Karte, an: boolean, dunkel: boolean): void {
  if (!map.getLayer("detail")) return;
  for (const [k, v] of Object.entries(detailFarbe(dunkel))) map.setPaintProperty("detail", k, v);
  zeige(map, ["detail"], an);
}

/** Regenradar als Bild-Ebene über der Detailkarte; beim ersten Bild angelegt, danach nur das Bild getauscht. */
export function radarBild(map: Karte, url: string, ecken: Ecken, an: boolean): void {
  const quelle = map.getSource("radar") as ImageSource | undefined;
  if (quelle) {
    if (JSON.stringify(quelle.coordinates) !== JSON.stringify(ecken)) quelle.setCoordinates(ecken);
    quelle.updateImage({ url });
    return;
  }
  map.addSource("radar", { type: "image", url, coordinates: ecken });
  map.addLayer(
    { id: "radar", type: "raster", source: "radar", layout: { visibility: sicht(an) }, paint: { "raster-opacity": 0.72, "raster-fade-duration": 0 } },
    map.getLayer("warn-flaeche") ? "warn-flaeche" : undefined,
  );
}
