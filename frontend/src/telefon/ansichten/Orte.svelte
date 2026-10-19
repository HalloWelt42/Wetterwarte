<script lang="ts">
  // Inhalt des Blatts "Orte" (Entwurf mockups/telefon/orte.html): oben die Suche, darunter die eigenen
  // Orte mit Symbol, Ortszeit, Temperatur sowie Hoch und Tief, Warnpunkt bei aktiver Warnung. Antippen
  // wählt den Ort und schließt das Blatt. Hinzufügen geht hier, Reihenfolge und Löschen am Rechner.
  import { onMount, untrack } from "svelte";
  import { fuegeOrtHinzu, orteState, sucheOrte, type Ort, type Treffer } from "../../kern/orte.svelte";
  import { neuLadenAufhalten } from "../../kern/fassung.svelte";
  import { uhr } from "../../kern/uhr.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import { ansicht, schliesse, waehleOrt } from "../ansicht.svelte";
  import { ladeOrteTelefon } from "../orte.svelte";
  import { ladeWennAlt, standVon } from "../wetter.svelte";
  import { grad } from "../format";
  import { heute } from "../rechnen";
  import { tempKlasse } from "../mikro/geometrie";
  import Symbol from "../Symbol.svelte";

  const SUCHE_WARTEN_MS = 250;

  let suche = $state("");
  let treffer = $state<Treffer[]>([]);
  let sucht = $state(false);
  let fuegtHinzu = $state<Treffer | null>(null);
  let fehler = $state("");
  let eingabe: HTMLInputElement;
  let lauf = 0; // nur die Antwort der letzten Eingabe zählt

  const begriff = $derived(suche.trim());

  // Wetter je Ort holen, sobald das Blatt offen ist (und für neu hinzugekommene Orte)
  $effect(() => {
    const slugs = orteState.liste.map((o) => o.slug);
    untrack(() => slugs.forEach(ladeWennAlt));
  });

  // Eine neue Fassung wartet, solange gesucht wird
  onMount(() => neuLadenAufhalten(() => !!suche.trim()));

  // Suche beim Tippen, kurz verzögert
  $effect(() => {
    const q = begriff;
    const nr = ++lauf;
    fehler = "";
    if (q.length < 2) {
      treffer = [];
      sucht = false;
      return;
    }
    sucht = true;
    const warten = setTimeout(async () => {
      const liste = await sucheOrte(q);
      if (nr !== lauf) return;
      treffer = liste;
      sucht = false;
    }, SUCHE_WARTEN_MS);
    return () => clearTimeout(warten);
  });

  function abbrechen(): void {
    suche = "";
    eingabe.blur();
  }

  function waehle(slug: string): void {
    waehleOrt(slug);
    schliesse();
  }

  /** Schon in der Liste: gleicher Name an (fast) gleicher Stelle. */
  function vorhanden(t: Treffer): Ort | undefined {
    return orteState.liste.find((o) => o.name === t.name && Math.abs(o.lat - t.lat) < 0.01 && Math.abs(o.lon - t.lon) < 0.01);
  }

  async function hinzufuegen(t: Treffer): Promise<void> {
    fuegtHinzu = t;
    fehler = "";
    const neu = await fuegeOrtHinzu(t);
    fuegtHinzu = null;
    if (!neu) {
      fehler = `${t.name} ließ sich gerade nicht hinzufügen.`;
      return;
    }
    void ladeOrteTelefon(); // Liste auch im Gerätespeicher nachführen
    suche = "";
    waehle(neu.slug);
  }

  /** Getippten Teil im Namen hervorheben. */
  function teile(name: string): [string, string, string] {
    const i = name.toLocaleLowerCase("de").indexOf(begriff.toLocaleLowerCase("de"));
    return i < 0 ? [name, "", ""] : [name.slice(0, i), name.slice(i, i + begriff.length), name.slice(i + begriff.length)];
  }

  const hoechsteStufe = (stufen: number[]): number => Math.max(...stufen);
</script>

