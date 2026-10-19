<script lang="ts">
  // Kachelkopf: Symbol, Titel in Großbuchstaben (13 px), rechts ein kurzer Zusatz, optional mit Symbol.
  let {
    titel,
    symbol = "",
    rechts = "",
    rechtsSymbol = "",
  }: { titel: string; symbol?: string; rechts?: string; rechtsSymbol?: string } = $props();
</script>

<div class="k-kopf">
  {#if symbol}<i class="fa-solid {symbol}"></i>{/if}<span>{titel}</span>{#if rechts}<span class="rechts">{#if rechtsSymbol}<i class="fa-solid {rechtsSymbol}"></i> {/if}{rechts}</span>{/if}
</div>
