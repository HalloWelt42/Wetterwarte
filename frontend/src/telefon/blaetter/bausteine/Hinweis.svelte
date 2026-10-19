<script lang="ts">
  // Ehrlicher Hinweis statt Werten: Quelle fehlt, nichts zu zeigen, noch nicht geladen.
  let { symbol = "fa-plug-circle-xmark", titel, text = "" }: { symbol?: string; titel: string; text?: string } = $props();
</script>

<div class="hinweis-blatt" role="status">
  <i class="fa-solid {symbol}"></i>
  <div><b>{titel}</b>{#if text}<small>{text}</small>{/if}</div>
</div>
