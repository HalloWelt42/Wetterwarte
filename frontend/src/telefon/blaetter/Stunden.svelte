<script lang="ts">
  // Blatt Stunden: großer Temperaturverlauf der nächsten 24 Stunden mit Regensäulen und Achse,
  // darunter alle verfügbaren Stunden (bis 48) nach Tagen, mit Sonnenauf- und -untergang.
  import type { KachelProps } from "../kachelprops";
  import { stunde, uhrzeit } from "../../kern/zeit";
  import { grad, zahl } from "../format";
  import { kommende, regenAbText } from "../rechnen";
  import Linie from "../mikro/Linie.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";
  import Achse from "./bausteine/Achse.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import StundenListe from "./bausteine/StundenListe.svelte";
  import { kalendertag, tagNah } from "./datum";
  import { erklaerung } from "./erklaerungen";

  let { daten, zone }: KachelProps = $props();

  const reihe = $derived(kommende(daten, 25)); // jetzt und 24 Stunden
  const temps = $derived(reihe.map((s) => s.temp));
  const regen = $derived(reihe.map((s) => s.regen_mm));
  const lo = $derived(Math.min(...temps));
  const hi = $derived(Math.max(...temps));
  const regenText = $derived(regenAbText(daten));
  const meist = $derived(reihe.reduce((m, s) => (s.regen_mm > m.regen_mm ? s : m), reihe[0]));
  const heute = $derived(kalendertag(daten.zeit, zone));
  const marken = $derived(
    reihe
      .map((s, i) => ({ s, i }))
      .filter(({ i }) => i % 4 === 0)
      .map(({ s, i }) => ({ anteil: (i + 0.5) / reihe.length, text: i === 0 ? "Jetzt" : String(stunde(s.zeit, zone)).padStart(2, "0"), an: i === 0 })),
  );
  const ende = $derived(Math.min(daten.stunden.length, daten.jetzt_index + 48));
</script>

{#if reihe.length < 2}
  <div class="abschnitt">
    <Hinweis titel="Keine Stundenvorhersage" text="Die Wetterquelle hat gerade keine Stunden geliefert. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="tafel">
      <div class="tafel-kopf">
        <b>Nächste {reihe.length - 1} Stunden</b>
        <span>{grad(lo)} bis {grad(hi)} · {regenText || "kein Regen erwartet"}</span>
      </div>
      <div class="diagramm verlauf" style="--n: {reihe.length}"><Linie werte={temps} farbe="temp" beschriften={3} jetzt={0} /></div>
      <div class="diagramm flach"><Saeulen werte={regen} max={2} /></div>
      <Achse {marken} />
      <div class="tafel-fuss">
        {#if meist && meist.regen_mm > 0}
          Säulen: Regen in mm je Stunde, am meisten {tagNah(kalendertag(meist.zeit, zone), heute)} um {uhrzeit(meist.zeit, zone)} Uhr mit
          <b>{zahl(meist.regen_mm, 1)} mm</b>.
        {:else}
          Säulen: Regen in mm je Stunde. In den nächsten 24 Stunden fällt keiner.
        {/if}
      </div>
    </div>
  </div>

  <StundenListe {daten} {zone} von={daten.jetzt_index} bis={ende} />

  <div class="abschnitt">
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
  <Begriffe liste={[erklaerung.regenMenge]} />
{/if}

<style>
  /* Verlauf um eine halbe Spalte eingerückt, damit die Punkte über ihren Regensäulen stehen
     (die Linie läuft 5 px vor dem Rand aus) */
  .verlauf {
    margin: 0 calc(100% / (2 * var(--n)) - 5px);
  }
</style>
