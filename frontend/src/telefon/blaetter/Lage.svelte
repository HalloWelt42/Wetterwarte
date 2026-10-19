<script lang="ts">
  // Blatt "Was kommt" (docs/WARNUNGEN.md): die Lage am Ort, wie das Backend sie erkennt (lage.py), kommende
  // Ereignisse mit Beginn und Quelle, laufende darunter. Hierher führt das Antippen einer Mitteilung. Unten, was
  // dieses Gerät zuletzt gemeldet bekam, und der Weg zu den Einstellungen.
  import { meldekatalog } from "../../kern/gemeinsam";
  import { uhr } from "../../kern/uhr.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import { oeffne } from "../ansicht.svelte";
  import { konto } from "../meldungen/konto.svelte";
  import type { Ereignis, Kompakt } from "../typen";
  import { kalendertag, tagNah } from "./datum";

  let { daten, zone }: { daten: Kompakt; zone: string } = $props();

  const QUELLE: Record<Ereignis["quelle"], string> = {
    radar: "Regenradar",
    vorhersage: "Vorhersage",
    amtlich: "Deutscher Wetterdienst",
    blitze: "Blitzmessung",
  };

  const lage = $derived(daten.lage ?? []);
  const kommend = $derived(lage.filter((e) => !e.laeuft));
  const laufend = $derived(lage.filter((e) => e.laeuft));
  const heute = $derived(kalendertag(uhr.jetzt, zone));
  const radarFehlt = $derived(daten.bereiche.nowcast?.status === "fehlt");
  const basisFehlt = $derived(daten.bereiche.basis.status === "fehlt");
  const gemeldet = $derived((konto.daten?.protokoll ?? []).filter((p) => p.ort === daten.ort.slug).slice(0, 6));

  function symbol(e: Ereignis): string {
    if (e.quelle === "blitze") return "fa-bolt";
    return meldekatalog.arten.find((a) => a.schluessel === e.art)?.symbol ?? "fa-circle-info";
  }

  function wann(iso: string): string {
    const tag = tagNah(kalendertag(iso, zone), heute);
    return `${tag === "heute" ? "" : `${tag} `}${uhrzeit(iso, zone)} Uhr`;
  }

  function zeile(e: Ereignis): string {
    const teile = [];
    if (e.beginn && !e.laeuft) teile.push(`ab ${wann(e.beginn)}`);
    teile.push(QUELLE[e.quelle]);
    return teile.join(" · ");
  }
</script>

<div class="abschnitt">
  <h3>{kommend.length ? "Kommt in den nächsten Stunden" : "Nichts in Sicht"}</h3>
  {#if kommend.length}
    {#each kommend as e (e.schluessel)}
      <article class="lage-karte stufe-{Math.min(4, Math.max(1, e.stufe))}">
        <span class="stufe-marke"><i class="fa-solid {symbol(e)}"></i></span>
        <div class="lk-txt">
          <b>{e.titel}</b>
          <span>{e.text}</span>
          <small>{zeile(e)}</small>
        </div>
      </article>
    {/each}
  {:else}
    <div class="lage-karte ruhig">
      <span class="stufe-marke ruhig"><i class="fa-solid fa-check"></i></span>
      <div class="lk-txt">
        <b>Ruhig</b>
        <span>Für {daten.ort.name} steht in den nächsten Stunden kein Regen, kein Gewitter und kein Sturm an.</span>
      </div>
    </div>
  {/if}
  {#if basisFehlt}
    <p class="hinweis-z warn"><i class="fa-solid fa-plug-circle-xmark"></i><span>Die Vorhersage antwortet gerade nicht; Regen, Gewitter und Sturm lassen sich nicht sagen.</span></p>
  {:else if radarFehlt}
    <p class="hinweis-z"><i class="fa-solid fa-satellite-dish"></i><span>Das Regenradar antwortet gerade nicht; Regen kommt aus der Vorhersage.</span></p>
  {/if}
</div>

{#if laufend.length}
  <div class="abschnitt">
    <h3>Gerade</h3>
    {#each laufend as e (e.schluessel)}
      <article class="lage-karte flach">
        <span class="stufe-marke"><i class="fa-solid {symbol(e)}"></i></span>
        <div class="lk-txt"><b>{e.titel}</b><small>{QUELLE[e.quelle]}</small></div>
      </article>
    {/each}
  </div>
{/if}

{#if gemeldet.length}
  <div class="abschnitt">
    <h3>Zuletzt gemeldet</h3>
    <div class="zeilen">
      {#each gemeldet as p (p.zeit + p.kanal)}
        <div class="zeile">
          <span class="sym"><i class="fa-solid {p.kanal === 'push' ? 'fa-bell' : 'fa-volume-high'}"></i></span>
          <span class="haupt"><b>{p.titel}</b><small>{wann(p.zeit)}{p.zugestellt ? "" : " · nicht zugestellt"}</small></span>
        </div>
      {/each}
    </div>
  </div>
{/if}

<div class="abschnitt einstellungen">
  <div class="zeilen">
    <button class="zeile" onclick={() => oeffne({ art: "meldungen" })}>
      <span class="sym"><i class="fa-solid fa-bell"></i></span>
      <span class="haupt"><b>Meldungen einstellen</b><small>Mitteilungen aufs Telefon und Tonansagen</small></span>
      <span class="rechts"><i class="fa-solid fa-chevron-right"></i></span>
    </button>
  </div>
</div>

<style>
  .lage-karte {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 14px;
    border-radius: var(--radius);
  }
  .lage-karte + .lage-karte {
    margin-top: 6px;
  }
  .lage-karte.ruhig,
  .lage-karte.flach {
    background: var(--flaeche-2);
  }
  .flach .stufe-marke {
    background: var(--flaeche-3);
    color: var(--text-2);
  }
  .lk-txt {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 3px;
    line-height: 1.3;
  }
  .lk-txt b {
    font-size: var(--s17);
    font-weight: 700;
  }
  .lk-txt span {
    font-size: var(--s15);
    color: var(--text-2);
  }
  .lk-txt small {
    font-size: var(--s13);
    color: var(--text-3);
  }
</style>
