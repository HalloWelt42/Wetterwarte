<script lang="ts">
  // Blatt Monatsvergleich: Abweichung des laufenden Monats (Ortszeit) vom Klimamittel groß, die
  // Abweichung je Monat seit Januar, Niederschlag zum Mittel und jeder Monat einzeln.
  // Abweichung = gemessenes Monatsmittel minus Normalwert; ohne Messwerte keine Zahl.
  import type { KachelProps } from "../kachelprops";
  import { uhr } from "../../kern/uhr.svelte";
  import { teile } from "../../kern/zeit";
  import { zahl } from "../format";
  import Abweichung from "../mikro/Abweichung.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import { MONATE } from "./datum";
  import { klimamittel } from "./erklaerungen";
  import { holeMonatsdaten, type Messmonat, type Monatsdaten } from "../monatdaten";

  let { daten, zone }: KachelProps = $props();

  const heute = $derived(teile(uhr.jetzt, zone));
  const jahr = $derived(heute.jahr);
  const monat = $derived(heute.monat);
  const ort = $derived(daten.ort.slug);
  const schluessel = $derived(`${ort}:${jahr}`);

  let geladen = $state.raw<{ schluessel: string; daten: Monatsdaten } | null>(null);
  let fehlt = $state.raw<string | null>(null);

  $effect(() => {
    const k = schluessel;
    let aktiv = true;
    holeMonatsdaten(ort, jahr)
      .then((d) => {
        if (aktiv) {
          geladen = { schluessel: k, daten: d };
          fehlt = null;
        }
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
  const monate = $derived(Array.from({ length: monat }, (_, i) => i + 1));
  const normal = (m: number) => d?.klima.monate.find((k) => k.monat === m) ?? null;
  const gemessen = (reihe: Messmonat[], m: number) => reihe.find((r) => r.monat === m) ?? null;

  const zeilen = $derived(
    d
      ? monate.map((m) => {
          const g = gemessen(d.temperatur, m);
          const n = normal(m)?.temp ?? null;
          const mittel = g?.mittel ?? null;
          return { m, mittel, normal: n, anzahl: g?.anzahl ?? 0, abw: mittel !== null && n !== null ? mittel - n : null };
        })
      : [],
  );
  const temp = $derived(zeilen.map((z) => z.abw));
  const aktuell = $derived(zeilen[monat - 1] ?? null);
  const mitWert = $derived(temp.filter((v): v is number => v !== null));
  const waermer = $derived(mitWert.filter((v) => Math.round(v * 10) > 0).length);

  // Niederschlag: laufender Monat gegen das Mittel bis heute (nach Tagen), frühere Monate ganz
  const tageImMonat = $derived(new Date(Date.UTC(jahr, monat, 0)).getUTCDate());
  const regenMonat = $derived(d?.niederschlag ? (gemessen(d.niederschlag, monat)?.summe ?? null) : null);
  const ueblich = (m: number) => {
    const n = normal(m)?.niederschlag ?? null;
    return n === null ? null : m === monat ? (n * heute.tag) / tageImMonat : n;
  };
  const regenUeblichBisher = $derived(ueblich(monat));
  const regenJahr = $derived.by(() => {
    if (!d?.niederschlag) return null;
    const summen = monate.map((m) => gemessen(d.niederschlag!, m)?.summe ?? null).filter((v): v is number => v !== null);
    return summen.length ? summen.reduce((a, b) => a + b, 0) : null;
  });
  const regenUeblichJahr = $derived.by(() => {
    const werte = monate.map(ueblich);
    return werte.every((v) => v !== null) ? (werte as number[]).reduce((a, b) => a + b, 0) : null;
  });

  const zehntel = (v: number) => Math.round(v * 10) / 10;
  const gradText = (v: number) => `${zehntel(v) > 0 ? "+" : zehntel(v) < 0 ? "-" : ""}${zahl(Math.abs(zehntel(v)), 1)}°`;
  const wort = (v: number) => (zehntel(v) > 0 ? "wärmer als üblich" : zehntel(v) < 0 ? "kühler als üblich" : "wie üblich");
  const farbe = (v: number) => (zehntel(v) > 0 ? "t-heiss" : zehntel(v) < 0 ? "t-frost" : "");
</script>

{#if zustand === "laedt"}
  <div class="abschnitt" aria-busy="true">
    <div class="sk-stapel">
      <span class="sk" style="width: 140px; height: 54px"></span>
      <span class="sk" style="width: 220px; height: 18px"></span>
      <span class="sk" style="width: 100%; height: 150px"></span>
    </div>
  </div>
{:else if zustand === "fehlt" || !d}
  <div class="abschnitt">
    <Hinweis titel="Klimadaten gerade nicht erreichbar" text="Der Vergleich mit dem Klimamittel lässt sich gerade nicht laden. Es werden keine Ersatzwerte gezeigt." />
  </div>
{:else}
  <div class="abschnitt">
    <div class="held">
      <div class="held-text">
        {#if aktuell?.abw != null}
          <div class="riesen-zahl {farbe(aktuell.abw)}">{gradText(aktuell.abw)}</div>
          <div class="held-satz">{MONATE[monat - 1]} bisher {wort(aktuell.abw)}</div>
          <div class="held-unter">
            Mittel bis heute <b>{zahl(aktuell.mittel ?? 0, 1)}°</b>, üblich <b>{zahl(aktuell.normal ?? 0, 1)}°</b>
            {#if aktuell.anzahl}(aus {aktuell.anzahl} {aktuell.anzahl === 1 ? "Messwert" : "Messwerten"}){/if}
          </div>
        {:else}
          <div class="riesen-zahl mittel">keine Angabe</div>
          <div class="held-satz">{MONATE[monat - 1]} bisher</div>
          <div class="held-unter">
            {aktuell?.mittel === null ? "In diesem Monat gibt es noch keine Messwerte." : "Für diesen Monat fehlt das Klimamittel."}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <div class="abschnitt">
    <h3>Temperatur je Monat · {jahr}</h3>
    <div class="tafel">
      <div class="tafel-kopf"><b>Abweichung vom Mittel</b><span>zu {d.klima.von} bis {d.klima.bis}</span></div>
      {#if mitWert.length}
        <div class="diagramm"><Abweichung werte={temp} hervor={monat - 1} /></div>
        <div class="monate" style="grid-template-columns: repeat({monat}, minmax(0, 1fr))">
          {#each monate as m (m)}<span class:an={m === monat}>{MONATE[m - 1][0]}</span>{/each}
        </div>
        <div class="tafel-fuss">
          Säulen nach oben: wärmer, nach unten: kühler als im Mittel. {waermer} von {mitWert.length}
          {mitWert.length === 1 ? "Monat mit Messwerten war" : "Monaten mit Messwerten waren"} wärmer.
        </div>
      {:else}
        <Hinweis symbol="fa-chart-column" titel="Noch keine Messwerte in diesem Jahr" />
      {/if}
    </div>
  </div>

  <div class="abschnitt">
    <h3>Niederschlag</h3>
    <div class="zeilen">
      <div class="zeile">
        <span class="sym"><i class="fa-solid fa-umbrella"></i></span>
        <div class="haupt">
          <b>{MONATE[monat - 1]} bisher</b>
          <small>{regenUeblichBisher !== null ? `üblich bis heute ${zahl(regenUeblichBisher)} mm` : "kein Mittel bekannt"}</small>
        </div>
        <span class="rechts">
          {#if regenMonat !== null}<span class="zahl-r">{zahl(regenMonat)} <small>mm</small></span>{:else}<span class="zahl-r matt">keine Messwerte</span>{/if}
        </span>
      </div>
      <div class="zeile">
        <span class="sym"><i class="fa-solid fa-calendar"></i></span>
        <div class="haupt">
          <b>Jahr bisher</b>
          <small>{regenUeblichJahr !== null ? `üblich bis heute ${zahl(regenUeblichJahr)} mm` : "kein Mittel bekannt"}</small>
        </div>
        <span class="rechts">
          {#if regenJahr !== null}<span class="zahl-r">{zahl(regenJahr)} <small>mm</small></span>{:else}<span class="zahl-r matt">keine Messwerte</span>{/if}
        </span>
      </div>
    </div>
    {#if !d.niederschlag}<p>Für diesen Ort wird kein Niederschlag aufgezeichnet; gezeigt ist nur das Mittel.</p>{/if}
  </div>

  <div class="abschnitt">
    <h3>Monate einzeln</h3>
    <div class="zeilen">
      {#each zeilen as z (z.m)}
        <div class="zeile" class:an={z.m === monat}>
          <div class="haupt">
            <b>{MONATE[z.m - 1]}</b>
            <small>
              {#if z.mittel !== null}Mittel {zahl(z.mittel, 1)}°{#if z.normal !== null}, üblich {zahl(z.normal, 1)}°{:else}, kein Klimamittel{/if}{#if z.m === monat}, bis zum {heute.tag}.{/if}
              {:else}keine Messwerte, kein Vergleich{/if}
            </small>
          </div>
          {#if z.abw !== null}<span class="rechts"><span class="zahl-r {farbe(z.abw)}">{gradText(z.abw)}</span></span>{/if}
        </div>
      {/each}
    </div>
  </div>

  <Begriffe liste={[klimamittel(d.klima.von, d.klima.bis)]} />
{/if}
