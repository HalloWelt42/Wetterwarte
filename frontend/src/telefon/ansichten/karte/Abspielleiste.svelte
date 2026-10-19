<script lang="ts">
  // Abspielleiste des Regenradars (Entwurf mockups/telefon/radar.html): Abspielen, Uhrzeit groß,
  // Zeitleiste von einer Stunde zurück bis zur Vorhersage +2 h mit Marke jetzt, schmale Legende in mm/h.
  // Ziehen auf der Zeitleiste wählt den Zeitpunkt; Pfeiltasten gehen bildweise.
  import { uhrzeit } from "../../../kern/zeit";
  import type { Abspieler } from "./abspieler.svelte";

  let { abspieler, zone }: { abspieler: Abspieler; zone: string } = $props();

  // Regenstufen wie die Karte am Rechner (Farben in --rr1 bis --rr8, nachts nur Rot)
  const STUFEN = ["0,1", "0,5", "1", "2", "5", "10", "20", "40"];
  const MARKEN = [
    { offset: -60, text: "-1 h" },
    { offset: 0, text: "jetzt" },
    { offset: 60, text: "+1 h" },
    { offset: 120, text: "+2 h" },
  ];

  let bahn: HTMLDivElement;
  let zieht = false;

  const rahmen = $derived(abspieler.rahmen);
  const aktuell = $derived(abspieler.aktuell);
  const von = $derived(rahmen[0]?.offset ?? 0);
  const bis = $derived(rahmen.at(-1)?.offset ?? 0);
  const lage = (offset: number): number => (bis > von ? Math.min(100, Math.max(0, ((offset - von) / (bis - von)) * 100)) : 0);
  // Marken nur innerhalb der vorhandenen Bilder (5 Minuten Spielraum für die Bildschritte)
  const marken = $derived(MARKEN.filter((m) => m.offset >= von - 5 && m.offset <= bis + 5).map((m) => ({ ...m, lage: lage(m.offset) })));

  const minuten = (n: number): string => (n === 1 ? "1 Minute" : `${n} Minuten`);
  const unter = $derived(
    !aktuell ? "" : aktuell.offset === 0 ? "gemessen, jetzt" : aktuell.offset < 0 ? `gemessen, vor ${minuten(-aktuell.offset)}` : `Vorhersage, in ${minuten(aktuell.offset)}`,
  );
  const zeitText = $derived(aktuell ? uhrzeit(aktuell.zeit, zone) : "");

  /** Bild, das der Stelle x auf der Zeitleiste am nächsten liegt. */
  function waehleBei(x: number): void {
    const r = bahn.getBoundingClientRect();
    const ziel = von + Math.min(1, Math.max(0, (x - r.left) / r.width)) * (bis - von);
    let best = 0;
    rahmen.forEach((f, i) => {
      if (Math.abs(f.offset - ziel) < Math.abs(rahmen[best].offset - ziel)) best = i;
    });
    abspieler.waehle(best);
  }

  function unten(e: PointerEvent): void {
    zieht = true;
    bahn.setPointerCapture(e.pointerId);
    waehleBei(e.clientX);
  }
  function taste(e: KeyboardEvent): void {
    const ziel = { ArrowLeft: abspieler.index - 1, ArrowRight: abspieler.index + 1, Home: 0, End: rahmen.length - 1 }[e.key];
    if (ziel === undefined) return;
    e.preventDefault();
    abspieler.waehle(Math.min(rahmen.length - 1, Math.max(0, ziel)));
  }
</script>

