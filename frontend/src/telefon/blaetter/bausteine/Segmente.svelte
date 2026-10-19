<script lang="ts" generics="T extends string">
  // Umschaltung zwischen Ansichten eines Blatts (Heute/Morgen, 24 h/48 h). Zeigt nur, ändert nichts.
  let { optionen, wert = $bindable() }: { optionen: { wert: T; titel: string }[]; wert: T } = $props();
</script>

<div class="segmente seg" role="group">
  {#each optionen as o (o.wert)}
    <button type="button" class:an={o.wert === wert} aria-pressed={o.wert === wert} onclick={() => (wert = o.wert)}>{o.titel}</button>
  {/each}
</div>

