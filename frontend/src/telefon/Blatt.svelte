<script lang="ts">
  // Blatt von unten: Griff, Titel, Schließen-Knopf, rollender Inhalt. Nach unten ziehen am Griff
  // oder Kopf schließt es, ebenso der Knopf und das Tippen daneben.
  import type { Snippet } from "svelte";

  let {
    titel,
    unter = "",
    voll = false,
    schliessen,
    children,
  }: { titel: string; unter?: string; voll?: boolean; schliessen: () => void; children: Snippet } = $props();

  let zug = $state(0);
  let start = $state<number | null>(null);

  function unten(e: PointerEvent): void {
    start = e.clientY;
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  }
  function bewegt(e: PointerEvent): void {
    if (start !== null) zug = Math.max(0, e.clientY - start);
  }
  function los(): void {
    if (zug > 110) schliessen();
    zug = 0;
    start = null;
  }
</script>

<div class="abdunkeln" role="presentation" onclick={schliessen}></div>
<div class="blatt" class:voll style="transform: translateY({zug}px); transition: {start === null ? 'transform 0.18s ease' : 'none'}" role="dialog" aria-modal="true" aria-label={titel}>
  <div class="zugflaeche" role="presentation" onpointerdown={unten} onpointermove={bewegt} onpointerup={los} onpointercancel={los}>
    <div class="blatt-griff"></div>
    <div class="blatt-kopf">
      <div class="blatt-titel">{titel}{#if unter}<small>{unter}</small>{/if}</div>
      <button class="knopf-rund flaeche" aria-label="Schließen" onclick={schliessen} onpointerdown={(e) => e.stopPropagation()}>
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </div>
  <div class="blatt-inhalt">{@render children()}</div>
</div>

<style>
  .zugflaeche {
    touch-action: none;
    flex: none;
  }
</style>
