<script lang="ts">
  // Echte MapLibre-Mini-Karte fuer die Dashboard-Kachel. Die Einstellungen
  // (Basiskarte, Orientierung, Blitze, Radar, Warnungen, Temperatur) leben PRO
  // KACHEL-INSTANZ in ihrer conf - so ist jede Karten-Kachel und jedes Profil
  // unabhaengig. Zentriert auf den Ort dieser Kachel; Aufklappen -> grosse Ansicht.
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";
  import { gehe } from "./route.svelte";
  import { kachelUrl } from "./karteEinst.svelte";
  import { patcheKachel } from "./kachelConf.svelte";

  let { id, conf = {}, ort }: { id: string; conf?: Record<string, any>; ort?: string } = $props();
  const slug = $derived(ort || wetter.slug);

  // Einstellungen aus der conf dieser Kachel-Instanz (mit sinnvollen Standardwerten).
  const basis = $derived((conf.basis as "hell" | "dunkel" | "satellit") ?? "hell");
  const orientierung = $derived(conf.orientierung === true);
  const blitzeAn = $derived(conf.blitze !== false); // Standard: an
  const radarAn = $derived(conf.radar === true);
  const warnungenAn = $derived(conf.warnungen === true);
  const temperaturAn = $derived(conf.temperatur === true);
  const blitzeLimit = $derived((conf.blitzeLimit as number) ?? 20000);

  const BASEN: ("hell" | "dunkel" | "satellit")[] = ["hell", "dunkel", "satellit"];
  const basisIcon = $derived(basis === "dunkel" ? "fa-moon" : basis === "satellit" ? "fa-satellite" : "fa-sun");
  const basisName = $derived(basis === "dunkel" ? "Dunkel" : basis === "satellit" ? "Satellit" : "Hell");

  // Temperatur-Farbfeld (deutschlandweit) als Bild-Overlay - gleiche Ecken wie die grosse Karte.
  const TEMP_COORDS: [[number, number], [number, number], [number, number], [number, number]] = [
    [5.8, 55.1],
    [15.1, 55.1],
    [15.1, 47.2],
    [5.8, 47.2],
  ];
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

  let kartenEl: HTMLDivElement;
  let map: maplibregl.Map | undefined;
  let ortMarker: maplibregl.Marker | undefined;
  let blitzTimer: ReturnType<typeof setInterval> | undefined;
  let warnTimer: ReturnType<typeof setInterval> | undefined;
  let blitzAnzahl = $state(0);

  function aktiverOrt(): [number, number] {
    const o = orteState.liste.find((x) => x.slug === slug);
    return o ? [o.lon, o.lat] : [10.45, 51.16];
  }

  async function ladeBlitze(): Promise<void> {
    if (!map) return;
    const b = map.getBounds();
    const url = `/blitze?north=${b.getNorth().toFixed(2)}&south=${b.getSouth().toFixed(2)}&east=${b.getEast().toFixed(2)}&west=${b.getWest().toFixed(2)}&since=1&limit=${blitzeLimit}`;
    try {
      const daten = await (await fetch(url)).json();
      if (!map) return; // Karte kann waehrend des Ladens entfernt worden sein
      const strikes: { t: number; lat: number; lon: number }[] = daten.strikes ?? [];
      const jetzt = Date.now();
      (map.getSource("blitze") as maplibregl.GeoJSONSource | undefined)?.setData({
        type: "FeatureCollection",
        features: strikes.map((s) => ({
          type: "Feature" as const,
          geometry: { type: "Point" as const, coordinates: [s.lon, s.lat] },
          properties: { min: Math.max(0, (jetzt - s.t) / 60000) },
        })),
      });
      blitzAnzahl = strikes.length;
    } catch {
      // still ignorieren
    }
  }

  async function ladeWarnungen(): Promise<void> {
    if (!map) return;
    try {
      const d = (await (await fetch("/api/v1/wetter/warnkarte")).json()).data as GeoJSON.FeatureCollection;
      if (!map) return; // Karte kann waehrend des Ladens entfernt worden sein
      (map.getSource("warnungen") as maplibregl.GeoJSONSource | undefined)?.setData(d);
    } catch {
      // still ignorieren
    }
  }

  onMount(() => {
    map = new maplibregl.Map({
      container: kartenEl,
      style: {
        version: 8,
        sources: { basis: { type: "raster", tiles: kachelUrl(basis), tileSize: 256 } },
        layers: [{ id: "basis", type: "raster", source: "basis" }],
      },
      center: aktiverOrt(),
      zoom: 6,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    ortMarker = new maplibregl.Marker({ color: "#2f7ce0" }).setLngLat(aktiverOrt()).addTo(map);
    map.on("load", () => {
      // Temperatur-Farbfeld (unter der Beschriftung).
      map!.addSource("temperatur", { type: "image", url: "/api/v1/wetter/temperatur.png", coordinates: TEMP_COORDS });
      map!.addLayer({
        id: "temperatur",
        type: "raster",
        source: "temperatur",
        paint: { "raster-opacity": 0.6, "raster-fade-duration": 0 },
        layout: { visibility: temperaturAn ? "visible" : "none" },
      });
      // Orientierungs-Ebene (voyager).
      map!.addSource("beschriftung", { type: "raster", tiles: ["/kachel/voyager/{z}/{x}/{y}"], tileSize: 256 });
      map!.addLayer({
        id: "beschriftung",
        type: "raster",
        source: "beschriftung",
        layout: { visibility: orientierung ? "visible" : "none" },
        paint: { "raster-opacity": basis === "satellit" ? 0.5 : 0.7 },
      });
      // Warn-Polygone (farbig nach Stufe).
      map!.addSource("warnungen", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map!.addLayer({
        id: "warn-fill",
        type: "fill",
        source: "warnungen",
        layout: { visibility: warnungenAn ? "visible" : "none" },
        paint: { "fill-color": WARN_FARBE, "fill-opacity": 0.25 },
      });
      map!.addLayer({
        id: "warn-linie",
        type: "line",
        source: "warnungen",
        layout: { visibility: warnungenAn ? "visible" : "none" },
        paint: { "line-color": WARN_FARBE, "line-width": 1.2, "line-opacity": 0.85 },
      });
      // Blitze.
      map!.addSource("blitze", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map!.addLayer({
        id: "blitze",
        type: "circle",
        source: "blitze",
        layout: { visibility: blitzeAn ? "visible" : "none" },
        paint: {
          "circle-radius": 3,
          "circle-color": ["interpolate", ["linear"], ["get", "min"], 0, "#ffffff", 5, "#ffd400", 20, "#ff7b00", 60, "#b23a00"],
          "circle-opacity": 0.9,
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 0.4,
        },
      });
      void ladeBlitze();
      if (warnungenAn) void ladeWarnungen();
    });
    map.on("moveend", () => void ladeBlitze());
    blitzTimer = setInterval(() => void ladeBlitze(), 60000);

    const beobachter = new ResizeObserver(() => map?.resize());
    beobachter.observe(kartenEl);

    return () => {
      clearInterval(blitzTimer);
      if (radarTimer) clearInterval(radarTimer);
      if (warnTimer) clearInterval(warnTimer);
      beobachter.disconnect();
      ortMarker?.remove();
      map?.remove();
      map = undefined; // verhindert Zugriffe auf die entfernte Karte in laufenden Callbacks
    };
  });

  // Basiskarte den Einstellungen folgen lassen.
  $effect(() => {
    const b = basis;
    (map?.getSource("basis") as unknown as { setTiles?: (u: string[]) => void } | undefined)?.setTiles?.(kachelUrl(b));
    if (map?.getLayer("beschriftung")) map.setPaintProperty("beschriftung", "raster-opacity", b === "satellit" ? 0.5 : 0.7);
  });

  // Orientierungs-Ebene ein-/ausblenden.
  $effect(() => {
    if (map?.getLayer("beschriftung")) map.setLayoutProperty("beschriftung", "visibility", orientierung ? "visible" : "none");
  });

  // Blitze-Overlay ein-/ausblenden.
  $effect(() => {
    if (map?.getLayer("blitze")) map.setLayoutProperty("blitze", "visibility", blitzeAn ? "visible" : "none");
  });

  // Temperatur-Overlay ein-/ausblenden.
  $effect(() => {
    const an = temperaturAn ? "visible" : "none";
    if (map?.getLayer("temperatur")) map.setLayoutProperty("temperatur", "visibility", an);
  });

  // Warnungen ein-/ausblenden (bei Bedarf laden + im Intervall auffrischen).
  $effect(() => {
    if (warnungenAn) {
      if (map?.getLayer("warn-fill")) {
        map.setLayoutProperty("warn-fill", "visibility", "visible");
        map.setLayoutProperty("warn-linie", "visibility", "visible");
      }
      void ladeWarnungen();
      if (!warnTimer) warnTimer = setInterval(() => void ladeWarnungen(), 180000);
    } else {
      if (warnTimer) clearInterval(warnTimer);
      warnTimer = undefined;
      if (map?.getLayer("warn-fill")) {
        map.setLayoutProperty("warn-fill", "visibility", "none");
        map.setLayoutProperty("warn-linie", "visibility", "none");
      }
    }
  });

  // --- Radar (nur der aktuelle Stand, ohne Abspieler/Vorhersage) ---
  let radarGebaut = false;
  let radarTimer: ReturnType<typeof setInterval> | undefined;

  async function ladeMiniRadar(): Promise<void> {
    if (!map) return;
    try {
      const d = (await (await fetch("/api/v1/radar/rahmen")).json()).data as {
        coords: [number, number][];
        frames: { id: string; art: string }[];
      };
      if (!map) return; // Karte kann waehrend des Ladens entfernt worden sein
      const gemessen = d.frames.filter((f) => f.art === "gemessen");
      const jetzt = gemessen.at(-1) ?? d.frames.at(-1);
      if (!jetzt) return;
      const url = `/api/v1/radar/bild/${jetzt.id}.png`;
      const koord = d.coords as [[number, number], [number, number], [number, number], [number, number]];
      if (!radarGebaut) {
        map.addSource("radar", { type: "image", url, coordinates: koord });
        map.addLayer(
          {
            id: "radar",
            type: "raster",
            source: "radar",
            paint: { "raster-opacity": 0.7, "raster-fade-duration": 0 },
            layout: { visibility: radarAn ? "visible" : "none" },
          },
          map.getLayer("beschriftung") ? "beschriftung" : undefined,
        );
        radarGebaut = true;
      } else {
        (map.getSource("radar") as maplibregl.ImageSource | undefined)?.updateImage({ url });
      }
    } catch {
      // still ignorieren
    }
  }

  // Radar an den Schalter koppeln (aktueller Stand, alle 5 min auffrischen).
  $effect(() => {
    if (radarAn) {
      if (!radarGebaut) void ladeMiniRadar();
      else if (map?.getLayer("radar")) map.setLayoutProperty("radar", "visibility", "visible");
      if (!radarTimer) radarTimer = setInterval(() => void ladeMiniRadar(), 300000);
    } else {
      if (radarTimer) clearInterval(radarTimer);
      radarTimer = undefined;
      if (map?.getLayer("radar")) map.setLayoutProperty("radar", "visibility", "none");
    }
  });

  // Auf Ortswechsel schwenken und die Pinnnadel mitfuehren.
  $effect(() => {
    void slug;
    void orteState.liste.length;
    const ziel = aktiverOrt();
    ortMarker?.setLngLat(ziel);
    map?.flyTo({ center: ziel, zoom: 6, duration: 700 });
  });

  // Overlay-/Basis-Schalter der Kachel: schreiben in die conf DIESER Instanz (pro Profil).
  const umschalten = (feld: string, wert: boolean) => patcheKachel(id, { [feld]: wert });
  function naechsteBasis(): void {
    patcheKachel(id, { basis: BASEN[(BASEN.indexOf(basis) + 1) % BASEN.length] });
  }
</script>

<div class="mini-karte">
  <div bind:this={kartenEl} class="mini-karte-flaeche"></div>
  <!-- Icon-Schalter je Kachel-Instanz (unabhaengig von anderen Karten/Profilen). -->
  <div class="mini-ebenen">
    <button class="basis-knopf" title="Basiskarte: {basisName} (wechseln)" aria-label="Basiskarte wechseln" onclick={naechsteBasis}>
      <i class="fa-solid {basisIcon}"></i>
    </button>
    <button class:an={orientierung} title="Beschriftung &amp; Grenzen" aria-label="Beschriftung und Grenzen" onclick={() => umschalten("orientierung", !orientierung)}><i class="fa-solid fa-signs-post"></i></button>
    <button class:an={warnungenAn} title="Warnungen" aria-label="Warnungen" onclick={() => umschalten("warnungen", !warnungenAn)}><i class="fa-solid fa-triangle-exclamation"></i></button>
    <button class:an={temperaturAn} title="Temperatur" aria-label="Temperatur" onclick={() => umschalten("temperatur", !temperaturAn)}><i class="fa-solid fa-temperature-half"></i></button>
    <button class:an={blitzeAn} title="Blitze" aria-label="Blitze" onclick={() => umschalten("blitze", !blitzeAn)}><i class="fa-solid fa-bolt"></i></button>
    <button class:an={radarAn} title="Regen-Radar" aria-label="Regen-Radar" onclick={() => umschalten("radar", !radarAn)}><i class="fa-solid fa-cloud-showers-heavy"></i></button>
  </div>
  <button class="icon-knopf mini-auf" aria-label="Grosse Karte oeffnen" onclick={() => gehe("karte")}>
    <i class="fa-solid fa-up-right-and-down-left-from-center"></i>
  </button>
  {#if blitzAnzahl > 0 && blitzeAn}
    <div class="mini-blitz-zaehler"><i class="fa-solid fa-bolt"></i> {blitzAnzahl}</div>
  {/if}
  <div class="mini-attribution">&copy; OpenStreetMap, &copy; CARTO &middot; Blitze: Blitzortung.org</div>
</div>
