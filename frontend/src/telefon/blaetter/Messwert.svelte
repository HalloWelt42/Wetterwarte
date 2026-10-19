<script lang="ts">
  // Blatt Messwert: der in der Kachel gewählte Wert (Einstellung "groesse") groß, darunter sein
  // Verlauf über 24 oder 48 Stunden aus den Stunden (6 zurück, der Rest voraus, wie die Kachel).
  // Titel, Einheit, Farbe und Verlauf kommen aus kacheln/messwerte.ts, damit Kachel und Blatt gleich zählen.
  import type { KachelProps } from "../kachelprops";
  import { einstellung } from "../../kern/gemeinsam";
  import { stunde, uhrzeit } from "../../kern/zeit";
  import { zahl } from "../format";
  import Linie from "../mikro/Linie.svelte";
  import Saeulen from "../mikro/Saeulen.svelte";
  import { druckTendenz, messwertVon, verlauf } from "../kacheln/messwerte";
  import Achse from "./bausteine/Achse.svelte";
  import Begriffe from "./bausteine/Begriffe.svelte";
  import Hinweis from "./bausteine/Hinweis.svelte";
  import Segmente from "./bausteine/Segmente.svelte";
  import Stand from "./bausteine/Stand.svelte";
  import { kalendertag, tagNah } from "./datum";
  import { erklaerung, type Begriff } from "./erklaerungen";

  let { kachel, daten, zone }: KachelProps = $props();

  const ZURUECK = 6;
  const BEGRIFFE: Record<string, Begriff[]> = {
    gefuehlt: [erklaerung.gefuehlt],
    feuchte: [erklaerung.feuchte, erklaerung.taupunkt],
    taupunkt: [erklaerung.taupunkt, erklaerung.feuchte],
    druck: [erklaerung.luftdruck],
    sicht: [erklaerung.sicht],
    bewoelkung: [erklaerung.bewoelkung],
    regen_heute: [erklaerung.regenMenge],
    boeen: [erklaerung.boeen, erklaerung.beaufort],
  };

  const m = $derived(messwertVon(einstellung("messwert", kachel.conf, "groesse")));
  const wert = $derived(m.jetzt(daten));
  const zusatz = $derived(wert === null ? null : m.zusatz(daten, wert, false));
  const tendenz = $derived(m.art === "druck" ? druckTendenz(daten.jetzt?.druck_tendenz ?? null) : null);

  let spanne = $state<"24" | "48">("24");
  const reihe = $derived(verlauf(daten, m, ZURUECK, (spanne === "24" ? 24 : 48) - ZURUECK));
  const von = $derived(reihe ? daten.jetzt_index - reihe.jetzt : 0);
  const stunden = $derived(reihe ? daten.stunden.slice(von, von + reihe.werte.length) : []);
  const lo = $derived(reihe ? Math.min(...reihe.werte) : 0);
  const hi = $derived(reihe ? Math.max(...reihe.werte) : 0);
  const summe = $derived(reihe ? reihe.werte.slice(reihe.jetzt).reduce((a, b) => a + b, 0) : 0);
  const heute = $derived(kalendertag(daten.zeit, zone));

  function wann(i: number): string {
    const s = stunden[i];
    if (!s) return "";
    const tag = tagNah(kalendertag(s.zeit, zone), heute);
    return `${tag === "heute" ? "" : `${tag} `}um ${uhrzeit(s.zeit, zone)} Uhr`;
  }
  const iHi = $derived(reihe ? reihe.werte.indexOf(hi) : -1);
  const iLo = $derived(reihe ? reihe.werte.indexOf(lo) : -1);
  // Einheit hinter großen Zahlen; die Kachel nennt hPa in ihrer Zeile darunter, das Blatt am Wert
  const ZUSATZ_EINHEIT: Record<string, string> = { druck: "hPa" };
  const einheit = $derived(m.einheit || (ZUSATZ_EINHEIT[m.art] ?? ""));

  // Achse alle 6 (24 h) bzw. 12 Stunden (48 h) ab jetzt; Linie von Rand zu Rand, Säulen mittig je Stunde
  const marken = $derived.by(() => {
    if (!reihe) return [];
    const schritt = spanne === "24" ? 6 : 12;
    return stunden
      .map((s, i) => ({ s, i }))
      .filter(({ i }) => (i - reihe.jetzt) % schritt === 0)
      .map(({ s, i }) => ({
        anteil: m.saeulen ? (i + 0.5) / stunden.length : i / Math.max(1, stunden.length - 1),
        text: i === reihe.jetzt ? "Jetzt" : String(stunde(s.zeit, zone)).padStart(2, "0"),
        an: i === reihe.jetzt,
      }));
  });
