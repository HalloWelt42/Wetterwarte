<script lang="ts">
  import { onMount } from "svelte";
  import maplibregl from "maplibre-gl";

  let kartenEl: HTMLDivElement;
  let basis = $state<"hell" | "dunkel" | "satellit">("hell");
  let overlays = $state<Record<string, boolean>>({
    radar: true,
    nowcast: false,
    wind: false,
    temperatur: false,
    warnungen: true,
    blitze: true,
  });

  const overlayNamen: [string, string][] = [
    ["radar", "Radar (DWD RADOLAN)"],
    ["nowcast", "Niederschlag-Nowcast"],
    ["wind", "Wind"],
    ["temperatur", "Temperatur"],
    ["warnungen", "Warnungen"],
    ["blitze", "Blitze"],
  ];

  onMount(() => {
    // Raster-Kacheln same-origin ueber den Vite-Proxy /karte -> osmlocal (Deutschland).
    const map = new maplibregl.Map({
      container: kartenEl,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["/karte/raster/colorful/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap-Mitwirkende",
          },
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }],
      },
      center: [12.14, 51.05],
      zoom: 8,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    return () => map.remove();
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
          <span class="fz-lab">{label}</span>
          <button
            class="schalter"
            class:an={overlays[schluessel]}
            onclick={() => (overlays[schluessel] = !overlays[schluessel])}
            aria-label={label}
          ></button>
        </div>
      {/each}
    </div>

    <!-- Radar-Zeitleiste -->
    <div
      class="panel"
      style="position: absolute; left: 50%; bottom: var(--a4); transform: translateX(-50%); z-index: 2; display: flex; align-items: center; gap: var(--a3); padding: var(--a2) var(--a3); margin: 0; box-shadow: var(--schatten-2);"
    >
      <button class="icon-knopf"><i class="fa-solid fa-play"></i></button>
      <div style="width: 280px;">
        <div style="height: 6px; border-radius: 3px; background: var(--flaeche-3); position: relative;">
          <span style="position: absolute; left: 66%; top: -4px; width: 14px; height: 14px; border-radius: 50%; background: var(--akzent);"></span>
        </div>
        <div class="reihe" style="justify-content: space-between; font-size: 0.7rem; color: var(--text-3); margin-top: 4px;">
          <span>-2 h</span><span>jetzt</span><span>+1 h</span>
        </div>
      </div>
      <div class="segment tabgruppe"><button class="aktiv">1x</button><button>2x</button></div>
    </div>

    <div class="karten-legende" style="z-index: 2;">Niederschlag mm/h<div class="legende-skala"></div></div>
    <div class="attribution" style="z-index: 2;">© OpenStreetMap-Mitwirkende &middot; DWD RADOLAN &middot; Blitzortung</div>
  </div>
</section>
