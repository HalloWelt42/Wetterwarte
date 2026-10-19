<script lang="ts">
  // Karten-Reiter (Entwurf mockups/telefon/radar.html): Karte über die ganze Fläche bis zur Reiterleiste,
  // zentriert auf den gewählten Ort. Oben Ort und Zeit des gezeigten Radarbilds, rechts je Ebene ein
  // eigener Schalter, unten die Abspielleiste des Regenradars. MapLibre wird erst hier nachgeladen, damit
  // die Übersicht ohne Kartenbibliothek startet. In der Karte wird verschoben, deshalb wechselt Wischen
  // hier nicht die Seite (nur die Reiterleiste). Beim Verlassen baut sich alles ab: Takte, Abrufe, Karte.
  import { onMount, tick, untrack } from "svelte";
  import type { Map as KartenBibliothek, Marker } from "maplibre-gl";
  import { karteAnlegen, OHNE_WEBGL } from "../../kern/webgl";
  import { orteState } from "../../kern/orte.svelte";
  import { neuLadenAufhalten } from "../../kern/fassung.svelte";
  import { uhr } from "../../kern/uhr.svelte";
  import { uhrzeit } from "../../kern/zeit";
  import { ansicht, nachtAktiv, nachtUmschalten, oeffne } from "../ansicht.svelte";
  import { Abspieler, type Rahmen } from "./karte/abspieler.svelte";
  import { EBENEN_VON, faerbe, grundKacheln, legeEbenenAn, leseFarben, radarBild, setzeDaten, setzeDetail, setzeGrund, zeige, type Ecken } from "./karte/ebenen";
  import { SCHALTER, kartenWahl, schalte } from "./karte/wahl.svelte";
  import Abspielleiste from "./karte/Abspielleiste.svelte";

  const ZOOM = 8; // Umgebung des Orts, rund 150 km breit
  const MITTE_DEUTSCHLAND: [number, number] = [10.45, 51.16];
  const BLITZE_GRENZE = 20000; // höchstens so viele Blitze der letzten Stunde je Abruf
  const BLITZ_ABSTAND_MS = 5000; // gedrosselt: Verschieben lädt höchstens alle 5 Sekunden
  const BLITZ_TAKT_MS = 60_000;
  const WARN_TAKT_MS = 3 * 60_000;
  const RADAR_TAKT_MS = 3 * 60_000;
  const WIND_TAKT_MS = 10 * 60_000;

  let wurzel: HTMLDivElement;
  let flaeche: HTMLDivElement;
  let map: KartenBibliothek | undefined;
  let ohneKarte = $state(false); // kein WebGL: Hinweis statt Karte (kern/webgl.ts)
  let marker: Marker | undefined;
  let grundDunkel: boolean | undefined; // welche Kacheln die Grundkarte gerade lädt (dunkel oder hell)
  let bereit = $state(false); // Stil geladen, Quellen und Ebenen angelegt
  const abbruch = new AbortController(); // bricht beim Abbau alle laufenden Abrufe ab

  const ort = $derived(orteState.liste.find((o) => o.slug === ansicht.ort));
  const lon = $derived(ort?.lon);
  const lat = $derived(ort?.lat);
  const zone = $derived(ort?.zeitzone ?? "");
  const nacht = $derived(nachtAktiv());

  // --- Regenradar
  let ecken = $state.raw<Ecken | null>(null);
  let radarFehlt = $state(false);
  const abspieler = new Abspieler((url) => {
    if (map && ecken) radarBild(map, url, ecken, kartenWahl.radar);
  });
  const jetztBild = $derived(abspieler.rahmen[abspieler.jetztIndex]);
  const radarAmOrt = $derived(!ecken || lon === undefined || lat === undefined || (lon >= ecken[0][0] && lon <= ecken[1][0] && lat >= ecken[2][1] && lat <= ecken[0][1]));
  const radarAlter = $derived(jetztBild ? uhr.jetzt.getTime() - new Date(jetztBild.zeit).getTime() : 0);
  const frische = $derived(radarAlter > 60 * 60_000 ? "weg" : radarAlter > 25 * 60_000 ? "alt" : "");
  const standText = $derived.by(() => {
    const b = abspieler.aktuell;
    if (!radarAmOrt) return "kein Regenradar am Ort";
    if (b) return `${uhrzeit(b.zeit, zone)} ${b.art === "gemessen" ? "gemessen" : "Vorhersage"}`;
    return radarFehlt ? "Regenradar nicht erreichbar" : "Regenradar lädt";
  });

  /** Abruf mit Abbruch beim Abbau; null bei Fehler oder wenn die Karte inzwischen abgebaut ist. */
  async function holeJson<T>(url: string): Promise<T | null> {
    try {
      const antwort = await fetch(url, { signal: abbruch.signal });
      if (!antwort.ok) return null;
      const daten = (await antwort.json()) as T;
      return map ? daten : null;
    } catch {
      return null;
    }
  }

  async function baue(abgebaut: () => boolean): Promise<void> {
    const [{ default: bibliothek }] = await Promise.all([import("maplibre-gl"), import("maplibre-gl/dist/maplibre-gl.css")]);
    if (abgebaut()) return;
    const dunkel = kartenWahl.dunkel;
    grundDunkel = dunkel;
    const m = karteAnlegen(() => new bibliothek.Map({
      container: flaeche,
      style: {
        version: 8,
        sources: { grund: { type: "raster", tiles: grundKacheln(dunkel), tileSize: 256 } },
        layers: [{ id: "grund", type: "raster", source: "grund" }],
      },
      center: lon !== undefined && lat !== undefined ? [lon, lat] : MITTE_DEUTSCHLAND,
      zoom: ort ? ZOOM : 5,
      minZoom: 3,
      maxZoom: 13,
      attributionControl: false,
      dragRotate: false,
      pitchWithRotate: false,
      touchPitch: false,
    }));
    if (!m) {
      ohneKarte = true;
      return;
    }
    m.touchZoomRotate.disableRotation();
    map = m;
    const punkt = document.createElement("div");
    punkt.className = "karte-ort-punkt";
    marker = new bibliothek.Marker({ element: punkt });
    if (lon !== undefined && lat !== undefined) marker.setLngLat([lon, lat]).addTo(m);
    // Quellen erst anlegen, wenn der Stil geladen ist ("style.load", sonst "Style is not done loading").
    // Nicht auf "load" warten: das kommt erst, wenn alle Kacheln der Grundkarte geladen oder gescheitert
    // sind, und hielte bei langsamen Kacheln Radar, Warnungen und Blitze zurück.
    m.once("style.load", () => {
      if (map !== m) return;
      legeEbenenAn(m, kartenWahl, leseFarben(wurzel));
      bereit = true;
    });
    m.on("moveend", () => {
      if (kartenWahl.blitze) blitzeGedrosselt();
    });
  }

  onMount(() => {
    let abgebaut = false;
    void baue(() => abgebaut);
    const abmelden = neuLadenAufhalten(() => abspieler.spielt); // keine neue Fassung mitten in der Wiedergabe
    return () => {
      abgebaut = true;
      abmelden();
      abbruch.abort();
      abspieler.stoppe();
      clearTimeout(blitzNachzug);
      marker?.remove();
      map?.remove();
      map = undefined; // laufende Abrufe brechen danach mit "if (!map) return" ab
      marker = undefined;
    };
  });

  // Ortswechsel: Punkt versetzen und hinfliegen
  $effect(() => {
    const l = lon;
    const b = lat;
    if (l === undefined || b === undefined) return;
    untrack(() => {
      if (!map || !marker) return;
      marker.setLngLat([l, b]).addTo(map);
      map.flyTo({ center: [l, b], zoom: ZOOM, duration: 800 });
    });
  });

  function zumOrt(): void {
    if (map && lon !== undefined && lat !== undefined) map.flyTo({ center: [lon, lat], zoom: ZOOM, duration: 700 });
  }

  // Farben aus den Variablen der Ansicht (Wechsel zwischen Tag und Nachtbetrieb)
  $effect(() => {
    void nacht;
    if (!bereit) return;
    void tick().then(() => map && faerbe(map, leseFarben(wurzel)));
  });

  // Grundkarte hell oder dunkel; die Detailkarte passt sich ihr an
  $effect(() => {
    const dunkel = kartenWahl.dunkel;
    const detail = kartenWahl.detail;
    if (!bereit || !map) return;
    if (dunkel !== grundDunkel) {
      setzeGrund(map, dunkel);
      grundDunkel = dunkel;
    }
    setzeDetail(map, detail, dunkel);
  });

  // Warnpolygone, alle 3 Minuten aufgefrischt
  async function ladeWarnungen(): Promise<void> {
    const d = await holeJson<{ data: GeoJSON.FeatureCollection }>("/api/v1/wetter/warnkarte");
    if (d?.data && map) setzeDaten(map, "warnungen", d.data);
  }
  $effect(() => {
    const an = kartenWahl.warnungen;
    if (!bereit || !map) return;
    zeige(map, EBENEN_VON.warnungen, an);
    if (!an) return;
    void ladeWarnungen();
    const takt = setInterval(() => void ladeWarnungen(), WARN_TAKT_MS);
    return () => clearInterval(takt);
  });

  // Windpfeile (nur Pfeile), alle 10 Minuten aufgefrischt
  async function ladeWind(): Promise<void> {
    const d = await holeJson<{ data: { wind: GeoJSON.FeatureCollection } }>("/api/v1/wetter/kartendaten");
    if (d?.data?.wind && map) setzeDaten(map, "wind", d.data.wind);
  }
  $effect(() => {
    const an = kartenWahl.wind;
    if (!bereit || !map) return;
    zeige(map, EBENEN_VON.wind, an);
    if (!an) return;
    void ladeWind();
    const takt = setInterval(() => void ladeWind(), WIND_TAKT_MS);
    return () => clearInterval(takt);
  });

  // Blitze der letzten Stunde im Ausschnitt der Karte, gedrosselt
  let blitzZuletzt = 0;
  let blitzLaeuft = false;
  let blitzNachzug: ReturnType<typeof setTimeout> | undefined;

  function blitzeGedrosselt(): void {
    if (blitzNachzug) return; // ein Abruf ist schon vorgemerkt
    const warten = blitzLaeuft ? BLITZ_ABSTAND_MS : BLITZ_ABSTAND_MS - (Date.now() - blitzZuletzt);
    if (warten > 0) {
      blitzNachzug = setTimeout(() => {
        blitzNachzug = undefined;
        blitzeGedrosselt();
      }, warten);
      return;
    }
    void ladeBlitze();
  }

  async function ladeBlitze(): Promise<void> {
    if (!map) return;
    blitzLaeuft = true;
    blitzZuletzt = Date.now();
    const b = map.getBounds();
    const d = await holeJson<{ strikes?: { t: number; lat: number; lon: number }[] }>(
      `/blitze?north=${b.getNorth().toFixed(2)}&south=${b.getSouth().toFixed(2)}&east=${b.getEast().toFixed(2)}&west=${b.getWest().toFixed(2)}&since=1&limit=${BLITZE_GRENZE}`,
    );
    blitzLaeuft = false;
    if (!d || !map) return;
    const jetzt = Date.now();
    setzeDaten(map, "blitze", {
      type: "FeatureCollection",
      features: (d.strikes ?? []).map((s) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [s.lon, s.lat] },
        properties: { min: Math.max(0, (jetzt - s.t) / 60000) },
      })),
    });
  }

  $effect(() => {
    const an = kartenWahl.blitze;
    if (!bereit || !map) return;
    zeige(map, EBENEN_VON.blitze, an);
    if (!an) return;
    untrack(blitzeGedrosselt);
    const takt = setInterval(blitzeGedrosselt, BLITZ_TAKT_MS);
    return () => {
      clearInterval(takt);
      clearTimeout(blitzNachzug);
      blitzNachzug = undefined;
    };
  });

  // Regenradar: Bildliste alle 3 Minuten auffrischen, der Abspieler tauscht das Bild der Ebene
  async function ladeRahmen(): Promise<void> {
    const d = await holeJson<{ data: { coords: Ecken; frames: Rahmen[] } }>("/api/v1/radar/rahmen");
    if (!map) return;
    if (!d?.data?.frames?.length) {
      radarFehlt = !abspieler.rahmen.length;
      return;
    }
    radarFehlt = false;
    ecken = d.data.coords;
    abspieler.uebernimm(d.data.frames);
  }

  $effect(() => {
    const an = kartenWahl.radar;
    if (!bereit || !map) return;
    zeige(map, EBENEN_VON.radar, an);
    if (!an) return;
    untrack(() => void ladeRahmen());
    const takt = setInterval(() => void ladeRahmen(), RADAR_TAKT_MS);
    return () => {
      clearInterval(takt);
      abspieler.stoppe();
    };
  });
