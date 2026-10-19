<script lang="ts">
  import { warnlage } from "../rechnen";
  // Blatt Warnungen: jede amtliche Warnung mit allen Einzelheiten (Stufe, Ereignis, Überschrift,
  // Zeitraum in Ortszeit, Beschreibung). Ohne Warnung ein ruhiger Hinweis; fällt die Quelle aus,
  // steht "Warnlage unbekannt" mit dem letzten Stand da, nie stillschweigend nichts.
  import type { KachelProps } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { kalendertag, tagNah, vorLang, zeitraum } from "./datum";
  import { erklaerung } from "./erklaerungen";

  let { daten, zone }: KachelProps = $props();

  const STUFEN = ["", "Wetterwarnung", "Markante Wetterwarnung", "Unwetterwarnung", "Extremes Unwetter"];

  const bereich = $derived(daten.bereiche.warnungen);
  const liste = $derived(daten.warnungen ?? []);
  const lage = $derived(warnlage(daten));
  const unbekannt = $derived(lage === "unbekannt");
  const heute = $derived(kalendertag(uhr.jetzt, zone));
  const standText = $derived.by(() => {
    if (!bereich.stand) return "Es liegt noch kein Stand vor.";
    const tag = tagNah(kalendertag(bereich.stand, zone), heute);
    return `Letzter Stand ${tag === "heute" ? "" : `${tag} `}${uhrzeit(bereich.stand, zone)} Uhr, ${vorLang(bereich.stand, uhr.jetzt)}.`;
  });
  const stufeKlasse = (s: number) => `stufe-${Math.min(4, Math.max(1, s))}`;
</script>

{#if unbekannt}
  <div class="abschnitt">
    <div class="warnkarte neutral" role="status">
      <div class="warn-kopf-blatt">
        <span class="stufe-marke gross unbekannt"><i class="fa-solid fa-question"></i></span>
        <div><b>Warnlage unbekannt</b><small>Die Warnquelle antwortet gerade nicht.</small></div>
      </div>
      <p class="warn-text">Ob amtliche Warnungen gelten, lässt sich gerade nicht sagen. {standText}</p>
    </div>
  </div>
{:else if !liste.length}
  <div class="abschnitt">
    <div class="warnkarte neutral" role="status">
      <div class="warn-kopf-blatt">
        <span class="stufe-marke gross ruhig"><i class="fa-solid fa-check"></i></span>
        <div>
          <b>Keine Warnungen</b>
          <small>{lage === "ausserhalb" ? `Der Wetterdienst warnt nur für Deutschland; für ${daten.ort.name} gibt es keine amtlichen Warnungen.` : `Für ${daten.ort.name} gilt gerade keine amtliche Warnung.`}</small>
        </div>
      </div>
    </div>
    <Stand {bereich} {zone} />
  </div>
{:else}
  <div class="abschnitt">
    <h3>{liste.length === 1 ? "Eine Warnung" : `${liste.length} Warnungen`} · höchste Stufe zuerst</h3>
    {#each liste as w, i (i)}
      <article class="warnkarte {stufeKlasse(w.stufe)}">
        <div class="warn-kopf-blatt">
          <span class="stufe-marke gross">{w.stufe}</span>
          <div><b>{w.ereignis}</b><small>Stufe {w.stufe} · {STUFEN[w.stufe] ?? "Warnung"}</small></div>
        </div>
        <div class="warn-zeit"><i class="fa-solid fa-clock"></i><span>{zeitraum(w.von, w.bis, zone, heute)}</span></div>
        {#if w.ueberschrift && w.ueberschrift !== w.ereignis}<div class="warn-titel">{w.ueberschrift}</div>{/if}
        {#if w.beschreibung}<p class="warn-text">{w.beschreibung}</p>{/if}
      </article>
    {/each}
    <Stand {bereich} {zone} quelle="Amtliche Warnungen" />
  </div>
{/if}

<Begriffe liste={[erklaerung.warnstufen]} />

<style>
  /* Fläche in Warnstufenfarbe kommt aus den gemeinsamen Klassen stufe-1 bis stufe-4 */
  .warnkarte {
    border-radius: var(--radius);
    padding: 12px 14px 14px;
  }
  .warnkarte.neutral {
    background: var(--flaeche-2);
  }
  /* Marke hebt sich von der neutralen Fläche ab */
  .neutral .stufe-marke {
    background: var(--flaeche-3);
  }
  .warnkarte + .warnkarte {
    margin-top: 6px;
  }
  .warn-kopf-blatt {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .warn-kopf-blatt > div {
    flex: 1;
    min-width: 0;
  }
  .warn-kopf-blatt b {
    display: block;
    font-size: var(--s19);
    font-weight: 700;
    line-height: 1.2;
  }
  .warn-kopf-blatt small {
    display: block;
    margin-top: 2px;
    font-size: var(--s15);
    color: var(--text-2);
    line-height: 1.3;
  }
  .warn-zeit {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-top: 12px;
    font-weight: 600;
  }
  .warn-zeit i {
    color: var(--text-3);
    font-size: var(--s15);
  }
  .warn-titel {
    margin-top: 8px;
    font-weight: 700;
    line-height: 1.3;
  }
  /* Beschreibung der Quelle behält ihre Absätze */
  :global(.tel) .warn-text {
    margin: 8px 0 0;
    font-size: var(--s15);
    color: var(--text-2);
    line-height: 1.45;
    white-space: pre-line;
    user-select: text;
  }
</style>
