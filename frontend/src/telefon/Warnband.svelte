<script lang="ts">
  // Warnband über dem Raster, wenn im Layout keine Warnkachel steht: oberste Warnung mit Zeit,
  // bei Ausfall der Quelle "Warnlage unbekannt" (nie stillschweigend nichts). Ohne amtliche Warnung steht hier,
  // was als Nächstes kommt (Regen, Gewitter, Sturm aus der Lage), Tippen öffnet "Was kommt".
  import { vorZeit } from "../kern/zeit";
  import { warnZeitraum } from "./kacheln/warnzeit";
  import { uhr } from "../kern/uhr.svelte";
  import { oeffne } from "./ansicht.svelte";
  import type { Kompakt } from "./typen";
  import { meldekatalog } from "../kern/gemeinsam";

  let { daten }: { daten: Kompakt } = $props();

  const status = $derived(daten.bereiche.warnungen.status);
  const liste = $derived(daten.warnungen ?? []);
  const oberste = $derived(liste[0]);
  const zone = $derived(daten.ort.zeitzone);
  const zeit = $derived(oberste ? warnZeitraum(oberste.von, oberste.bis, uhr.jetzt, zone) : "");
  const naechstes = $derived((daten.lage ?? []).find((e) => !e.laeuft && e.art !== "warnung"));
  const symbol = $derived(
    naechstes?.quelle === "blitze" ? "fa-bolt" : (meldekatalog.arten.find((a) => a.schluessel === naechstes?.art)?.symbol ?? "fa-circle-info"),
  );
</script>

{#if status === "fehlt"}
  <div class="warnband unbekannt" role="status">
    <span class="stufe-marke"><i class="fa-solid fa-question"></i></span>
    <div class="wb-txt">
      <div class="wb-titel">Warnlage unbekannt</div>
      <div class="wb-zeit">Quelle antwortet nicht{daten.bereiche.warnungen.stand ? `, zuletzt ${vorZeit(daten.bereiche.warnungen.stand, uhr.jetzt)}` : ""}</div>
    </div>
  </div>
{:else if oberste}
  <button class="warnband stufe-{oberste.stufe}" onclick={() => oeffne({ art: "warnungen" })}>
    <span class="stufe-marke">{oberste.stufe}</span>
    <div class="wb-txt">
      <div class="wb-titel">{oberste.ereignis}</div>
      <div class="wb-zeit">{zeit}</div>
    </div>
    {#if liste.length > 1}<span class="wb-mehr">+{liste.length - 1} weitere</span>{/if}
  </button>
{:else if naechstes}
  <button class="warnband lage stufe-{Math.min(4, Math.max(1, naechstes.stufe))}" onclick={() => oeffne({ art: "lage" })}>
    <span class="stufe-marke"><i class="fa-solid {symbol}"></i></span>
    <div class="wb-txt">
      <div class="wb-titel">{naechstes.titel}</div>
      <div class="wb-zeit">Was kommt</div>
    </div>
  </button>
{/if}

<style>
  /* Was kommt: ruhiger als eine amtliche Warnung, erst ab Stufe 3 in Warnfarbe */
  .warnband.lage.stufe-1,
  .warnband.lage.stufe-2 {
    background: var(--flaeche);
  }
  .warnband.lage.stufe-1 :global(.stufe-marke),
  .warnband.lage.stufe-2 :global(.stufe-marke) {
    background: var(--flaeche-3);
    color: var(--text);
  }
  button.warnband {
    width: calc(100% - 2 * var(--rand));
    text-align: left;
  }
</style>
