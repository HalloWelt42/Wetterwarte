
<script lang="ts">
  import { holeMonatsdaten, STUNDE_MS, type Messmonat, type Monatsdaten } from "../monatdaten";
  // Monatsvergleich: laufender Monat (Ortszeit) gegen das Klimamittel. 2x1 Abweichung der
  // Temperatur, 3x1 zusätzlich die Abweichung je Monat seit Januar, 3x2 zusätzlich der Niederschlag;
  // wird kein Niederschlag aufgezeichnet, zeigt 3x2 die Temperatur groß. Abweichung = gemessenes
  // Monatsmittel minus Normalwert.
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { teile } from "../../kern/zeit";
  import { zahl } from "../format";
  import KKopf from "../KKopf.svelte";
  import Abweichung from "../mikro/Abweichung.svelte";

  let { kachel, daten, zone }: KachelProps = $props();

  const MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
  const SYMBOL = "fa-chart-column";

  const f = $derived(form(kachel));
  const heute = $derived(teile(uhr.jetzt, zone));
  const jahr = $derived(heute.jahr);
  const monat = $derived(heute.monat);
  const ort = $derived(daten.ort.slug);
  const schluessel = $derived(`${ort}:${jahr}`);
  const stunde = $derived(Math.floor(uhr.jetzt.getTime() / STUNDE_MS));

  let geladen = $state.raw<{ schluessel: string; daten: Monatsdaten } | null>(null);
  let fehlt = $state.raw<string | null>(null);

  // Je Ort und Jahr laden, stündlich neu (aus dem Zwischenspeicher, solange er frisch ist).
  $effect(() => {
    const k = schluessel;
    const o = ort;
    const j = jahr;
    void stunde;
    let aktiv = true;
    holeMonatsdaten(o, j)
      .then((d) => {
        if (!aktiv) return;
        geladen = { schluessel: k, daten: d };
        fehlt = null;
      })
      .catch(() => {
        if (aktiv) fehlt = k;
      });
    return () => {
      aktiv = false;
    };
  });

  const zustand = $derived(geladen?.schluessel === schluessel ? "ok" : fehlt === schluessel ? "fehlt" : "laedt");
  const d = $derived(zustand === "ok" && geladen ? geladen.daten : null);

  const normal = (m: number) => d?.klima.monate.find((k) => k.monat === m) ?? null;
  const gemessen = (reihe: Messmonat[], m: number) => reihe.find((r) => r.monat === m) ?? null;
  const monate = $derived(Array.from({ length: monat }, (_, i) => i + 1));

  // Temperatur: Abweichung je Monat von Januar bis zum laufenden (null: keine Messwerte)
  const temp = $derived(
    d
      ? monate.map((m) => {
          const mittel = gemessen(d.temperatur, m)?.mittel ?? null;
          const n = normal(m)?.temp ?? null;
          return mittel !== null && n !== null ? mittel - n : null;
        })
      : [],
  );
  const bisher = $derived(d ? (gemessen(d.temperatur, monat)?.mittel ?? null) : null);
  const mittel = $derived(normal(monat)?.temp ?? null);
  const abw = $derived(temp[monat - 1] ?? null);
  const frueher = $derived(temp.some((v) => v !== null));

  // Niederschlag in Prozent zum Mittel; der laufende Monat gegen das Mittel bis heute (nach Tagen)
  const tageImMonat = $derived(new Date(Date.UTC(jahr, monat, 0)).getUTCDate());
  const regen = $derived.by(() => {
    const reihe = d?.niederschlag;
    if (!reihe) return null;
    return monate.map((m) => {
      const summe = gemessen(reihe, m)?.summe ?? null;
      const n = normal(m)?.niederschlag ?? null;
      const anteil = m === monat ? heute.tag / tageImMonat : 1;
      return summe !== null && n ? (summe / (n * anteil) - 1) * 100 : null;
    });
  });
  const regenAbw = $derived(regen?.[monat - 1] ?? null);

  const titel = $derived(`${MONATE[monat - 1]} bisher`);
  const zeitraum = $derived(f !== "2x1" && d ? `zu ${d.klima.von} bis ${d.klima.bis}` : "");
  const achse = $derived(monat === 1 ? [MONATE[0]] : [MONATE[0], MONATE[monat - 1]]);

  const zehntel = (v: number) => Math.round(v * 10) / 10;
  const vorzeichen = (v: number) => (v > 0 ? "+" : v < 0 ? "-" : "");
  const gradText = (v: number) => `${vorzeichen(zehntel(v))}${zahl(Math.abs(zehntel(v)), 1)}°`;
  const prozentText = (v: number) => `${vorzeichen(Math.round(v))}${zahl(Math.abs(Math.round(v)))} %`;
  const wort = (v: number) => (zehntel(v) > 0 ? "wärmer als üblich" : zehntel(v) < 0 ? "kühler als üblich" : "wie üblich");
  const tempFarbe = (v: number) => (zehntel(v) > 0 ? "t-heiss" : zehntel(v) < 0 ? "t-frost" : "");
  const regenFarbe = (v: number) => (Math.round(v) > 0 ? "c-regen" : Math.round(v) < 0 ? "c-sonne" : "");
