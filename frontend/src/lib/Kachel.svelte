<script lang="ts">
  import { registry } from "./kacheln/registry";
  import KachelKoerper from "./kacheln/KachelKoerper.svelte";
  import { ui } from "./ui.svelte";
  import { wetter } from "./wetter.svelte";

  let { typ, onEntfernen }: { typ: string; onEntfernen: () => void } = $props();

  const def = $derived(registry[typ]);
  const unter = $derived(def?.unter === "ORT" ? wetter.ort : def?.unter);
</script>

<div class="kachel-w">
  <div class="kw-kopf">
    <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
    <span class="kw-titel">{def?.titel}{#if unter}&nbsp;<span class="ort">{unter}</span>{/if}</span>
    <span class="kw-werkz">
      <button class="icon-knopf" title="Einstellungen" onclick={() => (ui.einstellungen = def?.titel ?? "")}><i class="fa-solid fa-sliders"></i></button>
      <button class="icon-knopf gefahr" title="Kachel entfernen" onclick={onEntfernen}><i class="fa-solid fa-xmark"></i></button>
    </span>
  </div>
  <div class="kw-koerper"><KachelKoerper {typ} /></div>
  <span class="kw-griff"></span>
</div>
