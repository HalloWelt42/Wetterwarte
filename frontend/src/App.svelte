<script lang="ts">
  import { onMount } from "svelte";
  import Kopf from "./lib/Kopf.svelte";
  import Nav from "./lib/Nav.svelte";
  import Dashboard from "./lib/Dashboard.svelte";
  import Karte from "./lib/Karte.svelte";
  import Aufzeichnung from "./lib/Aufzeichnung.svelte";
  import Archiv from "./lib/Archiv.svelte";
  import Katalog from "./lib/Katalog.svelte";
  import Hilfe from "./lib/Hilfe.svelte";
  import Layouts from "./lib/Layouts.svelte";
  import KachelEinstellungen from "./lib/KachelEinstellungen.svelte";
  import { route } from "./lib/route.svelte";
  import { ui } from "./lib/ui.svelte";
  import { ladeLayouts } from "./lib/layout.svelte";
  import { ladeWetter, wetter } from "./lib/wetter.svelte";
  import { stil } from "./lib/stil.svelte";

  onMount(() => {
    void ladeLayouts();
    void ladeWetter("koeln");
  });

  function stimmungFuer(icon?: string): string {
    if (!icon) return "tag-klar";
    if (icon.includes("night")) return "nacht-klar";
    if (icon.startsWith("rain") || icon.startsWith("drizzle") || icon.startsWith("thunder")) return "regen";
    if (icon.startsWith("overcast") || icon === "cloudy" || icon.startsWith("fog")) return "tag-wolkig";
    return "tag-klar";
  }
  const appKlasse = $derived(stil.atmo ? `app atmo ${stimmungFuer(wetter.aktuell?.icon)}` : "app");
</script>

<div class={appKlasse}>
  <Kopf />
  <Nav />
  {#if route.ansicht === "karte"}
    <Karte />
  {:else if route.ansicht === "aufzeichnung"}
    <Aufzeichnung />
  {:else if route.ansicht === "archiv"}
    <Archiv />
  {:else}
    <Dashboard />
  {/if}
</div>

{#if ui.katalog}<Katalog />{/if}
{#if ui.hilfe}<Hilfe />{/if}
{#if ui.layouts}<Layouts />{/if}
{#if ui.einstellungen}<KachelEinstellungen />{/if}