</script>

<div class="abschnitt">
  <div class="held">
    <div class="held-text">
      {#if wert !== null}
        <div class="riesen-zahl {m.klasse(wert)}">
          {m.text(wert)}{#if einheit}<small>{einheit}</small>{/if}
        </div>
      {:else}
        <div class="riesen-zahl mittel">keine Angabe</div>
      {/if}
      <div class="held-satz"><i class="fa-solid {m.symbol}"></i> {m.titel}</div>
      {#if tendenz && daten.jetzt?.druck_tendenz != null}
        <div class="held-unter">
          <i class="fa-solid {tendenz.pfeil}"></i> {tendenz.wort}, <b>{daten.jetzt.druck_tendenz > 0 ? "+" : ""}{zahl(daten.jetzt.druck_tendenz, 1)} hPa</b> in 3 Stunden
        </div>
      {:else if zusatz?.text}
        <div class="held-unter">{zusatz.text}{#if zusatz.fett}{" "}<b>{zusatz.fett}</b>{/if}</div>
      {/if}
    </div>
  </div>
</div>

<div class="abschnitt">
  <h3>Verlauf</h3>
  <Segmente optionen={[{ wert: "24", titel: "24 h" }, { wert: "48", titel: "48 h" }]} bind:wert={spanne} />
  <div class="tafel">
    {#if reihe}
      <div class="tafel-kopf">
        <b>{m.titel}</b>
        <span>{#if m.saeulen}ab jetzt zusammen {m.text(summe)} {einheit}{:else}{m.text(lo)} bis {m.text(hi)} {einheit}{/if}</span>
      </div>
      <div class="diagramm mittel">
        {#if m.saeulen}
          <Saeulen werte={reihe.werte} farbe={m.farbe} max={Math.max(1, hi)} hervor={reihe.jetzt} />
        {:else}
          <Linie werte={reihe.werte} farbe={m.farbe} flaeche={m.flaeche} jetzt={reihe.jetzt} minmax einheit={m.einheitVerlauf} />
        {/if}
      </div>
      <Achse {marken} />
      <div class="tafel-fuss">
        {#if m.saeulen}
          {#if hi > 0}Am meisten {wann(iHi)} mit <b>{m.text(hi)}&nbsp;{einheit}</b>. Säulen: je Stunde.{:else}In diesem Zeitraum fällt kein Regen.{/if}
        {:else}
          Höchstwert <b>{m.text(hi)}&nbsp;{einheit}</b> {wann(iHi)}, Tiefstwert <b>{m.text(lo)}&nbsp;{einheit}</b> {wann(iLo)}.
        {/if}
        Gezeigt: {ZURUECK} Stunden zurück und Vorhersage, der Punkt steht auf jetzt.
      </div>
    {:else}
      <Hinweis symbol="fa-chart-line" titel="Kein Verlauf" text="Für diesen Wert fehlen Stundenwerte; es wird nichts ergänzt." />
    {/if}
  </div>
  <Stand bereich={daten.bereiche.basis} {zone} />
</div>

<Begriffe liste={BEGRIFFE[m.art] ?? []} />

<style>
  .held-satz i {
    color: var(--text-3);
    margin-right: 2px;
  }
</style>
