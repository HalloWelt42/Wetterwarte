<script lang="ts">
  // Jetzt: Temperatur, Zustand, gefühlt, Hoch und Tief. Formen 1x1, 2x1, 3x1, 2x2, 3x2.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { zustandText } from "../../kern/wetterbild";
  import { grad, richtung, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import { heute, regenAb } from "../rechnen";
  import { stunde } from "../../kern/zeit";
  import KKopf from "../KKopf.svelte";
  import Symbol from "../Symbol.svelte";

  let { kachel, daten, zone }: KachelProps = $props();

  const j = $derived(daten.jetzt!);
  const f = $derived(form(kachel));
  const tag = $derived(heute(daten));
  const regen = $derived(regenAb(daten));
</script>

<KKopf titel="Jetzt" />
{#if f === "1x1" || f === "2x2"}
  <Symbol code={j.code} tag={j.tag} klasse="mc-ecke" />
  <div class="k-fuss">
    <div class="wert dick {tempKlasse(j.temp)}"><b>{grad(j.temp)}</b></div>
    {#if f === "1x1"}
      <div class="unter">gefühlt <b>{grad(j.gefuehlt)}</b></div>
    {:else}
      <div class="zustand">{zustandText(j.code)}</div>
      <div class="kz-reihe" style="margin-top: 8px">
        <div class="kz"><b>{grad(j.gefuehlt)}</b><small>gefühlt</small></div>
        {#if tag}<div class="kz"><b>{grad(tag.hoch)}</b><small>Hoch</small></div>
          <div class="kz"><b>{grad(tag.tief)}</b><small>Tief</small></div>{/if}
      </div>
    {/if}
  </div>
{:else if f === "2x1" || f === "3x1"}
  <div class="k-reihe mitte">
    <div class="wert dick {tempKlasse(j.temp)}"><b>{grad(j.temp)}</b></div>
    <Symbol code={j.code} tag={j.tag} stil="width: 50px; height: 50px" />
    {#if f === "2x1" && tag}
      <div class="k-block ans-ende zeilen-klein"><div>Hoch <b>{grad(tag.hoch)}</b></div><div>Tief <b>{grad(tag.tief)}</b></div></div>
    {:else if tag}
      <div class="kz-reihe ans-ende">
        <div class="kz"><b>{grad(j.gefuehlt)}</b><small>gefühlt</small></div>
        <div class="kz"><b>{grad(tag.hoch)}</b><small>Hoch</small></div>
        <div class="kz"><b>{grad(tag.tief)}</b><small>Tief</small></div>
      </div>
    {/if}
  </div>
  <div class="unter"><b>{zustandText(j.code)}</b></div>
{:else}
  <div class="k-reihe mitte">
    <Symbol code={j.code} tag={j.tag} stil="width: 72px; height: 72px; margin-left: -6px" />
    <div class="wert riesig {tempKlasse(j.temp)}"><b>{grad(j.temp)}</b></div>
    <div class="k-block ans-ende liste-klein">
      <div><i class="fa-solid fa-droplet"></i><b>{zahl(j.feuchte)} %</b></div>
      <div><i class="fa-solid fa-wind"></i><b>{zahl(j.wind)}</b> km/h {richtung(j.wind_grad)}</div>
      {#if regen}<div><i class="fa-solid fa-umbrella"></i><b>{zahl(regen.regen_wahrsch ?? 0)} %</b> ab {stunde(regen.zeit, zone)}</div>{/if}
    </div>
  </div>
  <div class="zustand">{zustandText(j.code)}</div>
  <div class="kz-reihe" style="margin-top: 6px">
    <div class="kz"><b>{grad(j.gefuehlt)}</b><small>gefühlt</small></div>
    {#if tag}<div class="kz"><b>{grad(tag.hoch)}</b><small>Hoch</small></div>
      <div class="kz"><b>{grad(tag.tief)}</b><small>Tief</small></div>{/if}
  </div>
{/if}
