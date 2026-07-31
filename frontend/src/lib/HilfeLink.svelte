<script lang="ts">
  // Hilfepunkt an fachlichen Stellen: oeffnet das Hilfe-Panel beim passenden Thema;
  // optional wird ein Begriff gleich gesucht und markiert (Auffinden).
  // Beispiel: <HilfeLink topic="karte" find="Blitze">Overlays</HilfeLink>
  import { hilfe } from "./hilfeStore.svelte";

  let { topic, find = "", children = null }: { topic: string; find?: string; children?: (() => unknown) | null } = $props();

  function oeffnen(e: MouseEvent): void {
    e.preventDefault();
    e.stopPropagation();
    if (find) hilfe.find(topic, find);
    else hilfe.show(topic);
  }
</script>

<button type="button" class="hilfe-link" class:nur-marke={!children} onclick={oeffnen} title="Hilfe zu diesem Punkt" aria-label="Hilfe">
  {#if children}{@render children()}{/if}
  <i class="fa-solid fa-circle-info"></i>
</button>

<style>
  .hilfe-link {
    background: transparent;
    border: 0;
    padding: 0;
    color: inherit;
    font: inherit;
    cursor: help;
    display: inline-flex;
    align-items: baseline;
    gap: 4px;
  }
  .hilfe-link > i {
    font-size: 0.78em;
    color: var(--akzent);
    transform: translateY(1px);
  }
  .hilfe-link:hover > i {
    color: var(--akzent-stark);
  }
</style>
