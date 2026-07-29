<script lang="ts">
  import Kopf from "./lib/Kopf.svelte";
  import Nav from "./lib/Nav.svelte";
  import Dashboard from "./lib/Dashboard.svelte";
  import Karte from "./lib/Karte.svelte";
  import { route } from "./lib/route.svelte";
</script>

<div class="app">
  <Kopf />
  <Nav />
  {#if route.ansicht === "karte"}
    <Karte />
  {:else}
    <Dashboard />
  {/if}
</div>
