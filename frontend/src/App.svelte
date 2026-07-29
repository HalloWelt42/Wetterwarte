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
  import { ladeWetter } from "./lib/wetter.svelte";

  onMount(() => {
    void ladeLayouts();
    void ladeWetter("koeln");
  });
</script>

<div class="app">
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
