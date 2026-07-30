<script lang="ts">
  import { registry } from "./kacheln/registry";
  import KachelKoerper from "./kacheln/KachelKoerper.svelte";
  import { ui } from "./ui.svelte";
  import { wetter } from "./wetter.svelte";
  import { konf } from "./kachelConf.svelte";

  let {
    typ,
    id,
    conf = {},
    onEntfernen,
  }: { typ: string; id: string; conf?: Record<string, unknown>; onEntfernen: () => void } = $props();

  const def = $derived(registry[typ]);
  const eigenerTitel = $derived((conf.titel as string) || "");
  const titel = $derived(eigenerTitel || def?.titel);
  const unter = $derived(def?.unter === "ORT" ? wetter.ort : def?.unter);

  function oeffneEinstellungen(): void {
    konf.id = id;
    konf.typ = typ;
    konf.werte = { ...conf };
    ui.einstellungen = true;
  }
</script>

<div class="kachel-w">
  <div class="kw-kopf">
    <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
    <span class="kw-titel">{titel}{#if unter && !eigenerTitel}&nbsp;<span class="ort">{unter}</span>{/if}</span>
    <span class="kw-werkz">
      <button class="icon-knopf" title="Einstellungen" aria-label="Einstellungen" onclick={oeffneEinstellungen}><i class="fa-solid fa-sliders"></i></button>
      <button class="icon-knopf gefahr" title="Kachel entfernen" aria-label="Kachel entfernen" onclick={onEntfernen}><i class="fa-solid fa-xmark"></i></button>
    </span>
  </div>
  <div class="kw-koerper"><KachelKoerper {typ} {conf} /></div>
  <span class="kw-griff"></span>
</div>
