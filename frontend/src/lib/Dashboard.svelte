<script lang="ts">
  import Brett from "./Brett.svelte";
  import { ui } from "./ui.svelte";
</script>

<section class="inhalt">
  <div class="werkzeuge">
    <div class="orts-titel">Köln <small>Sachsen-Anhalt &middot; aktualisiert vor 3 Min</small></div>
    <span class="luecke"></span>
    <button class="knopf klein" onclick={() => (ui.layouts = true)}><i class="fa-solid fa-pen"></i> Layout bearbeiten</button>
  </div>
  <Brett />
</section>
