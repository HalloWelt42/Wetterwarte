<script lang="ts">
  import { warnlage } from "../rechnen";
  // Warnungen (höchste Stufe zuerst): 1x1 nur Stufe und Anzahl, 2x1 Stufe und Ereignis, 3x1 oberste
  // Warnung mit Zeitraum, 3x2 bis drei Warnungen. Bis 3x1 trägt die Fläche die Farbe der höchsten
  // Stufe, in 3x2 jede Zeile ihre eigene. Ohne Warnung ruhig "Keine Warnungen"; fällt die Quelle
  // aus, zeigt das die Hülle ("Warnlage unbekannt"). Tippen öffnet alle Warnungen (Hülle).
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import { warnZeitraum } from "./warnzeit";
  import KKopf from "../KKopf.svelte";

  let { kachel, daten, zone }: KachelProps = $props();

  const SYMBOL = "fa-triangle-exclamation";
  const ZEILEN = 3;

  const f = $derived(form(kachel));
  const liste = $derived(daten.warnungen ?? []);
  const oberste = $derived(liste[0] ?? null);
  const gezeigt = $derived(liste.slice(0, ZEILEN));
  const anzahl = $derived(liste.length === 1 ? "1 Warnung" : `${liste.length} Warnungen`);
  const stand = $derived(daten.bereiche.warnungen.stand);
  const zeitraum = (von: string | null, bis: string | null) => warnZeitraum(von, bis, uhr.jetzt, zone);
  const weitere = (n: number) => (n > 0 ? `+${n} weitere` : "");
  const ausserhalb = $derived(warnlage(daten) === "ausserhalb");
</script>

{#if !oberste}
  {#if f === "1x1"}
    <div class="warn-kopf"><span class="stufe-marke ruhig"><i class="fa-solid fa-shield-halved"></i></span></div>
    <div class="k-fuss"><div class="titel-2">Keine Warnungen</div></div>
  {:else}
    <KKopf titel="Warnungen" symbol={SYMBOL} rechts={f !== "2x1" && stand ? `Stand ${uhrzeit(stand, zone)}` : ""} />
    <div class="k-reihe mitte">
      <span class="stufe-marke gross ruhig"><i class="fa-solid fa-shield-halved"></i></span>
      <div class="k-block dehnen">
        <div class={f === "2x1" ? "titel-2" : "titel-1"}>Keine Warnungen</div>
        {#if f !== "2x1"}<div class="unter">{ausserhalb ? "amtlich nur für Deutschland" : `für ${daten.ort.name}`}</div>{/if}
      </div>
    </div>
  {/if}
{:else if f === "3x2"}
  <KKopf titel="Warnungen" symbol={SYMBOL} rechts={liste.length > ZEILEN ? weitere(liste.length - ZEILEN) : `${liste.length} für ${daten.ort.name}`} />
  <div class="warn-liste">
    {#each gezeigt as w, i (i)}
      <div class="warn-zeile stufe-{w.stufe}">
        <span class="stufe-marke">{w.stufe}</span>
        <div class="wz-txt">
          <div class="wz-titel">{w.ereignis}</div>
          <div class="wz-zeit">{zeitraum(w.von, w.bis)}</div>
          {#if gezeigt.length < ZEILEN && w.beschreibung}<div class="wz-zeit entbehrlich">{w.beschreibung}</div>{/if}
        </div>
      </div>
    {/each}
  </div>
{:else}
  <!-- Fläche in der Farbe der höchsten Stufe; die Stufenmarke darin färbt telefon.css (.stufe-N .stufe-marke) -->
  <div class="getoent stufe-{oberste.stufe}">
    {#if f === "1x1"}
      <!-- ohne Kopf: das Wort steht in der Anzahl, der Titel passte bei großer Schrift nicht -->
      <div class="warn-kopf"><i class="fa-solid {SYMBOL} c-w{oberste.stufe} warnzeichen"></i></div>
      <div class="k-fuss">
        <div class="wert dick c-w{oberste.stufe}"><small>Stufe</small><b>{oberste.stufe}</b></div>
        <div class="unter"><span class="ersatz-fuer">{anzahl}</span><span class="ersatz">{liste.length} aktiv</span></div>
      </div>
    {:else}
      <KKopf titel="Warnungen" symbol={SYMBOL} rechts={weitere(liste.length - 1)} />
      <div class="k-reihe mitte">
        <span class="stufe-marke gross">{oberste.stufe}</span>
        <div class="k-block dehnen">
          {#if f === "2x1"}
            <div class="titel-2">{oberste.ereignis}</div>
          {:else}
            <div class="titel-1">{oberste.ereignis}</div>
            <div class="unter">{zeitraum(oberste.von, oberste.bis)}</div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
{/if}

<style>
  /* Die ganze Kachelfläche getönt: deckt die Kachel samt Innenabstand und ordnet den Inhalt wie .k */
  .getoent {
    position: absolute;
    inset: 0;
    padding: var(--innen);
    display: flex;
    flex-direction: column;
  }
  .warnzeichen {
    font-size: var(--s19);
  }
  /* "Stufe" vor der Zahl */
  .getoent .wert small {
    margin-right: 4px;
  }
</style>
