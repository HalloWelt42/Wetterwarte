<script lang="ts">
  // Karten-Kachel: echte MapLibre-Mini-Karte fuer den Ort dieser Kachel.
  // id + conf werden durchgereicht, damit jede Kachel-Instanz ihre eigenen
  // Karten-Einstellungen (Basiskarte, Overlays) pro Profil behaelt.
  import MiniKarte from "../../MiniKarte.svelte";

  let { id, conf = {}, ort }: { id: string; conf?: Record<string, any>; ort: string } = $props();
</script>

<MiniKarte {id} {conf} {ort} />
