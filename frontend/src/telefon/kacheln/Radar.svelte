<script module lang="ts">
  // Rahmenliste des Radars: ein Abruf für alle Radarkacheln zugleich, höchstens einmal je Minute.
  import { hole } from "../../kern/api";

  interface Radarbild {
    id: string;
    zeit: string;
    art: "gemessen" | "vorhersage";
  }
  interface Rahmen {
    coords: [number, number][]; // Ecken [lon, lat]: oben links, oben rechts, unten rechts, unten links
    frames: Radarbild[];
  }

  const FRISCH_MS = 60_000;
  let zuletzt: { zeit: number; rahmen: Rahmen } | null = null;
  let laufend: Promise<Rahmen> | null = null;

  function holeRahmen(): Promise<Rahmen> {
    if (zuletzt && Date.now() - zuletzt.zeit < FRISCH_MS) return Promise.resolve(zuletzt.rahmen);
    laufend ??= hole<Rahmen>("/radar/rahmen")
      .then((rahmen) => {
        zuletzt = { zeit: Date.now(), rahmen };
        return rahmen;
      })
      .finally(() => {
        laufend = null;
      });
    return laufend;
  }
</script>

<script lang="ts">
  // Regenradar: Kartenausschnitt um den Ort (dunkle Grundkarte aus Kacheln, Zoom 8) mit dem
  // letzten gemessenen Radarbild, ohne Kartenbibliothek. Web-Mercator rechnet die Kachel selbst;
  // das Radarbild ist in Mercator ausgerichtet und liegt mit seinen Eckpunkten darüber. Der Ort steht
  // in der Mitte. Nachts färbt eine Fläche mit Mischmodus alles rot (kein CSS-filter, der in Chromium
  // leere Kacheln erzeugt). Tippen öffnet den Karten-Reiter (Hülle).
  import type { KachelProps } from "../kachelprops";
  import { form } from "../kachelprops";
  import { uhrzeit } from "../../kern/zeit";
  import { KACHEL_PX, weltPixel } from "./mercator";
  import KKopf from "../KKopf.svelte";

  let { kachel, daten, zone }: KachelProps = $props();

  const ZOOM = 8;
  const TAKT_MS = 5 * 60_000;
  const SYMBOL = "fa-satellite-dish";

  let rahmen = $state.raw<Rahmen | null>(null);
  let fehler = $state(false);
  let fehlbild = $state<string | null>(null); // ID eines Radarbilds, das nicht geladen werden konnte
  let b = $state(0);
  let h = $state(0);

  // Rahmenliste holen und alle 5 Minuten neu; beim Entfernen der Kachel aufräumen.
  $effect(() => {
    let aktiv = true;
    const lade = () =>
      holeRahmen()
        .then((r) => {
          if (!aktiv) return;
          rahmen = r;
          fehler = false;
        })
        .catch(() => {
          if (aktiv) fehler = true;
        });
    void lade();
    const takt = setInterval(lade, TAKT_MS);
    return () => {
      aktiv = false;
      clearInterval(takt);
    };
  });

  const f = $derived(form(kachel));
  const titel = $derived(f === "2x2" ? "Radar" : "Regenradar");
  const ort = $derived(daten.ort);
  const bild = $derived(rahmen?.frames.filter((r) => r.art === "gemessen").at(-1) ?? null);
  const ecken = $derived.by(() => {
    const c = rahmen?.coords;
    return c && c.length === 4 ? { ol: c[0], ur: c[2] } : null;
  });
  // Ort innerhalb des Radarbilds? Außerhalb gäbe die leere Karte fälschlich "kein Regen" vor.
  const abgedeckt = $derived(
    !!ecken && ort.lon >= ecken.ol[0] && ort.lon <= ecken.ur[0] && ort.lat <= ecken.ol[1] && ort.lat >= ecken.ur[1],
  );

  // Weltpixel der linken oberen Ecke des sichtbaren Ausschnitts (Ort in der Mitte)
  const mitte = $derived(weltPixel(ort.lon, ort.lat, ZOOM));
  const ox = $derived(Math.round(mitte.x - b / 2));
  const oy = $derived(Math.round(mitte.y - h / 2));
  const kacheln = $derived.by(() => {
    const liste: { url: string; links: number; oben: number }[] = [];
    if (!b || !h || !abgedeckt) return liste;
    const anzahl = 2 ** ZOOM;
    for (let ty = Math.floor(oy / KACHEL_PX); ty * KACHEL_PX < oy + h; ty++) {
      if (ty < 0 || ty >= anzahl) continue;
      for (let tx = Math.floor(ox / KACHEL_PX); tx * KACHEL_PX < ox + b; tx++) {
        const x = ((tx % anzahl) + anzahl) % anzahl;
        liste.push({ url: `/kachel/dark/${ZOOM}/${x}/${ty}`, links: tx * KACHEL_PX - ox, oben: ty * KACHEL_PX - oy });
      }
    }
    return liste;
  });
  const lage = $derived.by(() => {
    if (!ecken) return null;
    const ol = weltPixel(ecken.ol[0], ecken.ol[1], ZOOM);
    const ur = weltPixel(ecken.ur[0], ecken.ur[1], ZOOM);
    return { links: ol.x - ox, oben: ol.y - oy, breite: ur.x - ol.x, hoehe: ur.y - ol.y };
  });
