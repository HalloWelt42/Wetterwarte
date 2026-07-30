<script lang="ts">
  // Echte MapLibre-Mini-Karte fuer die Dashboard-Kachel: Basiskarte (themabewusst)
  // zentriert auf den aktiven Ort, plus Live-Blitze. Aufklappen fuehrt zur
  // Vollansicht. Nutzt dieselben Kachel-/Blitz-Quellen wie die grosse Karte.
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";
  import { thema } from "./thema.svelte";
  import { gehe } from "./route.svelte";

  // Ort dieser Karte (Standard: aktiver Ort).
  let { ort }: { ort?: string } = $props();
  const slug = $derived(ort || wetter.slug);

  let kartenEl: HTMLDivElement;
  let map: maplibregl.Map | undefined;
  let blitzTimer: ReturnType<typeof setInterval> | undefined;
  let blitzAnzahl = $state(0);

  const provider: Record<string, string> = { hell: "light", dunkel: "dark" };
  const kacheln = (t: string): string[] => [`/kachel/${provider[t] ?? "light"}/{z}/{x}/{y}`];

  function aktiverOrt(): [number, number] {
    const o = orteState.liste.find((x) => x.slug === slug);
    return o ? [o.lon, o.lat] : [10.45, 51.16];
  }

  async function ladeBlitze(): Promise<void> {
    if (!map) return;
    const b = map.getBounds();
    const url = `/blitze?north=${b.getNorth().toFixed(2)}&south=${b.getSouth().toFixed(2)}&east=${b.getEast().toFixed(2)}&west=${b.getWest().toFixed(2)}&since=1&limit=1000`;
    try {
      const daten = await (await fetch(url)).json();
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

  onMount(() => {
    map = new maplibregl.Map({
      container: kartenEl,
      style: {
        version: 8,
        sources: { basis: { type: "raster", tiles: kacheln(thema.wert), tileSize: 256 } },
        layers: [{ id: "basis", type: "raster", source: "basis" }],
      },
      center: aktiverOrt(),
      zoom: 6,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.on("load", () => {
      map!.addSource("blitze", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map!.addLayer({
        id: "blitze",
        type: "circle",
        source: "blitze",
        paint: {
          "circle-radius": 3,
          "circle-color": ["interpolate", ["linear"], ["get", "min"], 0, "#ffffff", 5, "#ffd400", 20, "#ff7b00", 60, "#b23a00"],
          "circle-opacity": 0.9,
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 0.4,
        },
      });
      void ladeBlitze();
    });
    map.on("moveend", () => void ladeBlitze());
    // Blitze sind zeitkritisch; auf der Kachel etwas ruhiger als in der Vollansicht.
    blitzTimer = setInterval(() => void ladeBlitze(), 60000);

    // Bei Kachel-Groessenaenderung (gridstack) die Karte neu vermessen.
    const beobachter = new ResizeObserver(() => map?.resize());
    beobachter.observe(kartenEl);

    return () => {
      clearInterval(blitzTimer);
      beobachter.disconnect();
      map?.remove();
    };
  });

  // Basiskarte dem Thema folgen lassen.
  $effect(() => {
    const t = thema.wert;
    (map?.getSource("basis") as unknown as { setTiles?: (u: string[]) => void } | undefined)?.setTiles?.(kacheln(t));
  });

  // Auf Ortswechsel schwenken.
  $effect(() => {
    void slug;
    map?.flyTo({ center: aktiverOrt(), zoom: 6, duration: 700 });
  });
</script>

<div class="mini-karte">
  <div bind:this={kartenEl} class="mini-karte-flaeche"></div>
  <button class="icon-knopf mini-auf" aria-label="Grosse Karte oeffnen" onclick={() => gehe("karte")}>
    <i class="fa-solid fa-up-right-and-down-left-from-center"></i>
  </button>
  {#if blitzAnzahl > 0}
    <div class="mini-blitz-zaehler"><i class="fa-solid fa-bolt"></i> {blitzAnzahl}</div>
  {/if}
  <div class="mini-attribution">&copy; OpenStreetMap, &copy; CARTO &middot; Blitze: Blitzortung.org</div>
</div>
