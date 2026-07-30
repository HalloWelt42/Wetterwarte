<script lang="ts">
  import { meteocon } from "../../icons";
  import { aktuell } from "../../platzhalter";
  import { nutzeOrtDaten } from "../../ortdaten.svelte";
  import { tipp } from "../../tipp";
  import { begriffe } from "../../begriffe";

  let { conf = {}, ort }: { conf?: Record<string, any>; ort: string } = $props();

  // Jede Kachel holt ihre Daten eigenstaendig fuer ihren Ort (Standard: aktiver Ort).
  const daten = nutzeOrtDaten(() => ort);

  // Pro-Kachel-Einstellungen (mit sinnvollen Standardwerten, wenn nicht gesetzt).
  const kennzahlen = $derived((conf.kennzahlen as string[]) ?? ["feuchte", "wind", "druck", "sicht", "taupunkt", "bewoelkung"]);

  const jetzt = $derived(daten.basis?.aktuell ?? aktuell);
</script>

<div class="aktuell-haupt">
  <img class="mc gross" src={meteocon(jetzt.icon)} alt="" />
  <div class="aktuell-block">
    <span class="temp temp-gross {jetzt.tempKlasse}">{jetzt.temperatur}&deg;</span>
    <span class="aktuell-zustand">{jetzt.zustandText}</span>
    <span class="aktuell-gefuehlt">Gefühlt {jetzt.gefuehlt}&deg; &middot; Tageshoch {jetzt.tageshoch}&deg;</span>
  </div>
</div>
<div class="kv-gitter">
  {#if kennzahlen.includes("feuchte")}<div class="kv"><i class="fa-solid fa-droplet"></i><span class="kv-txt"><span class="kv-wert">{jetzt.feuchte} %</span><span class="kv-lab">Feuchte</span></span></div>{/if}
  {#if kennzahlen.includes("wind")}<div class="kv"><i class="fa-solid fa-wind"></i><span class="kv-txt"><span class="kv-wert">{jetzt.wind} km/h</span><span class="kv-lab">Wind {jetzt.windRichtung}</span></span></div>{/if}
  {#if kennzahlen.includes("druck")}<div class="kv"><i class="fa-solid fa-gauge"></i><span class="kv-txt"><span class="kv-wert">{jetzt.druck} hPa</span><span class="kv-lab">Druck</span></span></div>{/if}
  {#if kennzahlen.includes("sicht")}<div class="kv"><i class="fa-solid fa-eye"></i><span class="kv-txt"><span class="kv-wert">{jetzt.sicht} km</span><span class="kv-lab">Sicht</span></span></div>{/if}
  {#if kennzahlen.includes("taupunkt")}<div class="kv"><i class="fa-solid fa-temperature-half"></i><span class="kv-txt"><span class="kv-wert">{jetzt.taupunkt}&deg;</span><span class="kv-lab" use:tipp={begriffe.taupunkt}>Taupunkt</span></span></div>{/if}
  {#if kennzahlen.includes("bewoelkung")}<div class="kv"><i class="fa-solid fa-cloud"></i><span class="kv-txt"><span class="kv-wert">{jetzt.bewoelkung} %</span><span class="kv-lab">Bewölkung</span></span></div>{/if}
</div>