</script>

<div class="karte-solo" bind:this={wurzel}>
  <div class="karte-flaeche" bind:this={flaeche}></div>
  {#if ohneKarte}<div class="karte-ohne"><i class="fa-solid fa-map"></i><span>{OHNE_WEBGL}</span></div>{/if}
  <!-- Nachtbetrieb: färbt die Karte über die Textfarbe rot (multiply statt CSS-filter, der leere Kacheln erzeugt) -->
  {#if nacht}<div class="nachtfarbe" aria-hidden="true"></div>{/if}

  <button class="karte-kopf schwebe" onclick={() => oeffne({ art: "orte" })} aria-label="Orte, gewählt {ort?.name ?? 'keiner'}">
    <span class="karte-ort">{ort?.name ?? "Karte"}<i class="fa-solid fa-chevron-down"></i></span>
    {#if kartenWahl.radar}<span class="karte-stand {radarAmOrt && jetztBild ? frische : 'ohne'}"><span class="frische"></span>{standText}</span>{/if}
  </button>

  <div class="karte-knoepfe">
    <button class="rund schwebe mein-ort" aria-label="Mein Ort" onclick={zumOrt} disabled={lon === undefined}>
      <i class="fa-solid fa-location-crosshairs"></i>
    </button>
    <button class="rund schwebe" aria-label={nacht ? "Nachtbetrieb aus" : "Nachtbetrieb an"} aria-pressed={nacht} onclick={nachtUmschalten}>
      <i class="fa-solid {nacht ? 'fa-sun' : 'fa-moon'}"></i>
    </button>
    {#each SCHALTER as s (s.ebene)}
      <button class="rund schwebe" class:an={kartenWahl[s.ebene]} aria-pressed={kartenWahl[s.ebene]} aria-label={s.titel} onclick={() => schalte(s.ebene)}>
        <i class="fa-solid {s.symbol}"></i>
      </button>
    {/each}
  </div>

  <div class="karte-unten">
    <p class="quellen"><span>Radar und Warnungen: Deutscher Wetterdienst,</span><span>Karte: OpenStreetMap-Mitwirkende</span></p>
    {#if kartenWahl.radar && abspieler.rahmen.length}<Abspielleiste {abspieler} {zone} />{/if}
  </div>
</div>

<style>
  .karte-solo {
    position: absolute;
    inset: 0;
    overflow: hidden;
    background: var(--grund);
    isolation: isolate;
  }
  .karte-flaeche,
  .nachtfarbe {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: calc(var(--leiste-h) + var(--sicher-unten));
  }
  .karte-flaeche {
    z-index: 0;
  }
  .nachtfarbe {
    z-index: 1;
    background: var(--text);
    mix-blend-mode: multiply;
    pointer-events: none;
  }
  /* Ortspunkt (Element der Markierung, daher global innerhalb der Karte) */
  .karte-solo :global(.karte-ort-punkt) {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--text);
    box-shadow:
      0 0 0 3px var(--grund),
      0 0 0 7px color-mix(in srgb, var(--text) 30%, transparent);
  }

  /* Schwebende Bedienteile über der Karte */
  .schwebe {
    background: color-mix(in srgb, var(--flaeche) 90%, transparent);
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    box-shadow: 0 6px 22px rgba(0, 0, 0, 0.5);
  }
  .karte-kopf {
    position: absolute;
    z-index: 2;
    left: max(var(--rand), env(safe-area-inset-left, 0px));
    top: calc(var(--sicher-oben) + 4px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 52px;
    min-width: 0;
    max-width: calc(100% - 2 * var(--rand) - 60px);
    padding: 5px 16px 7px;
    border-radius: 16px;
    text-align: left;
  }
  .karte-ort {
    font-size: var(--s19);
    font-weight: 700;
    line-height: 1.15;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .karte-ort i {
    margin-left: 6px;
    font-size: var(--s13);
    color: var(--text-3);
  }
  .karte-stand {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: var(--s15);
    color: var(--text-2);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .karte-stand .frische {
    width: 8px;
    height: 8px;
  }
  .karte-stand.alt .frische {
    background: var(--w1);
  }
  .karte-stand.weg .frische {
    background: var(--gefahr);
  }
  .karte-stand.ohne .frische {
    background: var(--flaeche-3);
  }
  :global(.tel[data-modus="nacht"]) .karte-stand.alt .frische {
    background: none;
    box-shadow: inset 0 0 0 2px var(--text-2);
  }

  .karte-knoepfe {
    position: absolute;
    z-index: 2;
    right: max(var(--rand), env(safe-area-inset-right, 0px));
    top: calc(var(--sicher-oben) + 4px);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .rund {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    flex: none;
    color: var(--text-3);
    font-size: var(--s17);
  }
  .rund.an {
    background: color-mix(in srgb, var(--akzent) 34%, var(--flaeche));
    color: var(--text);
  }
  .rund.mein-ort {
    color: var(--text);
    margin-bottom: 6px;
  }
  .rund:disabled {
    color: var(--flaeche-3);
  }

  .karte-unten {
    position: absolute;
    z-index: 2;
    left: max(var(--rand), env(safe-area-inset-left, 0px));
    right: max(var(--rand), env(safe-area-inset-right, 0px));
    bottom: calc(var(--leiste-h) + var(--sicher-unten) + var(--rand));
    display: flex;
    flex-direction: column;
    gap: 8px;
    pointer-events: none;
  }
  /* Pflichtangabe der Quellen, klein unten links */
  .quellen {
    align-self: flex-start;
    max-width: calc(100% - 52px); /* nie unter die Knopfreihe rechts */
    margin: 0;
    padding: 2px 8px;
    border-radius: 8px;
    background: color-mix(in srgb, var(--grund) 60%, transparent);
    color: var(--text-2);
    font-size: var(--s13);
    line-height: 1.3;
  }
  .quellen span {
    display: block;
  }
</style>