<div class="abspiel">
  <div class="abspiel-zeile">
    <button class="abspielen" aria-label={abspieler.spielt ? "Anhalten" : "Abspielen"} onclick={() => abspieler.umschalten()} disabled={rahmen.length < 2}>
      <i class="fa-solid {abspieler.spielt ? 'fa-pause' : 'fa-play'}"></i>
    </button>
    <div class="abspiel-zeit"><b class="zahl">{zeitText}</b><small>{unter}</small></div>
  </div>
  <div
    class="zeitleiste"
    bind:this={bahn}
    role="slider"
    tabindex="0"
    aria-label="Zeitpunkt des Radarbilds"
    aria-valuemin={0}
    aria-valuemax={Math.max(0, rahmen.length - 1)}
    aria-valuenow={abspieler.index}
    aria-valuetext="{zeitText} {unter}"
    onpointerdown={unten}
    onpointermove={(e) => zieht && waehleBei(e.clientX)}
    onpointerup={() => (zieht = false)}
    onpointercancel={() => (zieht = false)}
    onkeydown={taste}
  >
    <div class="zl-bahn"><span class="zl-gemessen" style="width: {lage(0)}%"></span><span class="zl-vorhersage"></span></div>
    {#each marken as m (m.offset)}<span class="zl-marke" class:jetzt={m.offset === 0} style="left: {m.lage}%"></span>{/each}
    {#if aktuell}<span class="zl-griff" style="left: {lage(aktuell.offset)}%"></span>{/if}
  </div>
  <div class="zl-achse">
    {#each marken as m (m.offset)}
      <span class:jetzt={m.offset === 0} class:links={m.lage < 6} class:rechts={m.lage > 94} style="left: {m.lage}%">{m.text}</span>
    {/each}
  </div>
  <div class="legende">
    <span class="legende-titel">mm/h</span>
    <div class="legende-skala">
      <div class="legende-balken">{#each STUFEN as _, i (i)}<span style="background: var(--rr{i + 1})"></span>{/each}</div>
      <div class="legende-werte">{#each STUFEN as s (s)}<span>{s}</span>{/each}</div>
    </div>
  </div>
</div>

<style>
  .abspiel {
    /* Regenstufen wie die Karte am Rechner: 0,1 0,5 1 2 5 10 20 40 mm/h */
    --rr1: #4d8df2;
    --rr2: #2980e6;
    --rr3: #26c7b8;
    --rr4: #40cc59;
    --rr5: #f2e64d;
    --rr6: #fa9e33;
    --rr7: #eb4d33;
    --rr8: #bf33bf;
    padding: 8px 14px 12px 10px;
    border-radius: var(--radius);
    background: color-mix(in srgb, var(--flaeche) 90%, transparent);
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    box-shadow: 0 6px 22px rgba(0, 0, 0, 0.5);
    pointer-events: auto;
  }
  /* Nachtbetrieb: Stufen nur in Rot, unterschieden über die Helligkeit */
  :global(.tel[data-modus="nacht"]) .abspiel {
    --rr1: #3a0d0b;
    --rr2: #521310;
    --rr3: #6a1913;
    --rr4: #832017;
    --rr5: #9c271c;
    --rr6: #b52f22;
    --rr7: #cb3828;
    --rr8: #e0412f;
  }
  .abspiel-zeile {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .abspielen {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    flex: none;
    background: var(--akzent);
    color: var(--grund);
    font-size: var(--s17);
  }
  .abspielen:disabled {
    background: var(--flaeche-3);
    color: var(--text-3);
  }
  .abspiel-zeit {
    display: flex;
    flex-direction: column;
    min-width: 0;
    line-height: 1.05;
  }
  .abspiel-zeit b {
    font-size: var(--s26);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }
  .abspiel-zeit small {
    font-size: var(--s13);
    font-weight: 700;
    color: var(--text-3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .zeitleiste {
    position: relative;
    height: 44px;
    margin: 0 4px 0 6px;
    cursor: pointer;
    touch-action: none;
    outline: none;
  }
  .zeitleiste:focus-visible .zl-griff {
    box-shadow: 0 0 0 4px var(--flaeche), 0 0 0 6px var(--akzent);
  }
  .zl-bahn {
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    height: 6px;
    margin-top: -3px;
    display: flex;
  }
  .zl-gemessen {
    flex: none;
    border-radius: 3px 0 0 3px;
    background: var(--text-2);
  }
  .zl-vorhersage {
    flex: 1;
    border-radius: 0 3px 3px 0;
    background: repeating-linear-gradient(90deg, var(--text-3) 0 7px, transparent 7px 12px);
  }
  .zl-marke {
    position: absolute;
    top: 50%;
    width: 2px;
    height: 14px;
    margin: -7px 0 0 -1px;
    border-radius: 1px;
    background: var(--text-3);
  }
  .zl-marke.jetzt {
    height: 20px;
    margin-top: -10px;
    background: var(--text);
  }
  .zl-griff {
    position: absolute;
    top: 50%;
    width: 24px;
    height: 24px;
    margin: -12px 0 0 -12px;
    border-radius: 50%;
    background: var(--text);
    box-shadow: 0 0 0 4px var(--flaeche);
    pointer-events: none;
  }
  .zl-achse {
    position: relative;
    height: calc(var(--s13) + 4px);
    margin: -6px 4px 0 6px;
    font-size: var(--s13);
    font-weight: 700;
    color: var(--text-3);
  }
  .zl-achse span {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    white-space: nowrap;
  }
  .zl-achse span.links {
    transform: none;
  }
  .zl-achse span.rechts {
    transform: translateX(-100%);
  }
  .zl-achse .jetzt {
    color: var(--text);
  }
  .legende {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 12px 4px 0 6px;
  }
  .legende-titel {
    flex: none;
    font-size: var(--s13);
    font-weight: 700;
    line-height: 1;
    color: var(--text-3);
  }
  .legende-skala {
    flex: 1;
    min-width: 0;
  }
  .legende-balken {
    display: flex;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
  }
  .legende-balken span {
    flex: 1;
  }
  .legende-werte {
    display: flex;
    margin-top: 3px;
    font-size: var(--s13);
    font-weight: 700;
    color: var(--text-3);
    font-variant-numeric: tabular-nums;
  }
  .legende-werte span {
    flex: 1;
    min-width: 0;
  }
</style>
