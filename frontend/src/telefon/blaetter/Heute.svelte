<script lang="ts">
  // Blatt Heute: Tagesüberblick mit Zustand, Spanne von Tief bis Hoch mit Jetzt-Marke, Regen,
  // Wind, Sonne und UV des Tages und dem Verlauf der Stunden von heute.
  import type { KachelProps } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { stunde, uhrzeit } from "../../kern/zeit";
  import { zustandText } from "../../kern/wetterbild";
  import { beaufort, grad, uvWort, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import { regenAb } from "../rechnen";
  import Linie from "../mikro/Linie.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";
  import Symbol from "../Symbol.svelte";
  import Achse from "./bausteine/Achse.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { dauerLang, kalendertag } from "./datum";
  import { erklaerung } from "./erklaerungen";
  import { uvZahl } from "./worte";

  let { daten, zone }: KachelProps = $props();

  const t = $derived(daten.tage[0] ?? null);
  const j = $derived(daten.jetzt);
  const mm = (v: number) => zahl(v, v > 0 && v < 10 ? 1 : 0);
  const anteil = (v: number) => (t ? Math.min(100, Math.max(0, ((v - t.tief) / (t.hoch - t.tief || 1)) * 100)) : 0);

  // Regen heute: erste nennenswerte Stunde des Tages (gleiche Schwelle wie die Kacheln)
  const regen = $derived.by(() => {
    const s = regenAb(daten);
    return s && t && kalendertag(s.zeit, zone) === t.datum ? s : null;
  });
  // Zeile unter dem Untergang: Restzeit hell, sonst der Aufgang des Tages
  const sonneText = $derived.by(() => {
    if (!t?.sonnenaufgang || !t.sonnenuntergang) return "";
    const jetzt = uhr.jetzt.getTime();
    const auf = uhrzeit(t.sonnenaufgang, zone);
    const u = new Date(t.sonnenuntergang).getTime();
    if (jetzt < new Date(t.sonnenaufgang).getTime()) return `Untergang; Aufgang um ${auf}`;
    return jetzt < u ? `Untergang, noch ${dauerLang((u - jetzt) / 1000)} hell` : `Untergang; Aufgang war um ${auf}`;
  });

  // Verlauf: die Stunden dieses Kalendertags (die Daten reichen 6 Stunden zurück)
  const verlauf = $derived(t ? daten.stunden.filter((s) => kalendertag(s.zeit, zone) === t.datum) : []);
  const jetztIndex = $derived(verlauf.findIndex((s) => s.zeit === daten.stunden[daten.jetzt_index]?.zeit));
  const marken = $derived(
    verlauf
      .map((s, i) => ({ s, i }))
      .filter(({ i }) => i % 3 === 0)
      .map(({ s, i }) => ({ anteil: (i + 0.5) / verlauf.length, text: String(stunde(s.zeit, zone)).padStart(2, "0"), an: i === jetztIndex })),
  );
</script>

{#if !t}
  <div class="abschnitt">
    <Hinweis titel="Tageswerte fehlen" text="Die Wetterquelle hat gerade keine Tage geliefert. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      <Symbol code={t.code} />
      <div class="held-text">
        <div class="riesen-zahl {tempKlasse(t.hoch)}">{grad(t.hoch)}<small>/ {grad(t.tief)}</small></div>
        <div class="held-satz">{zustandText(t.code)}</div>
        <div class="held-unter">Hoch <b>{grad(t.hoch)}</b> · Tief <b>{grad(t.tief)}</b>{#if j}{" "}· jetzt <b>{grad(j.temp)}</b>{/if}</div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Tagesspanne</h3>
    <div class="tafel">
      <div class="spanne mit-marke">
        <b class="spanne-wert t-tief">{grad(t.tief)}</b>
        <span class="band">
          <span style="left: 0%; right: 0%"></span>
          {#if j}
            <i style="left: {anteil(j.temp)}%"></i>
            <em style="left: {Math.min(85, Math.max(15, anteil(j.temp)))}%">jetzt {grad(j.temp)}</em>
          {/if}
        </span>
        <b class="spanne-wert {tempKlasse(t.hoch)}">{grad(t.hoch)}</b>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Der Tag</h3>
    <div class="werte-gitter">
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-umbrella"></i>Regen</div>
        <div class="wg-wert">{mm(t.regen_mm)}<small>mm</small></div>
        <div class="wg-unter">
          {#if t.regen_wahrsch !== null}{zahl(t.regen_wahrsch)}&nbsp;%{:else}Wahrscheinlichkeit unbekannt{/if}{#if regen}, ab <b>{stunde(regen.zeit, zone)} Uhr</b>{/if}
        </div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-wind"></i>Wind</div>
        <div class="wg-wert">{zahl(t.wind_max)}<small>km/h</small></div>
        <div class="wg-unter">Böen bis <b>{zahl(t.boeen_max)}</b>, Stärke {beaufort(t.wind_max)}</div>
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-sun"></i>Sonne</div>
        {#if t.sonnenaufgang && t.sonnenuntergang}
          <div class="wg-wert">{uhrzeit(t.sonnenuntergang, zone)}</div>
          <div class="wg-unter">{sonneText}</div>
        {:else}
          <div class="wg-wert leer">keine Angabe</div>
        {/if}
      </div>
      <div class="wg">
        <div class="wg-kopf"><i class="fa-solid fa-sun"></i>UV</div>
        <div class="wg-wert">{uvZahl(t.uv_max)}</div>
        <div class="wg-unter">höchstens, {uvWort(t.uv_max)}</div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Verlauf heute</h3>
    <div class="tafel">
      {#if verlauf.length > 1}
        <div class="tafel-kopf">
          <b>Temperatur und Regen</b>
          <span>{uhrzeit(verlauf[0].zeit, zone)} bis {uhrzeit(verlauf[verlauf.length - 1].zeit, zone)} Uhr</span>
        </div>
        <div class="diagramm mittel verlauf" style="--n: {verlauf.length}">
          <Linie werte={verlauf.map((s) => s.temp)} farbe="temp" beschriften={3} jetzt={jetztIndex} />
        </div>
        <div class="diagramm flach"><Saeulen werte={verlauf.map((s) => s.regen_mm)} max={2} hervor={jetztIndex >= 0 ? jetztIndex : undefined} /></div>
        <Achse {marken} />
        <div class="tafel-fuss">Säulen: Regen in mm je Stunde. Gezeigt sind die Stunden von heute, die vorliegen.</div>
      {:else}
        <Hinweis symbol="fa-chart-line" titel="Kein Verlauf" text="Für heute liegen keine Stundenwerte mehr vor." />
      {/if}
    </div>
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>

  <Begriffe liste={[erklaerung.regenMenge, erklaerung.uv]} />
{/if}

<style>
  /* Verlauf um eine halbe Spalte eingerückt, damit die Punkte über ihren Regensäulen stehen */
  .verlauf {
    margin: 0 calc(100% / (2 * var(--n)) - 5px);
  }
  .spanne-wert {
    flex: none;
    font-size: var(--s26);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }
  .t-tief {
    color: var(--text-2);
  }
  /* Platz für die Jetzt-Beschriftung über dem Band */
  .mit-marke {
    padding-top: calc(var(--s13) + 10px);
  }
</style>
