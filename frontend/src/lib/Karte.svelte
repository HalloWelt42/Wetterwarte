<script lang="ts">
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";
  import { lies, schreib } from "./speicher";

  const OVERLAYS_STANDARD: Record<string, boolean> = {
    blitze: true,
    warnungen: false,
    radar: false,
    wind: false,
    nowcast: false,
    temperatur: false,
  };

  let kartenEl: HTMLDivElement;
  let map: maplibregl.Map | undefined;
  // Gemerkte Einstellungen (localStorage) laden.
  let basis = $state<"hell" | "dunkel" | "satellit">(lies("karte.basis", "hell"));
  let overlays = $state<Record<string, boolean>>({ ...OVERLAYS_STANDARD, ...lies("karte.overlays", {}) });

  // ... und bei Aenderung merken.
  $effect(() => schreib("karte.basis", basis));
  $effect(() => schreib("karte.overlays", overlays));

  // Overlays, die schon Daten haben, zuerst; die uebrigen kommen Schritt fuer Schritt.
  const overlayNamen: [string, string][] = [
    ["blitze", "Blitze"],
    ["warnungen", "Warnungen"],
    ["radar", "Radar"],
    ["wind", "Wind"],
    ["nowcast", "Niederschlag-Nowcast"],
    ["temperatur", "Temperatur"],
  ];

  const provider: Record<string, string> = { hell: "light", dunkel: "dark", satellit: "satellite" };
  const kacheln = (b: string): string[] => [`/kachel/${provider[b] ?? "light"}/{z}/{x}/{y}`];

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
          basis: {
            type: "raster",
            tiles: kacheln("hell"),
            tileSize: 256,
            attribution: "© OpenStreetMap, © CARTO",
          },
        },
        layers: [{ id: "basis", type: "raster", source: "basis" }],
      },
      center: aktiverOrt(),
      zoom: 7,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.on("load", () => {
      baueBlitzEbene();
      baueWellenEbene();
      void ladeBlitze();
    });
    map.on("moveend", () => void ladeBlitze());
    blitzTimer = setInterval(() => void ladeBlitze(), 30000);
    return () => {
      clearInterval(blitzTimer);
      map?.remove();
    };
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
      layout: { visibility: overlays.blitze ? "visible" : "none" },
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
    const url = `/blitze?north=${b.getNorth().toFixed(2)}&south=${b.getSouth().toFixed(2)}&east=${b.getEast().toFixed(2)}&west=${b.getWest().toFixed(2)}&since=1&limit=2000`;
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
    const an = overlays.blitze;
    if (map?.getLayer("blitze")) map.setLayoutProperty("blitze", "visibility", an ? "visible" : "none");
  });

  // --- Optionale Blitz-Wellen-Simulation (live via WebSocket) ---
  // Jeder eingehende Blitz wirft einen Ring, der waechst und ausblendet
  // (wie eine Schallwelle). Zeitkritisch -> Live-Feed statt Polling.
  let simulation = $state<boolean>(lies("karte.simulation", false));
  $effect(() => schreib("karte.simulation", simulation));
  let ws: WebSocket | undefined;
  let wellen: { lon: number; lat: number; start: number }[] = [];
  let animLaeuft = false;
  const WELLE_MS = 1400;

  function imBlick(lon: number, lat: number): boolean {
    const b = map?.getBounds();
    return !!b && lon >= b.getWest() && lon <= b.getEast() && lat >= b.getSouth() && lat <= b.getNorth();
  }

  function baueWellenEbene(): void {
    if (!map || map.getSource("wellen")) return;
    map.addSource("wellen", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    map.addLayer({
      id: "wellen",
      type: "circle",
      source: "wellen",
      paint: {
        "circle-radius": ["get", "r"],
        "circle-color": "#ffffff",
        "circle-opacity": 0,
        "circle-stroke-color": "#ffe680",
        "circle-stroke-width": 2,
        "circle-stroke-opacity": ["get", "o"],
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
        const p = (jetzt - w.start) / WELLE_MS;
        return {
          type: "Feature" as const,
          geometry: { type: "Point" as const, coordinates: [w.lon, w.lat] },
          properties: { r: 4 + p * 34, o: 0.9 * (1 - p) },
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
    if (!simulation) return;
    verbindeWs();
    return () => trenneWs();
  });

  // Basiskarte umschalten (Kacheln der vorhandenen Quelle austauschen).
  $effect(() => {
    const b = basis;
    const quelle = map?.getSource("basis") as maplibregl.RasterTileSource | undefined;
    // setTiles ersetzt die Kachel-URLs ohne Neuaufbau der Karte.
    (quelle as unknown as { setTiles?: (t: string[]) => void })?.setTiles?.(kacheln(b));
  });

  // Karte auf den aktiven Ort schwenken, wenn er wechselt.
  $effect(() => {
    void wetter.slug;
    map?.flyTo({ center: aktiverOrt(), zoom: 7, duration: 800 });
  });
</script>

<section class="inhalt">
  <div style="flex: 1; position: relative; margin: var(--a4); min-height: 0;">
    <div bind:this={kartenEl} style="position: absolute; inset: 0; border-radius: var(--r2); overflow: hidden;"></div>

    <!-- Ebenen-Panel -->
    <div class="panel" style="position: absolute; left: var(--a4); top: var(--a4); width: 236px; z-index: 2; box-shadow: var(--schatten-2);">
      <h2><i class="fa-solid fa-layer-group"></i> Ebenen</h2>
      <div class="kat-gruppe">Basiskarte</div>
      <div class="segment tabgruppe" style="margin-bottom: var(--a2);">
        <button class:aktiv={basis === "hell"} onclick={() => (basis = "hell")}>Hell</button>
        <button class:aktiv={basis === "dunkel"} onclick={() => (basis = "dunkel")}>Dunkel</button>
        <button class:aktiv={basis === "satellit"} onclick={() => (basis = "satellit")}>Satellit</button>
      </div>
      <div class="kat-gruppe">Overlays</div>
      {#each overlayNamen as [schluessel, label]}
        <div class="formzeile-quer">
          <span class="fz-lab">{label}{#if schluessel === "blitze" && blitzAnzahl > 0}&nbsp;<b class="tnum" style="color: var(--warn)">{blitzAnzahl}</b>{/if}</span>
          <button
            class="schalter"
            class:an={overlays[schluessel]}
            onclick={() => (overlays[schluessel] = !overlays[schluessel])}
            aria-label={label}
          ></button>
        </div>
      {/each}
      <div class="kat-gruppe">Simulation</div>
      <div class="formzeile-quer">
        <span class="fz-lab">Blitz-Wellen (live){#if simulation}&nbsp;<i class="fa-solid fa-tower-broadcast" style="color: var(--gut); font-size: 0.68rem"></i>{/if}</span>
        <button class="schalter" class:an={simulation} onclick={() => (simulation = !simulation)} aria-label="Blitz-Wellen (live)"></button>
      </div>
    </div>

    <div class="attribution" style="z-index: 2;">© OpenStreetMap, © CARTO &middot; Blitze: Blitzortung.org</div>
  </div>
</section>
