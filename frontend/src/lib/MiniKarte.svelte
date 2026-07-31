<script lang="ts">
  // Echte MapLibre-Mini-Karte fuer die Dashboard-Kachel. Folgt denselben
  // Einstellungen wie die grosse Karte (karteEinst): Basiskarte, Orientierungs-Ebene
  // und Blitze-Overlay. Zentriert auf den Ort dieser Kachel; Aufklappen -> Vollansicht.
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";
  import { wetter } from "./wetter.svelte";
  import { orteState } from "./orte.svelte";
  import { gehe } from "./route.svelte";
  import { karteEinst, kachelUrl } from "./karteEinst.svelte";

  // Ort dieser Karte (Standard: aktiver Ort).
  let { ort }: { ort?: string } = $props();
  const slug = $derived(ort || wetter.slug);

  let kartenEl: HTMLDivElement;
  let map: maplibregl.Map | undefined;
  let ortMarker: maplibregl.Marker | undefined;
  let blitzTimer: ReturnType<typeof setInterval> | undefined;
  let blitzAnzahl = $state(0);

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
        sources: { basis: { type: "raster", tiles: kachelUrl(karteEinst.basis), tileSize: 256 } },
        layers: [{ id: "basis", type: "raster", source: "basis" }],
      },
      center: aktiverOrt(),
      zoom: 6,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    // Pinnnadel am Ort dieser Karte.
    ortMarker = new maplibregl.Marker({ color: "#2f7ce0" }).setLngLat(aktiverOrt()).addTo(map);
    map.on("load", () => {
      // Orientierungs-Ebene (voyager), wie in der grossen Karte.
      map!.addSource("beschriftung", { type: "raster", tiles: ["/kachel/voyager/{z}/{x}/{y}"], tileSize: 256 });
      map!.addLayer({
        id: "beschriftung",
        type: "raster",
        source: "beschriftung",
        layout: { visibility: karteEinst.orientierung ? "visible" : "none" },
        paint: { "raster-opacity": karteEinst.basis === "satellit" ? 0.5 : 0.7 },
      });
      map!.addSource("blitze", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map!.addLayer({
        id: "blitze",
        type: "circle",
        source: "blitze",
        layout: { visibility: karteEinst.overlays.blitze ? "visible" : "none" },
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
      ortMarker?.remove();
      map?.remove();
    };
  });

  // Basiskarte den Einstellungen folgen lassen.
  $effect(() => {
    const b = karteEinst.basis;
    (map?.getSource("basis") as unknown as { setTiles?: (u: string[]) => void } | undefined)?.setTiles?.(kachelUrl(b));
    if (map?.getLayer("beschriftung")) map.setPaintProperty("beschriftung", "raster-opacity", b === "satellit" ? 0.5 : 0.7);
  });

  // Orientierungs-Ebene ein-/ausblenden.
  $effect(() => {
    const an = karteEinst.orientierung;
    if (map?.getLayer("beschriftung")) map.setLayoutProperty("beschriftung", "visibility", an ? "visible" : "none");
  });

  // Blitze-Overlay ein-/ausblenden.
  $effect(() => {
    const an = karteEinst.overlays.blitze;
    if (map?.getLayer("blitze")) map.setLayoutProperty("blitze", "visibility", an ? "visible" : "none");
  });

  // Auf Ortswechsel schwenken und die Pinnnadel mitfuehren.
  $effect(() => {
    void slug;
    void orteState.liste.length;
    const ziel = aktiverOrt();
    ortMarker?.setLngLat(ziel);
    map?.flyTo({ center: ziel, zoom: 6, duration: 700 });
  });
</script>

<div class="mini-karte">
  <div bind:this={kartenEl} class="mini-karte-flaeche"></div>
  <button class="icon-knopf mini-auf" aria-label="Grosse Karte oeffnen" onclick={() => gehe("karte")}>
    <i class="fa-solid fa-up-right-and-down-left-from-center"></i>
  </button>
  {#if blitzAnzahl > 0 && karteEinst.overlays.blitze}
    <div class="mini-blitz-zaehler"><i class="fa-solid fa-bolt"></i> {blitzAnzahl}</div>
  {/if}
  <div class="mini-attribution">&copy; OpenStreetMap, &copy; CARTO &middot; Blitze: Blitzortung.org</div>
</div>