</script>

<div class="karte-feld" class:mit-karte={abgedeckt && !!bild} bind:clientWidth={b} bind:clientHeight={h} aria-hidden="true">
  {#if abgedeckt && bild}
    {#each kacheln as k (k.url)}
      <img class="kachel" src={k.url} alt="" draggable="false" style="left: {k.links}px; top: {k.oben}px" />
    {/each}
    {#if lage && fehlbild !== bild.id}
      <img
        class="radarbild"
        src="/api/v1/radar/bild/{bild.id}.png"
        alt=""
        draggable="false"
        style="left: {lage.links}px; top: {lage.oben}px; width: {lage.breite}px; height: {lage.hoehe}px"
        onerror={() => (fehlbild = bild.id)}
      />
    {/if}
    <span class="nacht-grau"></span>
    <span class="nacht-rot"></span>
    <span class="ort-punkt" style="left: {mitte.x - ox}px; top: {mitte.y - oy}px"></span>
    <span class="schleier"></span>
  {/if}
</div>

<div class="oben">
  <KKopf titel={titel} symbol={SYMBOL} rechts={abgedeckt && bild ? `${uhrzeit(bild.zeit, zone)} gemessen` : ""} />
</div>
{#if !rahmen && !fehler}
  <span class="sk" style="flex: 1; min-height: 0; margin-top: 8px; border-radius: 10px" aria-busy="true"></span>
{:else if !rahmen}
  <div class="k-mitte hinweis">
    <i class="fa-solid fa-plug-circle-xmark"></i>
    <div class="k-hinweis">Radar gerade nicht erreichbar</div>
  </div>
{:else if !abgedeckt}
  <div class="k-mitte hinweis">
    <i class="fa-solid fa-map-location-dot"></i>
    <div class="k-hinweis">Für diesen Ort gibt es kein Regenradar</div>
  </div>
{:else if !bild}
  <div class="k-mitte hinweis"><div class="k-hinweis">Noch kein gemessenes Radarbild</div></div>
{:else}
  {#if fehlbild === bild.id}<div class="k-mitte hinweis"><div class="k-hinweis">Radarbild fehlt</div></div>{/if}
  <div class="quelle">Radar: Deutscher Wetterdienst, Karte: OpenStreetMap</div>
{/if}

<style>
  /* Kartenausschnitt über die ganze Kachel, unter Kopf und Quelle; isoliert, damit die
     Mischmodi des Nachtbetriebs nur die Karte treffen */
  .karte-feld {
    position: absolute;
    inset: 0;
    overflow: hidden;
    isolation: isolate;
    pointer-events: none;
  }
  /* Grund unter noch fehlenden Kacheln; ohne Karte bleibt die Kachelfläche (Laden, Hinweise) */
  .mit-karte {
    background: var(--flaeche-2);
  }
  .kachel {
    position: absolute;
    width: 256px;
    height: 256px;
    max-width: none;
  }
  .radarbild {
    position: absolute;
    max-width: none;
    opacity: 0.85;
  }
  .ort-punkt {
    position: absolute;
    width: 14px;
    height: 14px;
    margin: -7px 0 0 -7px;
    border-radius: 50%;
    background: var(--text);
    box-shadow: 0 0 0 3px var(--grund);
  }
  /* Kopf und Quelle bleiben auf dunklem Grund lesbar */
  .schleier {
    position: absolute;
    inset: 0;
    background:
      linear-gradient(var(--flaeche), transparent 50px),
      linear-gradient(0deg, var(--flaeche), transparent 54px);
  }
  /* Nachtbetrieb: erst grau (Sättigung des schwarzen Grunds), dann mit der Textfarbe multipliziert,
     so wird alles einfarbig rot */
  .nacht-grau,
  .nacht-rot {
    position: absolute;
    inset: 0;
    display: none;
  }
  :global(.tel[data-modus="nacht"]) .nacht-grau {
    display: block;
    background: var(--grund);
    mix-blend-mode: saturation;
  }
  :global(.tel[data-modus="nacht"]) .nacht-rot {
    display: block;
    background: var(--text);
    mix-blend-mode: multiply;
  }
  .oben {
    position: relative;
  }
  .hinweis {
    position: relative;
    align-items: flex-start;
    gap: 6px;
  }
  .hinweis i {
    color: var(--text-3);
    font-size: var(--s19);
  }
  /* Pflichtangabe der Lizenzen, klein am unteren Rand */
  .quelle {
    position: absolute;
    left: var(--innen);
    right: var(--innen);
    bottom: 8px;
    font-size: var(--s13);
    line-height: 1.2;
    color: var(--text-2);
  }
</style>
