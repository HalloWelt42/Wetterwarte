<script lang="ts">
  import { onMount } from "svelte";
  import { GridStack } from "gridstack";
  import { meteocon } from "./icons";
  import { aktuell, stunden, tage, warnungen } from "./platzhalter";
  import { gehe } from "./route.svelte";
  import { ui } from "./ui.svelte";
  import { sende } from "./api";
  import { layoutState } from "./layout.svelte";
  import { wetter } from "./wetter.svelte";

  // Echte Daten mit Rueckfall auf Platzhalter, solange nichts geladen ist.
  const jetzt = $derived(wetter.aktuell ?? aktuell);
  const stundenListe = $derived(wetter.stunden.length ? wetter.stunden : stunden);
  const tageListe = $derived(wetter.tage.length ? wetter.tage : tage);
  const warnungenListe = $derived(wetter.geladen ? wetter.warnungen : warnungen);
  const luft = $derived(wetter.luft);
  const aqiVar = $derived(
    !luft ? "var(--gut)" : luft.aqi <= 40 ? "var(--gut)" : luft.aqi <= 60 ? "var(--warn)" : "var(--gefahr)",
  );

  let brettEl: HTMLElement;
  let grid: GridStack | undefined;
  let angewendet: string | null = null;
  let ladend = false;

  // Stabile IDs in DOM-Reihenfolge - fuer Speichern/Laden der Anordnung.
  const kachelIds = [
    "aktuell", "stunden", "warnungen", "karte", "tage", "nowcast",
    "wind", "sonnemond", "luftqualitaet", "uv", "barometer", "verlauf",
  ];

  interface Position {
    id: string;
    x: number;
    y: number;
    w: number;
    h: number;
  }

  function anwenden(daten: Position[]): void {
    if (!grid || !Array.isArray(daten) || !daten.length) return;
    ladend = true;
    grid.batchUpdate();
    for (const p of daten) {
      const el = brettEl.querySelector<HTMLElement>(`[gs-id="${p.id}"]`);
      if (el) grid.update(el, { x: p.x, y: p.y, w: p.w, h: p.h });
    }
    grid.commit();
    ladend = false;
  }

  onMount(() => {
    grid = GridStack.init(
      {
        column: 12,
        cellHeight: 74,
        margin: 6,
        float: false,
        handle: ".kw-kopf",
        resizable: { handles: "se" },
      },
      brettEl,
    );

    // Jeder Kachel eine stabile ID geben.
    const kacheln = Array.from(brettEl.querySelectorAll<HTMLElement>(".grid-stack-item"));
    kacheln.forEach((el, i) => {
      const id = kachelIds[i];
      if (!id) return;
      el.setAttribute("gs-id", id);
      const knoten = (el as unknown as { gridstackNode?: { id?: string } }).gridstackNode;
      if (knoten) knoten.id = id;
    });

    let entprellen: ReturnType<typeof setTimeout> | undefined;
    grid.on("change", () => {
      const id = layoutState.aktivId;
      if (ladend || !id || !grid) return;
      const daten = grid.save(false) as Position[];
      clearTimeout(entprellen);
      entprellen = setTimeout(() => {
        void sende(`/layouts/${id}`, "PUT", { daten });
        const l = layoutState.liste.find((x) => x.id === id);
        if (l) l.daten = daten;
      }, 600);
    });

    return () => grid?.destroy(false);
  });

  // Auf Layout-Wechsel reagieren: gespeicherte Anordnung anwenden oder ein leeres
  // Layout mit der aktuellen Anordnung initialisieren.
  $effect(() => {
    const id = layoutState.aktivId;
    if (!grid || !id || id === angewendet) return;
    const l = layoutState.liste.find((x) => x.id === id);
    if (!l) return;
    angewendet = id;
    if (Array.isArray(l.daten) && l.daten.length) {
      anwenden(l.daten as Position[]);
    } else {
      const daten = grid.save(false) as Position[];
      l.daten = daten;
      void sende(`/layouts/${id}`, "PUT", { daten });
    }
  });
</script>

