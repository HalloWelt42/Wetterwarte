<script lang="ts">
  import Kopf from "./lib/Kopf.svelte";
  import Nav from "./lib/Nav.svelte";
  import Dashboard from "./lib/Dashboard.svelte";
  import Karte from "./lib/Karte.svelte";
  import Aufzeichnung from "./lib/Aufzeichnung.svelte";
  import Archiv from "./lib/Archiv.svelte";
  import { route } from "./lib/route.svelte";
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
