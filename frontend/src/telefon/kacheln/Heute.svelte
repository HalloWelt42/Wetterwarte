<script lang="ts">
  // Heute: Tagesspanne als Band von Tief bis Hoch mit Jetzt-Marke, Regen (Wahrscheinlichkeit und ab
  // wann, nur für den Rest des Tages) und Sonne (bis wann bzw. ab wann). Formen 2x1 und 3x1.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { stunde, teile, uhrzeit, wochentagKurz } from "../../kern/zeit";
  import { grad, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import { regenAb } from "../rechnen";
  import KKopf from "../KKopf.svelte";
  import { naechstesSonnenereignis, restStundenHeute } from "./tageslauf";

  let { kachel, daten, zone }: KachelProps = $props();

  const MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];

  const f = $derived(form(kachel));
  const tag = $derived(daten.tage[0] ?? null);
  const temp = $derived(daten.jetzt?.temp ?? null);
  const lage = $derived.by(() => {
    if (!tag || temp === null) return null;
    const p = ((temp - tag.tief) / (tag.hoch - tag.tief || 1)) * 100;
    return Math.min(100, Math.max(0, p));
  });
  const regen = $derived(regenAb(daten, restStundenHeute(daten, zone)));
  const regenJetzt = $derived(regen === daten.stunden[daten.jetzt_index]);
  const sonne = $derived(naechstesSonnenereignis(daten, uhr.jetzt));
  const sonneText = $derived(sonne ? `${sonne.art === "unter" ? "bis" : "ab"} ${uhrzeit(sonne.zeit, zone)}` : "");
  const datum = $derived.by(() => {
    const t = teile(daten.zeit, zone);
    return `${wochentagKurz(daten.zeit, zone)} ${t.tag}. ${MONATE[t.monat - 1]}`;
  });
</script>

{#snippet regenZeile()}
  <span>
    <i class="fa-solid fa-umbrella c-regen"></i>
    {#if !regen}
      heute trocken
    {:else}
      <b>{regen.regen_wahrsch !== null ? `${zahl(regen.regen_wahrsch)} %` : `${zahl(regen.regen_mm, 1)} mm`}</b>
      {regenJetzt ? "jetzt" : `ab ${stunde(regen.zeit, zone)} Uhr`}
    {/if}
  </span>
{/snippet}

<KKopf titel="Heute" symbol="fa-calendar-day" rechts={f === "2x1" ? (sonne ? sonneText : "") : datum} rechtsSymbol={f === "2x1" && sonne ? "fa-sun" : ""} />
<div class="k-reihe mitte">
  {#if tag}
    <div class="spanne" style="flex: 1">
      <div class="wert halb" style="color: var(--text-2)"><b>{grad(tag.tief)}</b></div>
      <span class="band">
        <span style="left: 0%; right: 0%"></span>
        {#if lage !== null && temp !== null}
          <i style="left: {lage}%"></i>
          <em class="entbehrlich" style="left: {Math.min(85, Math.max(15, lage))}%">{f === "3x1" ? "jetzt " : ""}{grad(temp)}</em>
        {/if}
      </span>
      <div class="wert halb {tempKlasse(tag.hoch)}"><b>{grad(tag.hoch)}</b></div>
    </div>
  {:else}
    <div class="k-hinweis">keine Angabe</div>
  {/if}
</div>
{#if f === "2x1"}
  <div class="unter">{@render regenZeile()}</div>
{:else}
  <div class="unter zeile-3">
    {@render regenZeile()}
    {#if sonne}<span class="ans-ende"><i class="fa-solid fa-sun c-sonne"></i> {sonne.art === "unter" ? "bis" : "ab"} <b>{uhrzeit(sonne.zeit, zone)}</b></span>{/if}
  </div>
{/if}

<style>
  .zeile-3 {
    display: flex;
    gap: 16px;
  }
</style>
