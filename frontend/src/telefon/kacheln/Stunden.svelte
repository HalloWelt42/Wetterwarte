<script lang="ts">
  // Stunden: 2x1 vier, 3x1 sechs Stunden als Spalten; 3x2 zwölf Stunden als Verlauf mit Symbolen und
  // Regensäulen; 3x3 vierundzwanzig Stunden, zusätzlich Regenwahrscheinlichkeit und Wind.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { stunde } from "../../kern/zeit";
  import { grad, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import { kommende, regenAbText } from "../rechnen";
  import KKopf from "../KKopf.svelte";
  import Symbol from "../Symbol.svelte";
  import Linie from "../mikro/Linie.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";

  let { kachel, daten, zone }: KachelProps = $props();

  const f = $derived(form(kachel));
  const anzahl = $derived(f === "2x1" ? 4 : f === "3x1" ? 6 : f === "3x2" ? 12 : 24);
  const reihe = $derived(kommende(daten, anzahl));
  const titel = $derived(f === "3x2" ? "12 Stunden" : f === "3x3" ? "24 Stunden" : "Stunden");
  const zusatz = $derived(regenAbText(daten, f !== "2x1"));
  const schritt = 3; // 24 Stunden: jede dritte beschriftet
  const marken = $derived(reihe.map((s, i) => ({ s, i })).filter(({ i }) => i % schritt === 0));
</script>

<KKopf {titel} rechts={zusatz} />
{#if f === "2x1" || f === "3x1"}
  <div class="spalten">
    {#each reihe as s, i}
      <div class="sp">
        <span class="sp-zeit">{i === 0 ? "Jetzt" : stunde(s.zeit, zone)}</span>
        <Symbol code={s.code} tag={s.tag} />
        <span class="sp-wert {tempKlasse(s.temp)}">{grad(s.temp)}</span>
        <span class="sp-klein entbehrlich-gross">{(s.regen_wahrsch ?? 0) >= 20 ? `${zahl(s.regen_wahrsch ?? 0)} %` : ""}</span>
      </div>
    {/each}
  </div>
{:else if f === "3x2"}
  <div class="spalten fest" style="height: 32px; margin-top: 6px">
    {#each reihe as s}<div class="sp"><Symbol code={s.code} tag={s.tag} /></div>{/each}
  </div>
  <div class="mikro-rand"><Linie werte={reihe.map((s) => s.temp)} farbe="temp" beschriften={2} jetzt={0} /></div>
  <div style="height: 26px; margin-top: 4px; flex: none"><Saeulen werte={reihe.map((s) => s.regen_mm)} max={2} /></div>
  <div class="spalten fest" style="margin-top: 3px">
    {#each reihe as s, i}<span class="sp-zeit" style={i === 0 ? "color: var(--text)" : ""}>{stunde(s.zeit, zone)}</span>{/each}
  </div>
{:else}
  <div class="achse-n" style="--n: {reihe.length}; height: 30px; margin-top: 8px">
    {#each marken as { s, i }}<span style="--i: {i}"><Symbol code={s.code} tag={s.tag} /></span>{/each}
  </div>
  <div class="mikro-rand"><Linie werte={reihe.map((s) => s.temp)} farbe="temp" beschriften={schritt} jetzt={0} /></div>
  <div style="height: 30px; margin-top: 4px; flex: none"><Saeulen werte={reihe.map((s) => s.regen_mm)} max={2} /></div>
  <div class="achse-n" style="--n: {reihe.length}; height: calc(var(--s13) * 1.1); margin-top: 3px">
    {#each marken as { s, i }}<span class="sp-klein" style="--i: {i}">{(s.regen_wahrsch ?? 0) >= 20 ? `${zahl(s.regen_wahrsch ?? 0)} %` : ""}</span>{/each}
  </div>
  <div class="achse-n wind-pfeil entbehrlich" style="--n: {reihe.length}; height: calc(var(--s15) * 1.1 + var(--s13) * 1.1 + 2px); margin-top: 8px">
    {#each marken as { s, i }}<span style="--i: {i}"><i class="fa-solid fa-arrow-up" style="rotate: {s.wind_grad + 180}deg"></i><b>{zahl(s.wind)}</b></span>{/each}
  </div>
  <div class="achse-n" style="--n: {reihe.length}; height: calc(var(--s13) * 1.1); margin-top: 4px">
    {#each marken as { s, i }}<span class="sp-zeit" style="--i: {i}{i === 0 ? '; color: var(--text)' : ''}">{stunde(s.zeit, zone)}</span>{/each}
  </div>
{/if}

<style>
  /* Verlauf füllt die Restfläche; seitlich um eine halbe Spalte eingerückt, damit die Punkte über
     ihren Spalten stehen. */
  .mikro-rand {
    flex: 1;
    min-height: 0;
    display: flex;
    margin: 0 calc(100% / 24 - 4px);
  }
</style>
