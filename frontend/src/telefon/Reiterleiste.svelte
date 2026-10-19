<script lang="ts">
  import { ansicht, zeige, type Reiter } from "./ansicht.svelte";

  const REITER: { r: Reiter; titel: string; symbol: string }[] = [
    { r: "karte", titel: "Karte", symbol: "fa-map-location-dot" },
    { r: "wetter", titel: "Wetter", symbol: "fa-cloud-sun" },
    { r: "gesundheit", titel: "Gesundheit", symbol: "fa-heart-pulse" },
    { r: "mehr", titel: "Mehr", symbol: "fa-ellipsis" },
  ];
</script>

<nav class="leiste" aria-label="Bereiche">
  {#each REITER as { r, titel, symbol }}
    <button class:an={ansicht.reiter === r} aria-current={ansicht.reiter === r ? "page" : undefined} onclick={() => zeige(r)}>
      <i class="fa-solid {symbol}"></i>{titel}
    </button>
  {/each}
</nav>
