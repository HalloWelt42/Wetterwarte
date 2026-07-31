<script lang="ts">
  import Brett from "./Brett.svelte";
  import { ui } from "./ui.svelte";
  import { wetter } from "./wetter.svelte";
  import { stil } from "./stil.svelte";
  import FrischeRing from "./FrischeRing.svelte";
</script>

<section class="inhalt">
  <div class="werkzeuge">
    <div class="orts-titel">{wetter.ort} <FrischeRing /></div>
    <span class="luecke"></span>
    <button class="knopf klein" class:primaer={stil.atmo} onclick={() => (stil.atmo = !stil.atmo)}><i class="fa-solid fa-image"></i> Atmosphäre</button>
    <button class="knopf klein" onclick={() => (ui.layouts = true)}><i class="fa-solid fa-pen"></i> Layout bearbeiten</button>
  </div>
  <Brett />
</section>
