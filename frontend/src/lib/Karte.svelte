<script lang="ts">
  import { onMount, untrack } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";
  import HilfeLink from "./HilfeLink.svelte";
  import { karteEinst, kachelUrl, BLITZE_LIMIT_MAX } from "./karteEinst.svelte";

  let kartenEl: HTMLDivElement;
  let map: maplibregl.Map | undefined;
  let ortMarker: maplibregl.Marker | undefined;

  // Overlay-Namen fuer das Ebenen-Panel.
  const overlayNamen: [string, string][] = [
    ["blitze", "Blitze"],
    ["warnungen", "Warnungen"],
    ["radar", "Radar"],
    ["wind", "Wind"],
    ["nowcast", "Niederschlag-Nowcast"],
    ["temperatur", "Temperatur"],
  ];

  const kacheln = kachelUrl;

  function aktiverOrt(): [number, number] {
    const o = orteState.liste.find((x) => x.slug === wetter.slug);
    return o ? [o.lon, o.lat] : [10.45, 51.16]; // Fallback: ungefaehre Mitte Deutschlands
  }

  onMount(() => {
    map = new maplibregl.Map({
      container: kartenEl,
      style: {
        version: 8,
        sources: {
          grund: {
            type: "raster",
            tiles: kacheln(karteEinst.basis),
            tileSize: 256,
            attribution: "© OpenStreetMap, © CARTO",
          },
        },
        layers: [{ id: "grund", type: "raster", source: "grund" }],
      },
      center: aktiverOrt(),
      zoom: 7,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    // Pinnnadel am aktiven Ort (Heimat).
    ortMarker = new maplibregl.Marker({ color: "#2f7ce0" }).setLngLat(aktiverOrt()).addTo(map);
    map.on("load", () => {
      baueOrientierung();
      baueWarnEbene();
      baueBlitzEbene();
      baueWellenEbene();
      void ladeBlitze();
    });
    map.on("moveend", () => void ladeBlitze());
    map.on("mousemove", beiMausTemp);
    map.on("mouseout", () => (tempHover = null));
    blitzTimer = setInterval(() => void ladeBlitze(), 30000);
    return () => {
      clearInterval(blitzTimer);
      stoppeRadar();
      if (radarRahmenTimer) clearInterval(radarRahmenTimer);
      if (warnTimer) clearInterval(warnTimer);
      if (gitterTimer) clearInterval(gitterTimer);
      ortMarker?.remove();
      map?.remove();
    };
  });

  // --- Orientierungs-Overlay (voyager: Beschriftung, Grenzen, Strassen) ---
  function baueOrientierung(): void {
    if (!map || map.getSource("beschriftung")) return;
    map.addSource("beschriftung", { type: "raster", tiles: ["/kachel/voyager/{z}/{x}/{y}"], tileSize: 256 });
    map.addLayer({
      id: "beschriftung",
      type: "raster",
      source: "beschriftung",
      layout: { visibility: karteEinst.orientierung ? "visible" : "none" },
      paint: { "raster-opacity": karteEinst.basis === "satellit" ? 0.5 : 0.7 },
    });
  }
  // Ein-/Ausblenden.
  $effect(() => {
    const an = karteEinst.orientierung;
    if (map?.getLayer("beschriftung")) map.setLayoutProperty("beschriftung", "visibility", an ? "visible" : "none");
  });
  // Deckkraft je Basiskarte (Satellitenbild soll durchscheinen).
  $effect(() => {
    const b = karteEinst.basis;
    if (map?.getLayer("beschriftung")) map.setPaintProperty("beschriftung", "raster-opacity", b === "satellit" ? 0.5 : 0.7);
  });

  // --- Amtliche Warnungen (DWD-Polygone) ---
  let warnAnzahl = $state(0);
  let warnTimer: ReturnType<typeof setInterval> | undefined;
  // Farbe nach Warnstufe (DWD: gelb/orange/rot/violett).
  const WARN_FARBE = [
    "match",
    ["get", "SEVERITY"],
    "Minor",
    "#ffd400",
    "Moderate",
    "#ff9800",
    "Severe",
    "#e53935",
    "Extreme",
    "#8e24aa",
    "#ffd400",
  ] as unknown as maplibregl.ExpressionSpecification;

  function baueWarnEbene(): void {
    if (!map || map.getSource("warnungen")) return;
    const sicht = karteEinst.overlays.warnungen ? "visible" : "none";
    const drueber = map.getLayer("beschriftung") ? "beschriftung" : undefined;
    map.addSource("warnungen", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    map.addLayer(
      {
        id: "warn-fill",
        type: "fill",
        source: "warnungen",
        layout: { visibility: sicht },
        paint: { "fill-color": WARN_FARBE, "fill-opacity": 0.25 },
      },
      drueber,
    );
    map.addLayer(
      {
        id: "warn-linie",
        type: "line",
        source: "warnungen",
        layout: { visibility: sicht },
        paint: { "line-color": WARN_FARBE, "line-width": 1.4, "line-opacity": 0.85 },
      },
      drueber,
    );
    map.on("click", "warn-fill", (e) => {
      if (!map) return;
      // Alle Warnungen am Klickpunkt sammeln (ueberlappende Flaechen), nicht nur die oberste.
      const treffer = map.queryRenderedFeatures(e.point, { layers: ["warn-fill"] });
      if (!treffer.length) return;
      const gesehen = new Set<string>();
      const bloecke: string[] = [];
      for (const f of treffer) {
        const p = (f.properties ?? {}) as Record<string, string>;
        const key = `${p.EVENT}|${p.HEADLINE}|${p.EXPIRES}`;
        if (gesehen.has(key)) continue;
        gesehen.add(key);
        const bis = p.EXPIRES
          ? new Date(p.EXPIRES).toLocaleString("de-DE", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })
          : "";
        bloecke.push(
          `<div class="warn-pop"><strong>${p.EVENT ?? "Warnung"}</strong>${p.HEADLINE ? `<br>${p.HEADLINE}` : ""}${bis ? `<br><small>gültig bis ${bis} Uhr</small>` : ""}</div>`,
        );
      }
      new maplibregl.Popup({ closeButton: true, maxWidth: "280px" })
        .setLngLat(e.lngLat)
        .setHTML(bloecke.join('<hr class="warn-pop-tr" />'))
        .addTo(map);
    });
    map.on("mouseenter", "warn-fill", () => map && (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", "warn-fill", () => map && (map.getCanvas().style.cursor = ""));
    // Ist das Overlay schon beim Start aktiv, gleich befuellen (die Quelle existiert jetzt).
    if (karteEinst.overlays.warnungen) void ladeWarnungen();
  }

  async function ladeWarnungen(): Promise<void> {
    if (!map) return;
    try {
      const d = (await (await fetch("/api/v1/wetter/warnkarte")).json()).data as GeoJSON.FeatureCollection;
      (map.getSource("warnungen") as maplibregl.GeoJSONSource | undefined)?.setData(d);
      warnAnzahl = d.features?.length ?? 0;
    } catch {
      // still ignorieren
    }
  }

  // Warn-Overlay an den Schalter koppeln (alle 3 min auffrischen).
  $effect(() => {
    const an = karteEinst.overlays.warnungen;
    const sicht = an ? "visible" : "none";
    if (map?.getLayer("warn-fill")) map.setLayoutProperty("warn-fill", "visibility", sicht);
    if (map?.getLayer("warn-linie")) map.setLayoutProperty("warn-linie", "visibility", sicht);
    if (an) {
      void ladeWarnungen();
      if (!warnTimer) warnTimer = setInterval(() => void ladeWarnungen(), 180000);
    } else {
      if (warnTimer) clearInterval(warnTimer);
      warnTimer = undefined;
    }
  });

  // --- Temperatur-Feld + Wind-Pfeile (Open-Meteo-Gitter, gemeinsamer Abruf) ---
  const TEMP_COORDS: [[number, number], [number, number], [number, number], [number, number]] = [
    [5.8, 55.1],
    [15.1, 55.1],
    [15.1, 47.2],
    [5.8, 47.2],
  ];
  let tempGebaut = false;
  let windGebaut = false;
  let windBilder = false;
  let gitterTimer: ReturnType<typeof setInterval> | undefined;
  let tempVersion = 0;
  const tempUrl = () => `/api/v1/wetter/temperatur.png?v=${tempVersion}`;
  const WIND_FARBEN = ["#9aa5b1", "#38bdf8", "#34d399", "#fb923c", "#ef4444"];

  function windPfeilBild(farbe: string): ImageData {
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
    x.strokeStyle = "rgba(0,0,0,0.4)";
    x.lineWidth = 3.4;
    pfeil();
    x.strokeStyle = farbe;
    x.lineWidth = 1.8;
    pfeil();
    return x.getImageData(0, 0, s, s);
  }

  function windBilderLaden(): void {
    if (!map || windBilder) return;
    WIND_FARBEN.forEach((f, i) => {
      const id = `wind${i}`;
      if (!map!.hasImage(id)) map!.addImage(id, windPfeilBild(f));
    });
    windBilder = true;
  }

  function baueTempEbene(): void {
    if (!map || map.getSource("temperatur")) return;
    tempVersion++;
    map.addSource("temperatur", { type: "image", url: tempUrl(), coordinates: TEMP_COORDS });
    const drueber = ["warn-fill", "radar", "beschriftung"].find((id) => map!.getLayer(id));
    map.addLayer(
      {
        id: "temperatur",
        type: "raster",
        source: "temperatur",
        layout: { visibility: karteEinst.overlays.temperatur ? "visible" : "none" },
        paint: { "raster-opacity": 1, "raster-fade-duration": 0, "raster-resampling": "linear" },
      },
      drueber,
    );
    tempGebaut = true;
  }

  function baueWindEbene(): void {
    if (!map || map.getSource("wind")) return;
    windBilderLaden();
    map.addSource("wind", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    map.addLayer({
      id: "wind",
      type: "symbol",
      source: "wind",
      layout: {
        "icon-image": ["match", ["get", "stufe"], 0, "wind0", 1, "wind1", 2, "wind2", 3, "wind3", 4, "wind4", "wind1"],
        "icon-rotate": ["+", ["get", "richtung"], 180],
        "icon-rotation-alignment": "map",
        "icon-size": ["interpolate", ["linear"], ["get", "tempo"], 0, 0.5, 45, 1.15],
        "icon-allow-overlap": true,
        "icon-ignore-placement": true,
        visibility: karteEinst.overlays.wind ? "visible" : "none",
      },
    });
    map.on("click", "wind", (e) => {
      const p = e.features?.[0]?.properties as Record<string, number> | undefined;
      if (!p || !map) return;
      const ri = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"][Math.round((p.richtung ?? 0) / 45) % 8];
      new maplibregl.Popup({ closeButton: true, maxWidth: "200px" })
        .setLngLat(e.lngLat)
        .setHTML(`<strong>${p.tempo} km/h</strong><br><small>aus ${ri}</small>`)
        .addTo(map);
    });
    windGebaut = true;
  }

  async function ladeGitter(): Promise<void> {
    if (!map) return;
    try {
      const d = (await (await fetch("/api/v1/wetter/kartendaten")).json()).data as {
        wind: GeoJSON.FeatureCollection;
        temp: TempGitter;
      };
      (map.getSource("wind") as maplibregl.GeoJSONSource | undefined)?.setData(d.wind);
      tempGitter = d.temp;
      tempVersion++;
      (map.getSource("temperatur") as maplibregl.ImageSource | undefined)?.updateImage({ url: tempUrl() });
    } catch {
      // still ignorieren
    }
  }

  // Temperatur an einer Position bilinear aus dem Gitter interpolieren (fuer den Hover).
  interface TempGitter {
    lons: number[];
    lats: number[];
    werte: number[][];
  }
  let tempGitter: TempGitter | null = null;
  let tempHover = $state<{ x: number; y: number; wert: number } | null>(null);

  function tempBei(lon: number, lat: number): number | null {
    const t = tempGitter;
    if (!t) return null;
    const { lons, lats, werte } = t;
    if (lon < lons[0] || lon > lons[lons.length - 1] || lat < lats[0] || lat > lats[lats.length - 1]) return null;
    let j = 0;
    while (j < lons.length - 2 && lons[j + 1] < lon) j++;
    let i = 0;
    while (i < lats.length - 2 && lats[i + 1] < lat) i++;
    const fx = (lon - lons[j]) / (lons[j + 1] - lons[j]);
    const fy = (lat - lats[i]) / (lats[i + 1] - lats[i]);
    return (
      werte[i][j] * (1 - fx) * (1 - fy) +
      werte[i][j + 1] * fx * (1 - fy) +
      werte[i + 1][j] * (1 - fx) * fy +
      werte[i + 1][j + 1] * fx * fy
    );
  }

  function beiMausTemp(e: maplibregl.MapMouseEvent): void {
    if (!karteEinst.overlays.temperatur || !tempGitter) {
      if (tempHover) tempHover = null;
      return;
    }
    const w = tempBei(e.lngLat.lng, e.lngLat.lat);
    tempHover = w === null ? null : { x: e.point.x, y: e.point.y, wert: w };
  }

  function gitterTaktSichern(): void {
    const aktiv = karteEinst.overlays.temperatur || karteEinst.overlays.wind;
    if (aktiv && !gitterTimer) gitterTimer = setInterval(() => void ladeGitter(), 600000);
    if (!aktiv && gitterTimer) {
      clearInterval(gitterTimer);
      gitterTimer = undefined;
    }
  }

  // Temperatur-Feld an den Schalter koppeln.
  $effect(() => {
    const an = karteEinst.overlays.temperatur;
    if (an && !tempGebaut) {
      baueTempEbene();
      void ladeGitter();
    } else if (map?.getLayer("temperatur")) {
      map.setLayoutProperty("temperatur", "visibility", an ? "visible" : "none");
    }
    gitterTaktSichern();
  });

  // Wind-Pfeile an den Schalter koppeln.
  $effect(() => {
    const an = karteEinst.overlays.wind;
    if (an && !windGebaut) {
      baueWindEbene();
      void ladeGitter();
    } else if (map?.getLayer("wind")) {
      map.setLayoutProperty("wind", "visibility", an ? "visible" : "none");
    }
    gitterTaktSichern();
  });

  // --- Blitze (Live-Ebene aus dem lightningmap-Dienst) ---
  let blitzAnzahl = $state(0);
  let blitzTimer: ReturnType<typeof setInterval> | undefined;

  function baueBlitzEbene(): void {
    if (!map || map.getSource("blitze")) return;
    map.addSource("blitze", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    map.addLayer({
      id: "blitze",
      type: "circle",
      source: "blitze",
      layout: { visibility: karteEinst.overlays.blitze ? "visible" : "none" },
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 4, 2.5, 9, 5],
        // Farbe nach Alter in Minuten: frisch weiss -> gelb -> orange -> dunkel.
        "circle-color": ["interpolate", ["linear"], ["get", "min"], 0, "#ffffff", 5, "#ffd400", 20, "#ff7b00", 60, "#b23a00"],
        "circle-opacity": 0.9,
        "circle-stroke-color": "#ffffff",
        "circle-stroke-width": 0.4,
      },
    });
  }

  async function ladeBlitze(): Promise<void> {
    if (!map) return;
    const b = map.getBounds();
    const url = `/blitze?north=${b.getNorth().toFixed(2)}&south=${b.getSouth().toFixed(2)}&east=${b.getEast().toFixed(2)}&west=${b.getWest().toFixed(2)}&since=1&limit=${karteEinst.blitzeLimit}`;
    try {
      const antwort = await fetch(url);
      const daten = await antwort.json();
      const strikes: { t: number; lat: number; lon: number }[] = daten.strikes ?? [];
      const jetzt = Date.now();
      const fc = {
        type: "FeatureCollection" as const,
        features: strikes.map((s) => ({
          type: "Feature" as const,
          geometry: { type: "Point" as const, coordinates: [s.lon, s.lat] },
          properties: { min: Math.max(0, (jetzt - s.t) / 60000) },
        })),
      };
      (map.getSource("blitze") as maplibregl.GeoJSONSource | undefined)?.setData(fc);
      blitzAnzahl = strikes.length;
    } catch {
      // still ignorieren
    }
  }

  // Blitz-Ebene an den Schalter koppeln.
  $effect(() => {
    const an = karteEinst.overlays.blitze;
    if (map?.getLayer("blitze")) map.setLayoutProperty("blitze", "visibility", an ? "visible" : "none");
  });

  // Blitze bei geaenderter Mengen-Grenze sofort neu laden (nicht erst beim naechsten Takt).
  $effect(() => {
    void karteEinst.blitzeLimit;
    if (karteEinst.overlays.blitze) void ladeBlitze();
  });

  // --- Regen-Radar (eigenes DWD-RADOLAN: gemessen + Nowcast, als Bild-Overlay) ---
  interface RadarFrame {
    id: string;
    zeit: string;
    offset: number;
    art: "gemessen" | "vorhersage";
  }
  let radarFrames = $state<RadarFrame[]>([]);
  let radarIdx = $state(0);
  let radarSpielt = $state(false);
  let radarLaedt = $state(false);
  let radarStand = $state("");
  let radarGebaut = false;
  let radarTimer: ReturnType<typeof setInterval> | undefined;
  let radarRahmenTimer: ReturnType<typeof setInterval> | undefined;
  const radarUrl = (id: string) => `/api/v1/radar/bild/${id}.png`;

  // Frame-Liste periodisch auffrischen: das Backend rotiert die Vorhersage-Frames
  // (neues DWD-Archiv alle paar Minuten). Ohne Auffrischung zeigt der Abspieler auf
  // inzwischen entfernte Frames -> 404. Die aktuelle Position wird ueber die ID gehalten.
  async function frischeRahmen(): Promise<void> {
    try {
      const antwort = await fetch("/api/v1/radar/rahmen");
      const d = (await antwort.json()).data as { frames: RadarFrame[]; stand: string };
      if (!d.frames?.length) return;
      const altId = radarFrames[radarIdx]?.id;
      radarFrames = d.frames;
      radarStand = d.stand ?? "";
      for (const f of d.frames) new Image().src = radarUrl(f.id);
      const neu = d.frames.findIndex((f) => f.id === altId);
      radarIdx = neu >= 0 ? neu : Math.min(radarIdx, d.frames.length - 1);
    } catch {
      // still ignorieren
    }
  }

  async function ladeRadar(): Promise<void> {
    if (radarLaedt) return;
    radarLaedt = true;
    try {
      const antwort = await fetch("/api/v1/radar/rahmen");
      const d = (await antwort.json()).data as { coords: [number, number][]; frames: RadarFrame[]; stand: string };
      if (!d.frames?.length) return;
      radarFrames = d.frames;
      radarStand = d.stand ?? "";
      // Bilder vorladen, damit der Abspieler nicht flackert.
      for (const f of d.frames) new Image().src = radarUrl(f.id);
      // Startbild = "jetzt" (letzter gemessener Frame).
      const jetztI = d.frames.map((f) => f.art).lastIndexOf("gemessen");
      const startI = jetztI >= 0 ? jetztI : 0;
      if (map) {
        const koord = d.coords as [[number, number], [number, number], [number, number], [number, number]];
        if (!radarGebaut) {
          // Quelle gleich mit dem Startbild bauen (kein sofortiges updateImage -> kein Abbruch).
          map.addSource("radar", { type: "image", url: radarUrl(d.frames[startI].id), coordinates: koord });
          const drueber = map.getLayer("beschriftung") ? "beschriftung" : map.getLayer("blitze") ? "blitze" : undefined;
          map.addLayer(
            { id: "radar", type: "raster", source: "radar", paint: { "raster-opacity": 0.72, "raster-fade-duration": 0 } },
            drueber,
          );
          radarGebaut = true;
        } else {
          (map.getSource("radar") as maplibregl.ImageSource | undefined)?.setCoordinates(koord);
          zeigeRadar(startI);
        }
      }
      radarIdx = startI;
      starteRadar();
    } catch {
      // still ignorieren - alter Stand bleibt
    } finally {
      radarLaedt = false;
    }
  }

  function zeigeRadar(i: number): void {
    const f = radarFrames[i];
    if (!f || !map?.getSource("radar")) return;
    (map.getSource("radar") as maplibregl.ImageSource).updateImage({ url: radarUrl(f.id) });
  }

  function starteRadar(): void {
    if (radarTimer || radarFrames.length < 2) return;
    radarSpielt = true;
    radarTimer = setInterval(() => {
      // am Ende kurz halten, dann von vorn.
      const naechster = radarIdx + 1 >= radarFrames.length ? 0 : radarIdx + 1;
      radarIdx = naechster;
      zeigeRadar(naechster);
    }, 450);
  }

  function stoppeRadar(): void {
    if (radarTimer) clearInterval(radarTimer);
    radarTimer = undefined;
    radarSpielt = false;
  }

  function radarAbspielen(): void {
    if (radarSpielt) stoppeRadar();
    else starteRadar();
  }

  function radarSchieben(i: number): void {
    stoppeRadar();
    radarIdx = i;
    zeigeRadar(i);
  }

  // Radar an den Schalter koppeln: einschalten laedt + spielt, ausschalten blendet aus.
  $effect(() => {
    const an = karteEinst.overlays.radar;
    if (an) {
      if (!radarGebaut) void ladeRadar();
      else {
        if (map?.getLayer("radar")) map.setLayoutProperty("radar", "visibility", "visible");
        // untrack: sonst wuerde Pause (radarSpielt=false) diesen Effect neu ausloesen
        // und die Wiedergabe sofort wieder starten - die Steuerung waere kaputt.
        untrack(() => {
          if (!radarSpielt) starteRadar();
        });
      }
      if (!radarRahmenTimer) radarRahmenTimer = setInterval(() => void frischeRahmen(), 180000);
    } else {
      stoppeRadar();
      if (radarRahmenTimer) clearInterval(radarRahmenTimer);
      radarRahmenTimer = undefined;
      if (map?.getLayer("radar")) map.setLayoutProperty("radar", "visibility", "none");
    }
  });

  // Beschriftung des aktuellen Frames (Ortszeit Deutschland).
  const radarAktiv = $derived(radarFrames[radarIdx]);
  const radarZeitLabel = $derived.by(() => {
    const f = radarAktiv;
    if (!f) return "";
    const t = new Date(f.zeit).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Berlin" });
    if (f.offset === 0) return `${t} Uhr - jetzt`;
    if (f.offset < 0) return `${t} Uhr - vor ${-f.offset} Min`;
    return `${t} Uhr - Vorhersage +${f.offset} Min`;
  });

  // --- Optionale Blitz-Wellen-Simulation (live via WebSocket) ---
  // Jeder eingehende Blitz wirft einen Ring, der waechst und ausblendet
  // (wie eine Schallwelle). Zeitkritisch -> Live-Feed statt Polling.
  let ws: WebSocket | undefined;
  let wellen: { lon: number; lat: number; start: number }[] = [];
  let animLaeuft = false;
  const WELLE_MS = 1600; // Dauer der Schallwelle (wachsender Ring)
  const FLASH_MS = 260; // Dauer des hellen Aufblitzens am Punkt

  function imBlick(lon: number, lat: number): boolean {
    const b = map?.getBounds();
    return !!b && lon >= b.getWest() && lon <= b.getEast() && lat >= b.getSouth() && lat <= b.getNorth();
  }

  function baueWellenEbene(): void {
    if (!map || map.getSource("wellen")) return;
    map.addSource("wellen", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    // Schallausbreitung: wandernder Ring, der waechst und ausblendet; die Front
    // ist anfangs dick und wird duenner - wie eine sich loesende Welle.
    map.addLayer({
      id: "wellen-ring",
      type: "circle",
      source: "wellen",
      paint: {
        "circle-radius": ["get", "r"],
        "circle-color": "#ffffff",
        "circle-opacity": 0,
        "circle-stroke-color": "#ffe680",
        "circle-stroke-width": ["get", "sw"],
        "circle-stroke-opacity": ["get", "o"],
      },
    });
    // Kurzes, helles Aufblitzen genau am Einschlagpunkt (schnell verglimmend).
    map.addLayer({
      id: "wellen-blitz",
      type: "circle",
      source: "wellen",
      paint: {
        "circle-radius": ["get", "fr"],
        "circle-color": "#ffffff",
        "circle-opacity": ["get", "fo"],
        "circle-blur": 0.5,
      },
    });
  }

  function animiere(): void {
    const quelle = map?.getSource("wellen") as maplibregl.GeoJSONSource | undefined;
    if (!quelle) {
      animLaeuft = false;
      return;
    }
    const jetzt = performance.now();
    wellen = wellen.filter((w) => jetzt - w.start < WELLE_MS);
    quelle.setData({
      type: "FeatureCollection",
      features: wellen.map((w) => {
        const alter = jetzt - w.start;
        const p = alter / WELLE_MS; // Ring: 0 (frisch) .. 1 (verklungen)
        const pf = Math.min(1, alter / FLASH_MS); // Blitz: 0 .. 1
        return {
          type: "Feature" as const,
          geometry: { type: "Point" as const, coordinates: [w.lon, w.lat] },
          properties: {
            // Schallwelle: waechst weit auf, Front wird duenner und blasser.
            r: 4 + p * 40,
            o: 0.85 * (1 - p),
            sw: 0.5 + (1 - p) * 3,
            // Aufblitzen: heller Kern, waechst minimal, verglimmt in FLASH_MS.
            fr: 5 + pf * 5,
            fo: alter < FLASH_MS ? 0.95 * (1 - pf) : 0,
          },
        };
      }),
    });
    if (wellen.length > 0) requestAnimationFrame(animiere);
    else animLaeuft = false;
  }

  function neueWelle(lon: number, lat: number): void {
    wellen.push({ lon, lat, start: performance.now() });
    if (wellen.length > 400) wellen.shift();
    if (!animLaeuft) {
      animLaeuft = true;
      requestAnimationFrame(animiere);
    }
  }

  function verbindeWs(): void {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${proto}://${location.host}/ws-blitze`);
    ws.onmessage = (e) => {
      try {
        const m = JSON.parse(e.data);
        if (m.type === "strike" && m.data && imBlick(m.data.lon, m.data.lat)) neueWelle(m.data.lon, m.data.lat);
      } catch {
        // ungueltige Nachricht ignorieren
      }
    };
    ws.onclose = () => {
      ws = undefined;
    };
    ws.onerror = () => ws?.close();
  }

  function trenneWs(): void {
    ws?.close();
    ws = undefined;
    wellen = [];
    (map?.getSource("wellen") as maplibregl.GeoJSONSource | undefined)?.setData({ type: "FeatureCollection", features: [] });
  }

  $effect(() => {
    if (!karteEinst.simulation) return;
    verbindeWs();
    return () => trenneWs();
  });

  // Basiskarte umschalten (Kacheln der vorhandenen Quelle austauschen).
  $effect(() => {
    const b = karteEinst.basis;
    const quelle = map?.getSource("grund") as maplibregl.RasterTileSource | undefined;
    // setTiles ersetzt die Kachel-URLs ohne Neuaufbau der Karte.
    (quelle as unknown as { setTiles?: (t: string[]) => void })?.setTiles?.(kacheln(b));
  });

  // Karte auf den aktiven Ort schwenken und die Pinnnadel mitfuehren.
  $effect(() => {
    void wetter.slug;
    void orteState.liste.length; // auch auf spaeter geladene Ortsliste reagieren
    const ziel = aktiverOrt();
    ortMarker?.setLngLat(ziel);
    map?.flyTo({ center: ziel, zoom: 7, duration: 800 });
  });
</script>

<section class="inhalt">
  <div style="flex: 1; position: relative; margin: var(--a4); min-height: 0;">
    <div bind:this={kartenEl} style="position: absolute; inset: 0; border-radius: var(--r2); overflow: hidden;"></div>

    <!-- Ebenen-Panel -->
    <div class="panel" style="position: absolute; left: var(--a4); top: var(--a4); width: 236px; z-index: 2; box-shadow: var(--schatten-2);">
      <h2><i class="fa-solid fa-layer-group"></i> Ebenen <span style="margin-left: auto"><HilfeLink topic="karte" /></span></h2>
      <div class="kat-gruppe">Basiskarte</div>
      <div class="segment tabgruppe" style="margin-bottom: var(--a2);">
        <button class:aktiv={karteEinst.basis === "hell"} onclick={() => (karteEinst.basis = "hell")}>Hell</button>
        <button class:aktiv={karteEinst.basis === "dunkel"} onclick={() => (karteEinst.basis = "dunkel")}>Dunkel</button>
        <button class:aktiv={karteEinst.basis === "satellit"} onclick={() => (karteEinst.basis = "satellit")}>Satellit</button>
      </div>
      <div class="formzeile-quer">
        <span class="fz-lab">Beschriftung &amp; Grenzen</span>
        <button class="schalter" class:an={karteEinst.orientierung} onclick={() => (karteEinst.orientierung = !karteEinst.orientierung)} aria-label="Beschriftung und Grenzen einblenden"></button>
      </div>
      <div class="kat-gruppe">Overlays</div>
      {#each overlayNamen as [schluessel, label]}
        <div class="formzeile-quer">
          <span class="fz-lab">{label}{#if schluessel === "blitze" && blitzAnzahl > 0}&nbsp;<b class="tnum" style="color: var(--warn)">{blitzAnzahl}</b>{/if}{#if schluessel === "warnungen" && warnAnzahl > 0}&nbsp;<b class="tnum" style="color: var(--warn)">{warnAnzahl}</b>{/if}</span>
          <button
            class="schalter"
            class:an={karteEinst.overlays[schluessel]}
            onclick={() => (karteEinst.overlays[schluessel] = !karteEinst.overlays[schluessel])}
            aria-label={label}
          ></button>
        </div>
      {/each}
      {#if karteEinst.overlays.blitze}
        <div class="formzeile" style="margin-top: var(--a1)">
          <label for="blitz-limit" class="fz-lab">Max. Blitze</label>
          <input
            id="blitz-limit"
            class="feld"
            type="number"
            min="100"
            max={BLITZE_LIMIT_MAX}
            step="1000"
            value={karteEinst.blitzeLimit}
            onchange={(e) =>
              (karteEinst.blitzeLimit = Math.min(BLITZE_LIMIT_MAX, Math.max(100, Number(e.currentTarget.value) || 20000)))}
          />
        </div>
        <p class="klein-txt dimm" style="margin: 2px var(--a1) 0; line-height: 1.35">
          So viele Blitze der letzten Stunde werden höchstens geladen (Dienst liefert bis {BLITZE_LIMIT_MAX.toLocaleString("de-DE")}).
        </p>
      {/if}
      <div class="kat-gruppe">Simulation</div>
      <div class="formzeile-quer">
        <span class="fz-lab">Blitz-Wellen (live){#if karteEinst.simulation}&nbsp;<i class="fa-solid fa-tower-broadcast" style="color: var(--gut); font-size: 0.68rem"></i>{/if}</span>
        <button class="schalter" class:an={karteEinst.simulation} onclick={() => (karteEinst.simulation = !karteEinst.simulation)} aria-label="Blitz-Wellen (live)"></button>
      </div>
    </div>

    {#if karteEinst.overlays.radar}
      <!-- Radar-Abspieler: Zeitleiste ueber gemessene + Vorhersage-Frames -->
      <div class="radar-leiste" style="z-index: 3;">
        <button class="radar-play" onclick={radarAbspielen} aria-label={radarSpielt ? "Pause" : "Abspielen"}>
          <i class="fa-solid {radarSpielt ? 'fa-pause' : 'fa-play'}"></i>
        </button>
        <input
          class="radar-schieber"
          type="range"
          min="0"
          max={Math.max(0, radarFrames.length - 1)}
          value={radarIdx}
          oninput={(e) => radarSchieben(+e.currentTarget.value)}
          aria-label="Radar-Zeitpunkt"
        />
        <span class="radar-zeit tnum" class:vorhersage={radarAktiv?.art === "vorhersage"}>
          {radarLaedt && !radarFrames.length ? "Radar wird geladen ..." : radarZeitLabel}
        </span>
      </div>
      <!-- Legende: Regenrate mm/h -->
      <div class="radar-legende" style="z-index: 3;">
        <span class="rl-titel">Regen mm/h</span>
        <span class="rl-chip" style="background: #4d8df2">0,1</span>
        <span class="rl-chip" style="background: #2980e6">0,5</span>
        <span class="rl-chip" style="background: #26c7b8">1</span>
        <span class="rl-chip" style="background: #40cc59">2</span>
        <span class="rl-chip" style="background: #f2e64d; color: #1f2933">5</span>
        <span class="rl-chip" style="background: #fa9e33; color: #1f2933">10</span>
        <span class="rl-chip" style="background: #eb4d33">20</span>
        <span class="rl-chip" style="background: #bf33bf">40+</span>
      </div>
    {/if}

    {#if tempHover && karteEinst.overlays.temperatur}
      <div class="temp-hover tnum" style="left: {tempHover.x}px; top: {tempHover.y}px; z-index: 4;">
        {tempHover.wert.toFixed(1)}°C
      </div>
    {/if}

    {#if karteEinst.overlays.temperatur}
      <div class="temp-legende" style="z-index: 3;">
        <span class="tl-titel">Temperatur °C</span>
        <span class="tl-bar"></span>
        <span class="tl-marks tnum"><i>-10</i><i>0</i><i>10</i><i>20</i><i>30</i><i>40</i></span>
      </div>
    {/if}

    <div class="attribution" style="z-index: 2;">© OpenStreetMap, © CARTO &middot; Blitze: Blitzortung.org &middot; Radar: DWD RADOLAN</div>
  </div>
</section>