<div class="such-zeile">
  <label class="suchfeld" class:aktiv={!!suche}>
    <i class="fa-solid fa-magnifying-glass"></i>
    <input bind:this={eingabe} bind:value={suche} type="text" enterkeyhint="search" autocomplete="off" placeholder="Ort suchen" aria-label="Ort suchen" />
    {#if suche}
      <button class="leeren" aria-label="Eingabe leeren" onclick={() => ((suche = ""), eingabe.focus())}><i class="fa-solid fa-circle-xmark"></i></button>
    {/if}
  </label>
  {#if suche}<button class="text-knopf" onclick={abbrechen}>Abbrechen</button>{/if}
</div>

{#if suche}
  <div class="abschnitt">
    {#if begriff.length < 2}
      <p class="hinweis-z"><i class="fa-solid fa-keyboard"></i><span>Mindestens zwei Buchstaben eingeben.</span></p>
    {:else if sucht && !treffer.length}
      <p class="hinweis-z"><i class="fa-solid fa-magnifying-glass"></i><span>Sucht ...</span></p>
    {:else if !treffer.length}
      <p class="hinweis-z"><i class="fa-solid fa-circle-info"></i><span>Kein Ort gefunden.</span></p>
    {:else}
      <h3>{treffer.length} Treffer</h3>
      <div class="zeilen">
        {#each treffer as t (`${t.name}|${t.lat}|${t.lon}`)}
          {@const [vor, hervor, nach] = teile(t.name)}
          {@const da = vorhanden(t)}
          <div class="zeile treffer">
            <span class="sym"><i class="fa-solid fa-location-dot"></i></span>
            <div class="haupt">
              <b>{vor}<em>{hervor}</em>{nach}</b>
              <small>{[t.region, t.land].filter(Boolean).join(" · ")}</small>
            </div>
            {#if da}
              <button class="knopf-text treffer-knopf" onclick={() => waehle(da.slug)}><i class="fa-solid fa-check"></i>Zeigen</button>
            {:else}
              <button class="knopf-text treffer-knopf" onclick={() => hinzufuegen(t)} disabled={!!fuegtHinzu}>
                <i class="fa-solid {fuegtHinzu === t ? 'fa-spinner fa-spin' : 'fa-plus'}"></i>Hinzufügen
              </button>
            {/if}
          </div>
        {/each}
      </div>
      {#if fehler}<p class="hinweis-z fehler"><i class="fa-solid fa-plug-circle-xmark"></i><span>{fehler}</span></p>{/if}
      <p class="hinweis-z"><i class="fa-solid fa-circle-info"></i><span>Hinzufügen nimmt den Ort in die Liste auf und zeigt sein Wetter.</span></p>
    {/if}
  </div>
{:else}
  <div class="abschnitt">
    {#if orteState.liste.length}
      <div class="zeilen">
        {#each orteState.liste as o (o.slug)}
          {@const stand = standVon(o.slug)}
          {@const d = stand.daten}
          {@const warnungen = d?.warnungen ?? []}
          {@const warnStatus = d?.bereiche.warnungen.status}
          {@const tag = d ? heute(d) : null}
          {@const zone = o.zeitzone || d?.ort.zeitzone || ""}
          <button class="zeile ort-z" class:an={o.slug === ansicht.ort} aria-current={o.slug === ansicht.ort ? "true" : undefined} onclick={() => waehle(o.slug)}>
            {#if d?.jetzt}
              <Symbol code={d.jetzt.code} tag={d.jetzt.tag} />
            {:else}
              <span class="symbol-leer" class:sk={stand.zustand === "laedt"}></span>
            {/if}
            <div class="haupt">
              <b>
                <span>{o.name}</span>
                {#if warnStatus === "fehlt"}
                  <span class="warn-punkt unbekannt" aria-label="Warnlage unbekannt">?</span>
                {:else if warnungen.length}
                  {@const stufe = hoechsteStufe(warnungen.map((w) => w.stufe))}
                  <span class="warn-punkt w{stufe}" aria-label="Warnstufe {stufe}">{stufe}</span>
                {/if}
              </b>
              <small>
                {#if warnStatus === "fehlt"}<span class="warn-text unbekannt">Warnlage unbekannt</span>
                {:else if warnungen.length}<span class="warn-text">{warnungen[0].ereignis}</span>
                {:else}{o.region || o.land}{/if}
                · {uhrzeit(uhr.jetzt, zone)}
              </small>
            </div>
            <div class="ort-temp">
              {#if d?.jetzt}
                <b class={tempKlasse(d.jetzt.temp)}>{grad(d.jetzt.temp)}</b>
                {#if tag}
                  <small><i class="fa-solid fa-arrow-up" aria-label="Hoch"></i> <b>{grad(tag.hoch)}</b> <i class="fa-solid fa-arrow-down" aria-label="Tief"></i> <b>{grad(tag.tief)}</b></small>
                {/if}
              {:else if stand.zustand === "laedt"}
                <span class="sk temp-leer"></span>
              {:else}
                <small>keine Angabe</small>
              {/if}
            </div>
          </button>
        {/each}
      </div>
    {:else}
      <p class="hinweis-z"><i class="fa-solid fa-location-dot"></i><span>Noch kein Ort in der Liste. Oben nach einem Ort suchen.</span></p>
    {/if}
    <p class="hinweis-z"><i class="fa-solid fa-desktop"></i><span>Reihenfolge und Löschen am Rechner.</span></p>
  </div>
{/if}

<style>
  .such-zeile {
    position: sticky;
    top: 0;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 4px;
    padding-bottom: 6px;
    background: var(--flaeche);
  }
  .such-zeile .suchfeld {
    flex: 1;
    min-width: 0;
  }
  :global(.tel) .suchfeld.aktiv {
    background: var(--flaeche-3);
    color: var(--text-2);
  }
  .leeren {
    width: 44px;
    height: 44px;
    margin-right: -12px;
    display: grid;
    place-items: center;
    flex: none;
    color: var(--text-3);
  }
  .text-knopf {
    min-height: 44px;
    padding: 0 10px;
    color: var(--akzent);
    font-weight: 600;
    flex: none;
  }
  :global(.tel) .abschnitt {
    margin-top: 6px;
  }
  .hinweis-z {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 14px 8px 0;
    font-size: var(--s15);
    color: var(--text-3);
    line-height: 1.35;
  }
  .hinweis-z i {
    margin-top: 3px;
  }
  .hinweis-z.fehler {
    color: var(--text-2);
  }

  /* Ortszeilen */
  :global(.tel) .ort-z {
    width: 100%;
    min-height: 72px;
    padding: 8px 14px 8px 10px;
    text-align: left;
  }
  :global(.tel) .ort-z :global(.mc),
  :global(.tel) .symbol-leer {
    width: 44px;
    height: 44px;
    flex: none;
  }
  :global(.tel) .symbol-leer {
    border-radius: 50%;
    background: var(--flaeche-3);
  }
  :global(.tel) .ort-z .haupt b {
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: normal;
    line-height: 1.2;
  }
  .ort-z .haupt b > span:first-child {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  :global(.tel) .ort-z .haupt small {
    white-space: normal;
    line-height: 1.2;
  }
  .warn-text {
    color: var(--w1);
    font-weight: 600;
  }
  .warn-text.unbekannt {
    color: var(--text-2);
  }
  .warn-punkt {
    flex: none;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: var(--s13);
    font-weight: 700;
    color: var(--grund);
    line-height: 1;
  }
  .warn-punkt.w1 {
    background: var(--w1);
  }
  .warn-punkt.w2 {
    background: var(--w2);
  }
  .warn-punkt.w3 {
    background: var(--w3);
  }
  .warn-punkt.w4 {
    background: var(--w4);
  }
  .warn-punkt.unbekannt {
    background: var(--flaeche-3);
    color: var(--text-2);
  }
  .ort-temp {
    margin-left: auto;
    flex: none;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    line-height: 1.05;
    font-variant-numeric: tabular-nums;
  }
  .ort-temp > b {
    font-size: var(--s26);
    font-weight: 700;
  }
  .ort-temp small {
    margin-top: 4px;
    font-size: var(--s15);
    color: var(--text-3);
    white-space: nowrap;
  }
  .ort-temp small b {
    font-size: var(--s15);
    color: var(--text-2);
  }
  .ort-temp small i {
    font-size: var(--s13);
  }
  .temp-leer {
    width: 44px;
    height: 26px;
  }

  /* Treffer der Suche */
  .treffer b {
    font-weight: 500;
    color: var(--text-2);
  }
  .treffer b em {
    font-style: normal;
    font-weight: 700;
    color: var(--text);
  }
  :global(.tel) .treffer .haupt small {
    white-space: normal;
    line-height: 1.2;
  }
  :global(.tel) .treffer-knopf {
    min-height: 44px;
    padding: 0 14px;
    flex: none;
    background: var(--flaeche-3);
    color: var(--akzent);
    font-size: var(--s15);
  }
  .treffer-knopf:disabled {
    color: var(--text-3);
  }
</style>