</script>

<KKopf {titel} symbol={SYMBOL} rechts={zeitraum} />
{#if zustand === "laedt"}
  <div class="k-reihe" aria-busy="true">
    <div class="sk-stapel">
      <span class="sk" style="width: 74px; height: 30px"></span>
      <span class="sk" style="width: 110px; height: 14px"></span>
    </div>
    {#if f !== "2x1"}<span class="sk diagramm-sk"></span>{/if}
  </div>
{:else if zustand === "fehlt"}
  <div class="k-mitte hinweis">
    <i class="fa-solid fa-plug-circle-xmark"></i>
    <div class="k-hinweis">Klimadaten gerade nicht erreichbar</div>
  </div>
{:else if abw === null}
  <!-- Noch kein Vergleich möglich; frühere Monate bleiben sichtbar -->
  <div class="k-reihe mitte">
    <div class="k-block hinweis-block">
      <div class="k-hinweis">{bisher === null ? "Noch keine Messwerte in diesem Monat" : "Kein Klimamittel für diesen Monat"}</div>
    </div>
    {#if f !== "2x1" && frueher}<Abweichung werte={temp} hervor={monat - 1} {achse} />{/if}
  </div>
{:else if f === "2x1"}
  <div class="k-reihe">
    <div class="k-block">
      <div class="wert halb {tempFarbe(abw)}"><b>{gradText(abw)}</b></div>
      <div class="unter">{wort(abw)}</div>
    </div>
    {#if bisher !== null && mittel !== null}
      <div class="k-block ans-ende zeilen-klein entbehrlich-gross">
        <div>bisher <b>{zahl(bisher, 1)}°</b></div>
        <div>Mittel <b>{zahl(mittel, 1)}°</b></div>
      </div>
    {/if}
  </div>
{:else if f === "3x1"}
  <div class="k-reihe breit">
    <div class="k-block">
      <div class="wert halb {tempFarbe(abw)}"><b>{gradText(abw)}</b></div>
      <div class="unter">{wort(abw)}</div>
    </div>
    <Abweichung werte={temp} hervor={monat - 1} {achse} />
  </div>
{:else if regen}
  <div class="k-reihe breit zweizeilig">
    <div class="k-block drittel">
      <div class="wert halb {tempFarbe(abw)}"><b>{gradText(abw)}</b></div>
      <div class="unter">Temperatur</div>
    </div>
    <Abweichung werte={temp} hervor={monat - 1} />
  </div>
  <div class="k-reihe breit zweizeilig regen-farben">
    <div class="k-block drittel">
      {#if regenAbw !== null}
        <div class="wert halb {regenFarbe(regenAbw)}"><b>{prozentText(regenAbw)}</b></div>
      {:else}
        <div class="k-hinweis">keine Angabe</div>
      {/if}
      <div class="unter">Niederschlag</div>
    </div>
    <Abweichung werte={regen} hervor={monat - 1} {achse} />
  </div>
{:else}
  <div class="k-reihe fest gross-oben">
    <div class="k-block">
      <div class="wert voll {tempFarbe(abw)}"><b>{gradText(abw)}</b></div>
      <div class="unter">{wort(abw)}</div>
    </div>
    {#if bisher !== null && mittel !== null}
      <div class="k-block ans-ende zeilen-klein">
        <div>bisher <b>{zahl(bisher, 1)}°</b></div>
        <div>Mittel <b>{zahl(mittel, 1)}°</b></div>
      </div>
    {/if}
  </div>
  <div class="diagramm-gross"><Abweichung werte={temp} hervor={monat - 1} {achse} /></div>
{/if}

<style>
  .k-reihe.breit {
    gap: 12px;
  }
  .zweizeilig {
    margin-top: 6px;
  }
  .zweizeilig + .zweizeilig {
    margin-top: 10px;
  }
  .k-block.drittel {
    width: 32%;
  }
  /* Niederschlag: mehr als üblich in Regenfarbe nach oben, weniger in Sonnenfarbe nach unten */
  .regen-farben {
    --t-heiss: var(--regen);
    --t-frost: var(--sonne);
  }
  .gross-oben {
    margin-top: 6px;
  }
  .diagramm-gross {
    flex: 1;
    min-height: 0;
    display: flex;
    margin-top: 10px;
  }
  .sk.diagramm-sk {
    flex: 1;
    align-self: stretch;
    border-radius: 8px;
  }
  .k-block.hinweis-block {
    flex: 0 1 auto;
    max-width: 45%;
  }
  .k-reihe > .k-block.hinweis-block:only-child {
    max-width: none;
  }
  .hinweis {
    align-items: flex-start;
    gap: 6px;
  }
  .hinweis i {
    color: var(--text-3);
    font-size: var(--s19);
  }
</style>