<div class="grid-stack brett-stack" bind:this={brettEl}>
  <!-- 1) Aktuell -->
  <div class="grid-stack-item" gs-w="4" gs-h="3">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Aktuell <span class="ort">{wetter.ort}</span></span>
          <span class="kw-werkz">
            <button class="icon-knopf" title="Einstellungen" onclick={() => (ui.einstellungen = "Aktuell")}><i class="fa-solid fa-sliders"></i></button>
          </span>
        </div>
        <div class="kw-koerper">
          <div class="aktuell-haupt">
            <img class="mc gross" src={meteocon(jetzt.icon)} alt="" />
            <div class="aktuell-block">
              <span class="temp temp-gross {jetzt.tempKlasse}">{jetzt.temperatur}&deg;</span>
              <span class="aktuell-zustand">{jetzt.zustandText}</span>
              <span class="aktuell-gefuehlt">Gefühlt {jetzt.gefuehlt}&deg; &middot; Tageshoch {jetzt.tageshoch}&deg;</span>
            </div>
          </div>
          <div class="kv-gitter">
            <div class="kv"><i class="fa-solid fa-droplet"></i><span class="kv-txt"><span class="kv-wert">{jetzt.feuchte} %</span><span class="kv-lab">Feuchte</span></span></div>
            <div class="kv"><i class="fa-solid fa-wind"></i><span class="kv-txt"><span class="kv-wert">{jetzt.wind} km/h</span><span class="kv-lab">Wind {jetzt.windRichtung}</span></span></div>
            <div class="kv"><i class="fa-solid fa-gauge"></i><span class="kv-txt"><span class="kv-wert">{jetzt.druck} hPa</span><span class="kv-lab">Druck</span></span></div>
            <div class="kv"><i class="fa-solid fa-eye"></i><span class="kv-txt"><span class="kv-wert">{jetzt.sicht} km</span><span class="kv-lab">Sicht</span></span></div>
            <div class="kv"><i class="fa-solid fa-temperature-half"></i><span class="kv-txt"><span class="kv-wert">{jetzt.taupunkt}&deg;</span><span class="kv-lab">Taupunkt</span></span></div>
            <div class="kv"><i class="fa-solid fa-cloud"></i><span class="kv-txt"><span class="kv-wert">{jetzt.bewoelkung} %</span><span class="kv-lab">Bewölkung</span></span></div>
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 2) Stundenvorhersage -->
  <div class="grid-stack-item" gs-w="8" gs-h="3">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Stundenvorhersage <span class="ort">48 Stunden</span></span>
        </div>
        <div class="kw-koerper">
          <div class="stunden">
            {#each stundenListe as s}
              <div class="stunde">
                <span class="zeit">{s.zeit}</span>
                <img class="mc mittel" src={meteocon(s.icon)} alt="" />
                <span class="st-temp {s.tempKlasse}">{s.temp}&deg;</span>
                <span class="st-regen">{s.regen ? s.regen + "%" : ""}</span>
              </div>
            {/each}
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 3) Warnungen -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Wetterwarnungen <span class="ort">Burgenlandkreis</span></span>
        </div>
        <div class="kw-koerper">
          {#if warnungenListe.length}
            {#each warnungenListe as w}
              <div class="warnbanner warnstufe-{w.stufe}">
                {#if w.icon}
                  <img class="mc mittel" src={meteocon(w.icon)} alt="" />
                {:else}
                  <i class="fa-solid fa-triangle-exclamation fa-lg"></i>
                {/if}
                <div class="wb-txt"><div class="wb-titel">{w.titel}</div><div class="wb-zeit">{w.zeit}</div></div>
              </div>
            {/each}
          {:else}
            <div class="kw-leer"><i class="fa-solid fa-shield-halved"></i><div>Keine Warnungen aktiv</div></div>
          {/if}
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 4) Karte -->
  <div class="grid-stack-item" gs-w="4" gs-h="4">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Karte <span class="ort">Radar</span></span>
          <span class="kw-werkz"><button class="icon-knopf" title="Groß" onclick={() => gehe("karte")}><i class="fa-solid fa-up-right-and-down-left-from-center"></i></button></span>
        </div>
        <div class="kw-koerper">
          <div class="karten-flaeche">
            <div class="radar-blob" style="width: 90px; height: 70px; left: 28%; top: 34%"></div>
            <div class="radar-blob" style="width: 54px; height: 46px; left: 55%; top: 55%; opacity: 0.55"></div>
            <div class="karten-steuer">
              <button class="icon-knopf" title="Ebenen"><i class="fa-solid fa-layer-group"></i></button>
              <button class="icon-knopf" title="Vergrößern"><i class="fa-solid fa-plus"></i></button>
              <button class="icon-knopf" title="Verkleinern"><i class="fa-solid fa-minus"></i></button>
            </div>
            <div class="overlay-leiste">
              <span class="chip aktiv">Radar</span>
              <span class="chip">Wind</span>
              <span class="chip">Warnungen</span>
            </div>
            <div class="karten-legende">Niederschlag mm/h<div class="legende-skala"></div></div>
            <div class="attribution">&copy; OpenStreetMap &middot; DWD RADOLAN</div>
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 5) 7-Tage -->
  <div class="grid-stack-item" gs-w="4" gs-h="4">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">7-Tage-Vorhersage</span>
        </div>
        <div class="kw-koerper">
          <div class="tage">
            {#each tageListe as t}
              <div class="tag">
                <span class="wtag">{t.kurz}</span>
                <img class="mc klein" src={meteocon(t.icon)} alt="" />
                <span class="temp-band"><span style="left: {t.bandLinks}%; right: {t.bandRechts}%"></span></span>
                <span class="hilo"><span class="hi">{t.hi}&deg;</span> <span class="lo">{t.lo}&deg;</span></span>
              </div>
            {/each}
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 6) Regen-Nowcast -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Regen-Nowcast <span class="ort">Köln</span></span>
        </div>
        <div class="kw-koerper">
          <div class="nowcast-text">{wetter.nowcast?.text ?? "Kein Regen in den nächsten 3 Stunden"}</div>
          <div class="nowcast-balken">
            {#each wetter.nowcast?.balken ?? [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] as h}
              <span class="nb" style="height: {h}%"></span>
            {/each}
          </div>
          <div class="nowcast-achse"><span>jetzt</span><span>+30</span><span>+60</span><span>+90 Min</span></div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 7) Wind -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Wind</span>
        </div>
        <div class="kw-koerper">
          <div class="gauge-zeile">
            <svg class="kompass" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="44" style="fill: none; stroke: var(--rand); stroke-width: 2" />
              <g style="stroke: var(--rand-stark); stroke-width: 2">
                <line x1="50" y1="7" x2="50" y2="15" /><line x1="93" y1="50" x2="85" y2="50" />
                <line x1="50" y1="93" x2="50" y2="85" /><line x1="7" y1="50" x2="15" y2="50" />
              </g>
              <text x="50" y="22" text-anchor="middle" style="fill: var(--text-3); font-size: 9px">N</text>
              <g transform="rotate({(jetzt.windGrad ?? 315) - 315} 50 50)">
                <line x1="50" y1="50" x2="32" y2="32" style="stroke: var(--akzent); stroke-width: 3; stroke-linecap: round" />
                <polygon points="32,32 43,34 34,43" style="fill: var(--akzent)" />
              </g>
              <circle cx="50" cy="50" r="4" style="fill: var(--akzent)" />
            </svg>
            <div class="spalte">
              <div><span class="temp temp-mittel">{jetzt.wind}</span> <span class="dimm">km/h</span></div>
              <div class="klein-txt">Böen <b class="tnum">{jetzt.boeen} km/h</b></div>
              <div class="klein-txt dimm">aus {jetzt.windRichtung}</div>
            </div>
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 8) Sonne und Mond -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Sonne und Mond</span>
        </div>
        <div class="kw-koerper">
          <svg class="sonnenbogen" viewBox="0 0 200 70" preserveAspectRatio="xMidYMid meet">
            <path d="M8,62 Q100,-4 192,62" style="fill: none; stroke: var(--rand); stroke-width: 2; stroke-dasharray: 3 4" />
            <path d="M8,62 Q100,-4 192,62" style="fill: none; stroke: var(--warn); stroke-width: 2.5" pathLength="100" stroke-dasharray="66 100" />
            <circle cx="140" cy="17" r="6" style="fill: var(--warn)" />
          </svg>
          <div class="sm-zeiten">
            <span><i class="fa-solid fa-arrow-up dimm"></i> {wetter.sonne?.aufgang ?? "05:42"}</span>
            <span class="reihe"><img class="mc winzig" src={meteocon("moon-waxing-gibbous")} alt="" /> zunehmend 78%</span>
            <span><i class="fa-solid fa-arrow-down dimm"></i> {wetter.sonne?.untergang ?? "21:18"}</span>
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 9) Luftqualitaet -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Luftqualität <span class="ort">Köln</span></span>
        </div>
        <div class="kw-koerper">
          <div class="gauge-zeile">
            <div class="gauge">
              <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
                <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
                <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: {aqiVar}; stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.min(100, luft?.aqi ?? 34)} 100" />
              </svg>
              <span class="gwert" style="color: {aqiVar}">{luft?.aqi ?? 34}</span>
            </div>
            <div class="spalte">
              <div><b>{luft?.label ?? "Gut"}</b> <span class="dimm klein-txt">(EU-AQI)</span></div>
              <div class="klein-txt tnum">PM2,5 {luft?.pm2_5 ?? 8} &middot; PM10 {luft?.pm10 ?? 15}</div>
              <div class="klein-txt tnum">O3 {luft?.o3 ?? 62} &middot; NO2 {luft?.no2 ?? 11}</div>
            </div>
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 10) UV-Index -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">UV-Index</span>
        </div>
        <div class="kw-koerper">
          <div class="gauge-zeile">
            <div class="gauge">
              <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
                <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
                <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--t-heiss); stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.round((jetzt.uv ?? 6) / 11 * 100)} 100" />
              </svg>
              <span class="gwert" style="color: var(--t-heiss)">{jetzt.uv ?? 6}</span>
            </div>
            <div class="spalte">
              <div><b>Hoch</b></div>
              <div class="klein-txt dimm">Schutz 11 - 15 Uhr</div>
              <div class="klein-txt dimm">Maximum 13:20 Uhr</div>
            </div>
          </div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 11) Barometer -->
  <div class="grid-stack-item" gs-w="4" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Luftdruck</span>
        </div>
        <div class="kw-koerper">
          <div class="baro-wert"><span class="zahl">{jetzt.druck}</span><span class="dimm">hPa</span><span class="tendenz faellt"><i class="fa-solid fa-arrow-trend-down"></i> -2,4 / 3 h</span></div>
          <svg class="spark" viewBox="0 0 100 30" preserveAspectRatio="none" style="height: 34px; margin-top: 8px">
            <polyline points="0,8 16,7 32,9 48,13 64,17 80,20 100,24" style="fill: none; stroke: var(--gefahr); stroke-width: 2" />
          </svg>
          <div class="klein-txt dimm">Fallend - Wetterverschlechterung wahrscheinlich</div>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>

  <!-- 12) Temperaturverlauf -->
  <div class="grid-stack-item" gs-w="8" gs-h="2">
    <div class="grid-stack-item-content">
      <div class="kachel-w">
        <div class="kw-kopf">
          <i class="fa-solid fa-grip-vertical kw-griffpunkte"></i>
          <span class="kw-titel">Temperaturverlauf <span class="ort">Letzte 24 Stunden - Archiv</span></span>
          <span class="kw-werkz"><span class="segment"><button class="aktiv">24 h</button><button>7 T</button><button>30 T</button></span></span>
        </div>
        <div class="kw-koerper">
          <svg class="chart-flaeche" viewBox="0 0 320 96" preserveAspectRatio="none">
            <defs>
              <linearGradient id="tflaeche" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stop-color="#2f7ce0" stop-opacity="0.30" />
                <stop offset="1" stop-color="#2f7ce0" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path d="M0,72 L26,74 L52,78 L78,70 L104,54 L130,40 L156,30 L182,26 L208,30 L234,38 L260,50 L286,60 L320,64 L320,96 L0,96 Z" fill="url(#tflaeche)" />
            <polyline points="0,72 26,74 52,78 78,70 104,54 130,40 156,30 182,26 208,30 234,38 260,50 286,60 320,64" style="fill: none; stroke: var(--akzent); stroke-width: 2" />
          </svg>
        </div>
        <span class="kw-griff"></span>
      </div>
    </div>
  </div>
</div>
