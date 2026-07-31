<script lang="ts">
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";
  import HilfeLink from "./HilfeLink.svelte";
  import { karteEinst, kachelUrl } from "./karteEinst.svelte";

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
      baueBlitzEbene();
      baueWellenEbene();
      void ladeBlitze();
    });
    map.on("moveend", () => void ladeBlitze());
    blitzTimer = setInterval(() => void ladeBlitze(), 30000);
    return () => {
      clearInterval(blitzTimer);
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
    const an = karteEinst.overlays.blitze;
    if (map?.getLayer("blitze")) map.setLayoutProperty("blitze", "visibility", an ? "visible" : "none");
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
          <span class="fz-lab">{label}{#if schluessel === "blitze" && blitzAnzahl > 0}&nbsp;<b class="tnum" style="color: var(--warn)">{blitzAnzahl}</b>{/if}</span>
          <button
            class="schalter"
            class:an={karteEinst.overlays[schluessel]}
            onclick={() => (karteEinst.overlays[schluessel] = !karteEinst.overlays[schluessel])}
            aria-label={label}
          ></button>
        </div>
      {/each}
      <div class="kat-gruppe">Simulation</div>
      <div class="formzeile-quer">
        <span class="fz-lab">Blitz-Wellen (live){#if karteEinst.simulation}&nbsp;<i class="fa-solid fa-tower-broadcast" style="color: var(--gut); font-size: 0.68rem"></i>{/if}</span>
        <button class="schalter" class:an={karteEinst.simulation} onclick={() => (karteEinst.simulation = !karteEinst.simulation)} aria-label="Blitz-Wellen (live)"></button>
      </div>
    </div>

    <div class="attribution" style="z-index: 2;">© OpenStreetMap, © CARTO &middot; Blitze: Blitzortung.org</div>
  </div>
</section>
