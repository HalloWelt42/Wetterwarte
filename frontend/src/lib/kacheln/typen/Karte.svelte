<script lang="ts">
  // Karten-Kachel: echte MapLibre-Mini-Karte fuer den Ort dieser Kachel.
  import MiniKarte from "../../MiniKarte.svelte";

  let { ort }: { conf?: Record<string, any>; ort: string } = $props();
</script>

<MiniKarte {ort} />
