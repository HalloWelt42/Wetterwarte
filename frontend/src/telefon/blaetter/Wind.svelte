<script lang="ts">
  // Blatt Wind: große Windrose mit Wert, Böen und Richtung in Worten, Stärke nach Beaufort, Verlauf
  // der nächsten 24 Stunden (Wind und Böen) und die Höchstwerte der nächsten Tage.
  import type { KachelProps } from "../kachelprops";
  import { stunde } from "../../kern/zeit";
  import { beaufort, richtungLang, windWort, zahl } from "../format";
  import { kommende } from "../rechnen";
  import Linie from "../mikro/Linie.svelte";
  import Windrose from "../mikro/Windrose.svelte";
  import Achse from "./bausteine/Achse.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Segmente from "./bausteine/Segmente.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { kalendertag, tageZwischen, tagLang } from "./datum";
  import { erklaerung } from "./erklaerungen";
  import { beaufortZeichen } from "./worte";

  let { daten, zone }: KachelProps = $props();

  const j = $derived(daten.jetzt);
  const boeenHeute = $derived(daten.tage[0]?.boeen_max ?? null);
  let ansicht = $state<"24" | "tage">("24");

  const reihe = $derived(kommende(daten, 25));
  const wind = $derived(reihe.map((s) => s.wind));
  const spalten = $derived(reihe.map((s, i) => ({ s, i })).filter(({ i }) => i % 3 === 0 && i < 24));
  const marken = $derived(
    reihe
      .map((s, i) => ({ s, i }))
      .filter(({ i }) => i % 6 === 0)
      .map(({ s, i }) => ({ anteil: i / Math.max(1, reihe.length - 1), text: i === 0 ? "Jetzt" : String(stunde(s.zeit, zone)).padStart(2, "0"), an: i === 0 })),
  );
  const heute = $derived(kalendertag(daten.zeit, zone));
  const tagName = (datum: string) => {
    const d = tageZwischen(heute, datum);
    return d === 0 ? "Heute" : d === 1 ? "Morgen" : tagLang(datum);
  };
</script>

{#if !j}
  <div class="abschnitt">
    <Hinweis titel="Windwerte fehlen" text="Die Wetterquelle antwortet gerade nicht. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      <div class="held-bild rose"><Windrose grad={j.wind_grad} /></div>
      <div class="held-text">
        <div class="riesen-zahl">{zahl(j.wind)}<small>km/h</small></div>
        <div class="held-satz">aus {richtungLang(j.wind_grad)}</div>
        <div class="held-unter">Böen <b>{zahl(j.boeen)} km/h</b> · {Math.round(j.wind_grad)}°</div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Stärke</h3>
    <div class="zeilen">
      <div class="zeile">
        <span class="sym"><i class="fa-solid fa-wind"></i></span>
        <div class="haupt"><b>Stärke {beaufort(j.wind)}: {windWort(j.wind)}</b><small>{beaufortZeichen(j.wind)}</small></div>
      </div>
      <div class="zeile">
        <span class="sym"><i class="fa-solid fa-wind"></i></span>
        <div class="haupt">
          <b>Böen Stärke {beaufort(j.boeen)}: {windWort(j.boeen)}</b>
          <small>{boeenHeute !== null ? `heute bis ${zahl(boeenHeute)} km/h` : beaufortZeichen(j.boeen)}</small>
        </div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Verlauf</h3>
    <Segmente optionen={[{ wert: "24", titel: "24 h" }, { wert: "tage", titel: `${daten.tage.length} Tage` }]} bind:wert={ansicht} />
    {#if ansicht === "24"}
      <div class="tafel">
        {#if reihe.length > 1}
          <div class="tafel-kopf">
            <b>Wind in km/h</b>
            <span>{zahl(Math.min(...wind))} bis {zahl(Math.max(...wind))} · Böen bis {zahl(Math.max(...reihe.map((s) => s.boeen)))}</span>
          </div>
          <div class="diagramm flach"><Linie werte={wind} farbe="--text-2" flaeche jetzt={0} einheit="" /></div>
          <Achse {marken} />
          <div class="spalten wind-sp" style="margin-top: 12px">
            {#each spalten as { s, i } (s.zeit)}
              <div class="sp">
                <span class="sp-zeit">{i === 0 ? "Jetzt" : String(stunde(s.zeit, zone)).padStart(2, "0")}</span>
                <i class="fa-solid fa-arrow-up" style="rotate: {s.wind_grad + 180}deg"></i>
                <span class="sp-wert">{zahl(s.wind)}</span>
                <span class="sp-boe">{zahl(s.boeen)}</span>
              </div>
            {/each}
          </div>
          <div class="tafel-fuss">Oben Wind, darunter Böen in km/h, alle 3 Stunden. Der Pfeil zeigt, wohin der Wind weht.</div>
        {:else}
          <Hinweis symbol="fa-chart-line" titel="Kein Verlauf" text="Die Wetterquelle hat gerade keine Stunden geliefert." />
        {/if}
      </div>
    {:else}
      <div class="zeilen">
        {#each daten.tage as t (t.datum)}
          <div class="zeile">
            <div class="haupt"><b>{tagName(t.datum)}</b><small>Stärke {beaufort(t.wind_max)}: {windWort(t.wind_max)}</small></div>
            <span class="rechts">
              <span class="zahl-r">{zahl(t.wind_max)} <small>km/h</small></span>
              <span class="zahl-r"><small>Böen</small> {zahl(t.boeen_max)}</span>
            </span>
          </div>
        {/each}
      </div>
    {/if}
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>

  <Begriffe liste={[erklaerung.beaufort, erklaerung.boeen]} />
{/if}

<style>
  .rose {
    width: 150px;
    height: 150px;
  }
</style>
