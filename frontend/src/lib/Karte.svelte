<script lang="ts">
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";

  let kartenEl: HTMLDivElement;
  let map: maplibregl.Map | undefined;
  let basis = $state<"hell" | "dunkel" | "satellit">("hell");
  let overlays = $state<Record<string, boolean>>({
    blitze: true,
    warnungen: false,
    radar: false,
    wind: false,
    nowcast: false,
    temperatur: false,
  });

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
    </div>

    <div class="attribution" style="z-index: 2;">© OpenStreetMap, © CARTO &middot; Blitze: Blitzortung.org</div>
  </div>
</section>
