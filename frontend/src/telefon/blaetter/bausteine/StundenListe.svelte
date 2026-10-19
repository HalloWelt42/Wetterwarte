<script lang="ts">
  // Stunden als Zeilen, nach Tagen gruppiert: Uhrzeit, Symbol, Temperatur, Regen in % und mm,
  // Wind mit Richtungspfeil (zeigt, wohin der Wind weht). Sonnenauf- und -untergang als eigene Zeilen.
  import type { Kompakt } from "../../typen";
  import { uhr } from "../../../kern/uhr.svelte";
  import { uhrzeit } from "../../../kern/zeit";
  import { grad, zahl } from "../../format";
  import { tempKlasse } from "../../mikro/geometrie";
  import Symbol from "../../Symbol.svelte";
  import { stundenNachTagen } from "../stundenliste";

  let { daten, zone, von, bis }: { daten: Kompakt; zone: string; von: number; bis: number } = $props();

  // Die Liste folgt der Minute, nicht jeder Sekunde der Uhr.
  const minute = $derived(Math.floor(uhr.jetzt.getTime() / 60_000));
  const gruppen = $derived(stundenNachTagen(daten, zone, von, bis, new Date(minute * 60_000)));
</script>

{#each gruppen as g (g.datum)}
  <div class="abschnitt">
    <h3>{g.titel} · {g.stunden} {g.stunden === 1 ? "Stunde" : "Stunden"}</h3>
    <div class="zeilen">
      {#each g.eintraege as e (e.art === "stunde" ? `s${e.stunde.zeit}` : `e${e.zeit}`)}
        {#if e.art === "stunde"}
          {@const s = e.stunde}
          {@const p = s.regen_wahrsch}
          <div class="zeile stunde">
            <span class="uhr">{e.jetzt ? "Jetzt" : uhrzeit(s.zeit, zone)}</span>
            <Symbol code={s.code} tag={s.tag} />
            <span class="temp {tempKlasse(s.temp)}">{grad(s.temp)}</span>
            <span class="nass">
              {#if p !== null}<span class={p >= 30 ? "c-regen" : "matt"}>{zahl(p)}&nbsp;%</span>{/if}
              <small>{zahl(s.regen_mm, s.regen_mm > 0 && s.regen_mm < 10 ? 1 : 0)} mm</small>
            </span>
            <span class="wind-w">
              <i class="fa-solid fa-arrow-up pfeil-w" style="rotate: {s.wind_grad + 180}deg"></i>{zahl(s.wind)}<small>km/h</small>
            </span>
          </div>
        {:else}
          <div class="zeile stunde ereignis">
            <span class="uhr">{uhrzeit(e.zeit, zone)}</span>
            <Symbol name={e.aufgang ? "sunrise" : "sunset"} />
            <span class="ereignis-text">{e.aufgang ? "Sonnenaufgang" : "Sonnenuntergang"}</span>
          </div>
        {/if}
      {/each}
    </div>
  </div>
{/each}
