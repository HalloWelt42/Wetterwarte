<script lang="ts">
  // Zeitachse unter einem Diagramm: Marken an ihrem Anteil der Breite (0 links, 1 rechts).
  // Die erste Marke steht linksbündig, die letzte rechtsbündig, die übrigen mittig.
  let { marken }: { marken: { anteil: number; text: string; an?: boolean }[] } = $props();
</script>

<div class="achse" aria-hidden="true">
  {#each marken as m, i (i)}<span class:an={m.an} style="left: {m.anteil * 100}%">{m.text}</span>{/each}
</div>
