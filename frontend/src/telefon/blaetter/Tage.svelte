<script lang="ts">
  // Blatt Tage: alle Vorhersagetage (bis 7) mit Temperaturband über die Spanne der Woche; jeder Tag
  // klappt auf zu Regen, Wind mit Böen, Sonne und UV.
  import type { KachelProps } from "../kachelprops";
  import { uhrzeit } from "../../kern/zeit";
  import { zustandText } from "../../kern/wetterbild";
  import { beaufort, grad, uvWort, zahl } from "../format";
  import { tempKlasse } from "../mikro/geometrie";
  import Symbol from "../Symbol.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { dauerLang, kalendertag, tagMonat, tageZwischen, wochentag } from "./datum";
  import { erklaerung } from "./erklaerungen";
  import { uvZahl } from "./worte";

  let { daten, zone }: KachelProps = $props();

  const tage = $derived(daten.tage.slice(0, 7));
  const lo = $derived(Math.min(...tage.map((t) => t.tief)));
  const hi = $derived(Math.max(...tage.map((t) => t.hoch)));
  const spanne = $derived(hi - lo || 1);
  const links = (t: number) => ((t - lo) / spanne) * 100;
  const jetzt = $derived(daten.jetzt?.temp ?? null);
  const heute = $derived(kalendertag(daten.zeit, zone));
  const mm = (v: number) => zahl(v, v > 0 && v < 10 ? 1 : 0);

  function name(datum: string): string {
    const d = tageZwischen(heute, datum);
    return d === 0 ? "Heute" : d === 1 ? "Morgen" : wochentag(datum);
  }
</script>

{#if !tage.length}
  <div class="abschnitt">
    <Hinweis titel="Keine Tagesvorhersage" text="Die Wetterquelle hat gerade keine Tage geliefert. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <h3>{tage.length} Tage · {grad(lo)} bis {grad(hi)} · Tag antippen für mehr</h3>
    <div class="zeilen">
      {#each tage as t, i (t.datum)}
        {@const p = t.regen_wahrsch}
        <details class="auf">
          <summary class="tag-z">
            <span class="tag">
              <b>{name(t.datum)}</b>
              <small>{tagMonat(t.datum)}{#if p !== null}{" "}· <span class="regen" class:matt={p < 30}>{zahl(p)}&nbsp;%</span>{/if}</small>
            </span>
            <Symbol code={t.code} />
            <span class="lo">{grad(t.tief)}</span>
            <span class="band">
              <span style="left: {links(t.tief)}%; right: {100 - links(t.hoch)}%"></span>
              {#if i === 0 && t.datum === heute && jetzt !== null}<i style="left: {Math.min(100, Math.max(0, links(jetzt)))}%"></i>{/if}
            </span>
            <span class="hi {tempKlasse(t.hoch)}">{grad(t.hoch)}</span>
            <i class="fa-solid fa-chevron-down"></i>
          </summary>
          <div class="auf-inhalt">
            <div class="zustand-tag">{zustandText(t.code)}</div>
            <div class="werte-gitter">
              <div class="wg">
                <div class="wg-kopf"><i class="fa-solid fa-umbrella"></i>Regen</div>
                <div class="wg-wert">{mm(t.regen_mm)}<small>mm</small></div>
                <div class="wg-unter">{p !== null ? `Wahrscheinlichkeit ${zahl(p)}\u00a0%` : "Wahrscheinlichkeit unbekannt"}</div>
              </div>
              <div class="wg">
                <div class="wg-kopf"><i class="fa-solid fa-wind"></i>Wind</div>
                <div class="wg-wert">{zahl(t.wind_max)}<small>km/h</small></div>
                <div class="wg-unter">Böen bis <b>{zahl(t.boeen_max)}</b>, Stärke {beaufort(t.wind_max)}</div>
              </div>
              <div class="wg">
                <div class="wg-kopf"><i class="fa-solid fa-sun"></i>Sonne</div>
                {#if t.sonnenaufgang && t.sonnenuntergang}
                  <div class="wg-wert">{uhrzeit(t.sonnenaufgang, zone)}</div>
                  <div class="wg-unter">bis <b>{uhrzeit(t.sonnenuntergang, zone)}</b>, {dauerLang(t.tageslaenge_s)} hell</div>
                {:else}
                  <div class="wg-wert leer">keine Angabe</div>
                  <div class="wg-unter">Tageslänge {dauerLang(t.tageslaenge_s)}</div>
                {/if}
              </div>
              <div class="wg">
                <div class="wg-kopf"><i class="fa-solid fa-sun"></i>UV</div>
                <div class="wg-wert">{uvZahl(t.uv_max)}</div>
                <div class="wg-unter">höchstens, {uvWort(t.uv_max)}</div>
              </div>
            </div>
          </div>
        </details>
      {/each}
    </div>
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>

  <Begriffe liste={[erklaerung.tagesband, erklaerung.regenMenge, erklaerung.uv]} />
{/if}

<style>
  .zustand-tag {
    margin: 0 0 8px 2px;
    font-weight: 600;
    color: var(--text-2);
  }
</style>
