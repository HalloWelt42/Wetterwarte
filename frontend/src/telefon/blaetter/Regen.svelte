<script lang="ts">
  // Blatt Regen: Satz zu den nächsten 2 Stunden, Säulen je Viertelstunde mit Achse, Hinweis zur
  // Quelle (Kurzfristvorhersage aus dem Wettermodell), danach der Regen der nächsten Stunden.
  import type { KachelProps } from "../kachelprops";
  import { uhrzeit } from "../../kern/zeit";
  import { zahl } from "../format";
  import { regenAb } from "../rechnen";
  import { zeige } from "../ansicht.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";
  import Symbol from "../Symbol.svelte";
  import Achse from "./bausteine/Achse.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import StundenListe from "./bausteine/StundenListe.svelte";
  import { dauerLang, kalendertag, tagNah } from "./datum";
  import { erklaerung } from "./erklaerungen";
  import { regenStaerke } from "./worte";

  let { daten, zone }: KachelProps = $props();

  const r = $derived(daten.regen);
  const j = $derived(daten.jetzt);
  // Die Viertelstunden beginnen mit der laufenden Viertelstunde der aktuellen Werte
  const start = $derived(new Date(j?.zeit ?? daten.zeit).getTime());
  const nach = (min: number) => new Date(start + min * 60_000).toISOString();
  const heute = $derived(kalendertag(daten.zeit, zone));
  const mm = (v: number) => zahl(v, v > 0 && v < 10 ? 1 : 0);

  const iMax = $derived(r ? r.werte.indexOf(r.max_mm_h) : -1);
  const skala = $derived(r ? Math.max(1, Math.ceil(r.max_mm_h)) : 1);
  // Regen bis Mitternacht aus der Stundenvorhersage (laufende Stunde eingeschlossen)
  const restHeute = $derived(
    daten.stunden.slice(daten.jetzt_index).filter((s) => kalendertag(s.zeit, zone) === heute).reduce((a, s) => a + s.regen_mm, 0),
  );
  // Regen nach den 2 Stunden der Kurzfristvorhersage (gleiche Schwelle wie die Kacheln)
  const spaeter = $derived(regenAb({ ...daten, jetzt_index: daten.jetzt_index + 2 }));
  const spaeterWann = $derived.by(() => {
    if (!spaeter) return "";
    const tag = tagNah(kalendertag(spaeter.zeit, zone), heute);
    return `${tag === "heute" ? "" : `${tag} `}${uhrzeit(spaeter.zeit, zone)} Uhr`;
  });
  const ende = $derived(Math.min(daten.stunden.length, daten.jetzt_index + 14));
</script>

{#if !r}
  <div class="abschnitt">
    <Hinweis titel="Kurzfristvorhersage fehlt" text="Die Wetterquelle antwortet gerade nicht. Es werden keine Ersatzwerte gezeigt." />
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      {#if j}<Symbol code={j.code} tag={j.tag} />{/if}
      <div class="held-text">
        {#if r.beginn_min === 0}
          {#if r.ende_min !== null}
            <div class="riesen-zahl c-regen">{uhrzeit(nach(r.ende_min), zone)}<small>Uhr</small></div>
            <div class="held-satz">Es regnet, Ende in {dauerLang(r.ende_min * 60)}</div>
          {:else}
            <div class="riesen-zahl c-regen">{zahl(r.max_mm_h, 1)}<small>mm/h</small></div>
            <div class="held-satz">Es regnet die nächsten 2 Stunden</div>
          {/if}
        {:else if r.beginn_min !== null}
          <div class="riesen-zahl c-regen">{uhrzeit(nach(r.beginn_min), zone)}<small>Uhr</small></div>
          <div class="held-satz">Regenbeginn in {dauerLang(r.beginn_min * 60)}</div>
        {:else}
          <div class="riesen-zahl mittel">trocken</div>
          <div class="held-satz">in den nächsten 2 Stunden</div>
        {/if}
        <div class="held-unter">
          {#if r.beginn_min === null}
            {#if spaeter}Danach Regen ab <b>{spaeterWann}</b>{#if spaeter.regen_wahrsch !== null}, {zahl(spaeter.regen_wahrsch)}&nbsp;%{/if}.
            {:else}Auch danach ist in den nächsten 24 Stunden kein Regen in Sicht.{/if}
          {:else}
            Höchstens <b>{zahl(r.max_mm_h, 1)} mm/h</b>, {regenStaerke(r.max_mm_h)}.
          {/if}
          Bis Mitternacht <b>{mm(restHeute)} mm</b>.
        </div>
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Nächste 2 Stunden</h3>
    <div class="tafel">
      <div class="tafel-kopf"><b>Kurzfristvorhersage</b><span>je {r.schritt_min} Minuten · Skala bis {skala} mm/h</span></div>
      <div class="diagramm mittel">
        <Saeulen werte={r.werte} max={skala} />
        {#if r.max_mm_h <= 0}<div class="im-feld">kein Regen</div>{/if}
      </div>
      <Achse marken={[{ anteil: 0, text: "Jetzt", an: true }, { anteil: 0.5, text: "+1 h" }, { anteil: 1, text: "+2 h" }]} />
      <div class="tafel-fuss">
        {#if r.max_mm_h > 0 && iMax >= 0}
          Höchstens <b>{zahl(r.max_mm_h, 1)} mm/h</b> gegen {uhrzeit(nach(iMax * r.schritt_min), zone)} Uhr, das ist {regenStaerke(r.max_mm_h)}.
        {:else}
          In den nächsten 2 Stunden fällt nach dem Modell kein Regen.
        {/if}
        Danach gilt die Stundenvorhersage, unten nach Tagen.
      </div>
    </div>
  </div>

  <StundenListe {daten} {zone} von={daten.jetzt_index + 2} bis={ende} />

  <div class="abschnitt">
    <h3>Quelle</h3>
    <div class="zeilen">
      <div class="zeile">
        <span class="sym"><i class="fa-solid fa-chart-column"></i></span>
        <div class="haupt"><b>Kurzfristvorhersage aus dem Wettermodell</b><small>in Viertelstunden für 2 Stunden, danach die Stundenvorhersage</small></div>
      </div>
      <details class="auf erkl">
        <summary><i class="fa-solid fa-circle-info"></i><span>{erklaerung.kurzfrist.titel}</span><i class="fa-solid fa-chevron-down"></i></summary>
        <p>{erklaerung.kurzfrist.text}</p>
      </details>
      <details class="auf erkl">
        <summary><i class="fa-solid fa-circle-info"></i><span>{erklaerung.regenMenge.titel}</span><i class="fa-solid fa-chevron-down"></i></summary>
        <p>{erklaerung.regenMenge.text}</p>
      </details>
      <button type="button" class="zeile radar" onclick={() => zeige("karte")}>
        <span class="sym"><i class="fa-solid fa-map"></i></span>
        <div class="haupt"><b>Auf der Karte ansehen</b><small>Regenradar mit Abspielleiste</small></div>
        <span class="rechts"><i class="fa-solid fa-chevron-right"></i></span>
      </button>
    </div>
    <Stand bereich={daten.bereiche.basis} {zone} />
  </div>
{/if}

<style>
  .radar {
    width: 100%;
    text-align: left;
  }
</style>
