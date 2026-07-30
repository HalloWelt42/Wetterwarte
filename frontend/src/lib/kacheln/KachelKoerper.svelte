<script lang="ts">
  import { meteocon } from "../icons";
  import { aktuell, stunden, tage, warnungen } from "../platzhalter";
  import { gehe } from "../route.svelte";
  import { wetter } from "../wetter.svelte";
  import { uhr } from "../uhr.svelte";
  import { tipp } from "../tipp";
  import { begriffe } from "../begriffe";
  import LinienChart from "../LinienChart.svelte";
  import MiniKarte from "../MiniKarte.svelte";

  let { typ, conf = {} }: { typ: string; conf?: Record<string, any> } = $props();

  // Pro-Kachel-Einstellungen (mit sinnvollen Standardwerten, wenn nicht gesetzt).
  const kennzahlen = $derived((conf.kennzahlen as string[]) ?? ["feuchte", "wind", "druck", "sicht", "taupunkt", "bewoelkung"]);
  const stundenAnzahl = $derived((conf.anzahl as number) ?? 18);
  const tageAnzahl = $derived((conf.anzahl as number) ?? 7);
  const allergien = $derived((conf.allergien as string[]) ?? []);
  const schadstoffe = $derived((conf.schadstoffe as string[]) ?? ["pm2_5", "pm10", "o3", "no2"]);

  const jetzt = $derived(wetter.aktuell ?? aktuell);
  const stundenListe = $derived(wetter.stunden.length ? wetter.stunden : stunden);
  const tageListe = $derived(wetter.tage.length ? wetter.tage : tage);
  const warnungenListe = $derived(wetter.geladen ? wetter.warnungen : warnungen);
  const luft = $derived(wetter.luft);
  const aqiVar = $derived(
    !luft ? "var(--gut)" : luft.aqi <= 40 ? "var(--gut)" : luft.aqi <= 60 ? "var(--warn)" : "var(--gefahr)",
  );
  const blitze = $derived(wetter.blitze);

  // Pollen (DWD-Gefahrenindex): Tag-Auswahl + nach Belastung sortiert.
  const pollenDaten = $derived(wetter.pollen);
  let pollenTag = $state<"today" | "tomorrow" | "dayafter">("today");
  const pollenTage = [
    { key: "today", label: "Heute" },
    { key: "tomorrow", label: "Morgen" },
    { key: "dayafter", label: "Übermorgen" },
  ] as const;
  const pollenSortiert = $derived.by(() => {
    if (!pollenDaten) return [];
    return Object.values(pollenDaten.arten)
      .map((a) => ({ icon: a.icon, name: a.name, stufe: a[pollenTag], allergie: allergien.includes(a.name) }))
      .sort((x, y) => {
        if (x.allergie !== y.allergie) return x.allergie ? -1 : 1;
        return y.stufe.value - x.stufe.value;
      });
  });
  function pollenBreite(v: number): number {
    return v < 0 ? 0 : Math.min((v / 3) * 100, 100);
  }

  // Sonne: Bogen mit Live-Marker (Vorbild alter SunWidget).
  function zuMinuten(t?: string): number {
    const m = t ? /^(\d{1,2}):(\d{2})/.exec(t) : null;
    return m ? +m[1] * 60 + +m[2] : 0;
  }
  const sonneAuf = $derived(zuMinuten(wetter.sonne?.aufgang));
  const sonneUnter = $derived(zuMinuten(wetter.sonne?.untergang));
  const jetztMin = $derived(uhr.jetzt.getHours() * 60 + uhr.jetzt.getMinutes());
  const jetztZeit = $derived(uhr.jetzt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }));
  const istTag = $derived(jetztMin >= sonneAuf && jetztMin <= sonneUnter);
  const tagLaenge = $derived(sonneUnter - sonneAuf);
  const sonneWinkel = $derived.by(() => {
    if (!sonneAuf || !sonneUnter) return Math.PI / 2;
    if (istTag && tagLaenge > 0) return Math.PI * (1 - (jetztMin - sonneAuf) / tagLaenge);
    const nachtDauer = 1440 - sonneUnter + sonneAuf;
    const f = jetztMin >= sonneUnter ? (jetztMin - sonneUnter) / nachtDauer : (1440 - sonneUnter + jetztMin) / nachtDauer;
    return -Math.PI * f;
  });
  const sonneX = $derived(60 + 50 * Math.cos(sonneWinkel));
  const sonneY = $derived(60 - 50 * Math.sin(sonneWinkel));
  const sonneFarbe = $derived.by(() => {
    if (!istTag) return "var(--flaeche-3)";
    const f = (jetztMin - sonneAuf) / tagLaenge;
    if (f < 0.12) return "#FF9800";
    if (f < 0.3) return "#FFB74D";
    if (f < 0.7) return "#FFF59D";
    if (f < 0.88) return "#FFB74D";
    return "#FF7043";
  });

  // Mondphase: rein rechnerisch (synodischer Monat).
  const SYNODISCH = 29.530588853;
  const NEUMOND0 = Date.UTC(2000, 0, 6, 18, 14, 0);
  const mond = $derived.by(() => {
    const tage = (uhr.jetzt.getTime() - NEUMOND0) / 86400000;
    const alter = ((tage % SYNODISCH) + SYNODISCH) % SYNODISCH;
    const phase = alter / SYNODISCH;
    const beleuchtung = Math.round(((1 - Math.cos(phase * 2 * Math.PI)) / 2) * 100);
    let emoji = "🌕";
    if (phase < 0.025 || phase >= 0.975) emoji = "🌑";
    else if (phase < 0.235) emoji = "🌒";
    else if (phase < 0.265) emoji = "🌓";
    else if (phase < 0.485) emoji = "🌔";
    else if (phase < 0.515) emoji = "🌕";
    else if (phase < 0.735) emoji = "🌖";
    else if (phase < 0.765) emoji = "🌗";
    else emoji = "🌘";
    const fmt = (d: number) =>
      new Date(uhr.jetzt.getTime() + d * 86400000).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
    return {
      emoji,
      beleuchtung,
      zunehmend: phase < 0.5,
      naechsterNeu: fmt(((1 - phase) % 1) * SYNODISCH),
      naechsterVoll: fmt(((0.5 - phase + 1) % 1) * SYNODISCH),
    };
  });
  const heuteKurz = $derived.by(() => {
    const wd = uhr.jetzt.toLocaleDateString("de-DE", { weekday: "short" }).replace(".", "");
    const dm = `${String(uhr.jetzt.getDate()).padStart(2, "0")}.${String(uhr.jetzt.getMonth() + 1).padStart(2, "0")}`;
    return `${wd} ${dm}`;
  });

  // Temperaturverlauf 24h als wiederverwendbarer LinienChart.
  const verlaufPunkte = $derived(stundenListe.slice(0, 24).map((s) => ({ label: s.zeit, wert: s.temp })));
  // Barometer: Luftdruck-Verlauf (falls die Stundendaten Druck liefern).
  const druckPunkte = $derived(
    stundenListe.slice(0, 24).filter((s) => s.druck != null).map((s) => ({ label: s.zeit, wert: s.druck as number })),
  );
  const druckTrend = $derived.by(() => {
    const p = druckPunkte;
    if (p.length < 4) return null;
    const d = Math.round((p[3].wert - p[0].wert) * 10) / 10;
    return { delta: d, richtung: d > 0.3 ? "steigend" : d < -0.3 ? "fallend" : "gleichbleibend" };
  });
</script>

{#if typ === "aktuell"}
  <div class="aktuell-haupt">
    <img class="mc gross" src={meteocon(jetzt.icon)} alt="" />
    <div class="aktuell-block">
      <span class="temp temp-gross {jetzt.tempKlasse}">{jetzt.temperatur}&deg;</span>
      <span class="aktuell-zustand">{jetzt.zustandText}</span>
      <span class="aktuell-gefuehlt">Gefühlt {jetzt.gefuehlt}&deg; &middot; Tageshoch {jetzt.tageshoch}&deg;</span>
    </div>
  </div>
  <div class="kv-gitter">
    {#if kennzahlen.includes("feuchte")}<div class="kv"><i class="fa-solid fa-droplet"></i><span class="kv-txt"><span class="kv-wert">{jetzt.feuchte} %</span><span class="kv-lab">Feuchte</span></span></div>{/if}
    {#if kennzahlen.includes("wind")}<div class="kv"><i class="fa-solid fa-wind"></i><span class="kv-txt"><span class="kv-wert">{jetzt.wind} km/h</span><span class="kv-lab">Wind {jetzt.windRichtung}</span></span></div>{/if}
    {#if kennzahlen.includes("druck")}<div class="kv"><i class="fa-solid fa-gauge"></i><span class="kv-txt"><span class="kv-wert">{jetzt.druck} hPa</span><span class="kv-lab">Druck</span></span></div>{/if}
    {#if kennzahlen.includes("sicht")}<div class="kv"><i class="fa-solid fa-eye"></i><span class="kv-txt"><span class="kv-wert">{jetzt.sicht} km</span><span class="kv-lab">Sicht</span></span></div>{/if}
    {#if kennzahlen.includes("taupunkt")}<div class="kv"><i class="fa-solid fa-temperature-half"></i><span class="kv-txt"><span class="kv-wert">{jetzt.taupunkt}&deg;</span><span class="kv-lab" use:tipp={begriffe.taupunkt}>Taupunkt</span></span></div>{/if}
    {#if kennzahlen.includes("bewoelkung")}<div class="kv"><i class="fa-solid fa-cloud"></i><span class="kv-txt"><span class="kv-wert">{jetzt.bewoelkung} %</span><span class="kv-lab">Bewölkung</span></span></div>{/if}
  </div>
{:else if typ === "stunden"}
  <div class="stunden">
    {#each stundenListe.slice(0, stundenAnzahl) as s}
      <div class="stunde">
        <span class="zeit">{s.zeit}</span>
        <img class="mc mittel" src={meteocon(s.icon)} alt="" />
        <span class="st-temp {s.tempKlasse}">{s.temp}&deg;</span>
        <span class="st-regen">{s.regen ? s.regen + "%" : ""}</span>
      </div>
    {/each}
  </div>
{:else if typ === "warnungen"}
  {#if warnungenListe.length}
    {#each warnungenListe as w}
      <div class="warnbanner warnstufe-{w.stufe}">
        {#if w.icon}<img class="mc mittel" src={meteocon(w.icon)} alt="" />{:else}<i class="fa-solid fa-triangle-exclamation fa-lg"></i>{/if}
        <div class="wb-txt"><div class="wb-titel">{w.titel}</div><div class="wb-zeit">{w.zeit}</div></div>
      </div>
    {/each}
  {:else}
    <div class="kw-leer"><i class="fa-solid fa-shield-halved"></i><div>Keine Warnungen aktiv</div></div>
  {/if}
{:else if typ === "karte"}
  <MiniKarte />
{:else if typ === "tage"}
  <div class="tage">
    {#each tageListe.slice(0, tageAnzahl) as t}
      <div class="tag">
        <span class="wtag">{t.kurz}</span>
        <img class="mc klein" src={meteocon(t.icon)} alt="" />
        <span class="temp-band"><span style="left: {t.bandLinks}%; right: {t.bandRechts}%"></span></span>
        <span class="hilo"><span class="hi">{t.hi}&deg;</span> <span class="lo">{t.lo}&deg;</span></span>
      </div>
    {/each}
  </div>
{:else if typ === "nowcast"}
  <div class="nowcast-text">{wetter.nowcast?.text ?? "Kein Regen in den nächsten 3 Stunden"}</div>
  <div class="nowcast-balken">
    {#each wetter.nowcast?.balken ?? [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] as h}<span class="nb" style="height: {h}%"></span>{/each}
  </div>
  <div class="nowcast-achse"><span>jetzt</span><span>+30</span><span>+60</span><span>+90 Min</span></div>
{:else if typ === "wind"}
  <div class="gauge-zeile">
    <svg class="kompass" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="44" style="fill: none; stroke: var(--rand); stroke-width: 2" />
      <g style="stroke: var(--rand-stark); stroke-width: 2">
        <line x1="50" y1="7" x2="50" y2="15" /><line x1="93" y1="50" x2="85" y2="50" /><line x1="50" y1="93" x2="50" y2="85" /><line x1="7" y1="50" x2="15" y2="50" />
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
      <div class="klein-txt"><span use:tipp={begriffe.boeen}>Böen</span> <b class="tnum">{jetzt.boeen} km/h</b></div>
      <div class="klein-txt dimm">aus {jetzt.windRichtung}</div>
    </div>
  </div>
{:else if typ === "sonne"}
  <div class="sm-bogen-wrap">
    <svg class="sm-bogen" viewBox="0 0 120 120" preserveAspectRatio="xMidYMid meet">
      <defs>
        <linearGradient id="sm-tag" x1="0%" y1="50%" x2="100%" y2="50%">
          <stop offset="0%" stop-color="#FF9800" /><stop offset="50%" stop-color="#FFEB3B" /><stop offset="100%" stop-color="#FF5722" />
        </linearGradient>
      </defs>
      <path d="M 110 60 A 50 50 0 0 1 10 60" fill="none" stroke="var(--rand)" stroke-width="2" stroke-dasharray="3 4" />
      <path d="M 10 60 A 50 50 0 0 1 110 60" fill="none" stroke="url(#sm-tag)" stroke-width="2" stroke-linecap="round" />
      <line x1="5" y1="60" x2="115" y2="60" stroke="var(--rand-stark)" stroke-width="1" />
      <circle cx={sonneX} cy={sonneY} r="11" fill={sonneFarbe} stroke={istTag ? "none" : "var(--rand-stark)"} stroke-width={istTag ? 0 : 2} stroke-dasharray={istTag ? "none" : "3 3"} />
    </svg>
    <div class="sm-mitte"><div class="sm-jetzt">Jetzt</div><div class="sm-zeit">{jetztZeit}</div></div>
  </div>
  <div class="sm-auf-unter">
    <span><span class="sm-lab">Aufgang</span><b><i class="fa-solid fa-arrow-up dimm"></i> {wetter.sonne?.aufgang ?? "-"}</b></span>
    <span class="rechts"><span class="sm-lab">Untergang</span><b>{wetter.sonne?.untergang ?? "-"} <i class="fa-solid fa-arrow-down dimm"></i></b></span>
  </div>
{:else if typ === "mond"}
  <div class="mond-datum">{heuteKurz}</div>
  <div class="mond-haupt">
    <span class="mond-gross">{mond.emoji}</span>
    <span class="mond-werte">
      <span class="dimm klein-txt">{mond.zunehmend ? "Zunehmend" : "Abnehmend"}</span>
      <span class="mond-prozent tnum">{mond.beleuchtung}%</span>
      <span class="dimm klein-txt">beleuchtet</span>
    </span>
  </div>
  <div class="mond-daten">
    <span>🌑 Neumond {mond.naechsterNeu}</span>
    <span>🌕 Vollmond {mond.naechsterVoll}</span>
  </div>
{:else if typ === "luftqualitaet"}
  <div class="gauge-zeile">
    <div class="gauge">
      <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
        <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
        <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: {aqiVar}; stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.min(100, luft?.aqi ?? 34)} 100" />
      </svg>
      <span class="gwert" style="color: {aqiVar}">{luft?.aqi ?? 34}</span>
    </div>
    <div class="spalte">
      <div class="lq-kopf"><b class="lq-stufe">{luft?.label ?? "Gut"}</b> <span class="dimm klein-txt" use:tipp={begriffe.aqi}>EU-AQI</span></div>
      <div class="lq-gitter">
        {#if schadstoffe.includes("pm2_5")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.pm25}>PM2,5</span><span class="lq-wert">{luft?.pm2_5 ?? 8}</span></div>{/if}
        {#if schadstoffe.includes("pm10")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.pm10}>PM10</span><span class="lq-wert">{luft?.pm10 ?? 15}</span></div>{/if}
        {#if schadstoffe.includes("o3")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.ozon}>O&#8323;</span><span class="lq-wert">{luft?.o3 ?? 62}</span></div>{/if}
        {#if schadstoffe.includes("no2")}<div class="lq-paar"><span class="lq-lab" use:tipp={begriffe.no2}>NO&#8322;</span><span class="lq-wert">{luft?.no2 ?? 11}</span></div>{/if}
      </div>
    </div>
  </div>
{:else if typ === "uv"}
  <div class="gauge-zeile">
    <div class="gauge">
      <svg class="spark" viewBox="0 0 100 60" preserveAspectRatio="xMidYMid meet">
        <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--flaeche-3); stroke-width: 9; stroke-linecap: round" />
        <path d="M8,54 A42,42 0 0 1 92,54" style="fill: none; stroke: var(--t-heiss); stroke-width: 9; stroke-linecap: round" pathLength="100" stroke-dasharray="{Math.round((jetzt.uv ?? 6) / 11 * 100)} 100" />
      </svg>
      <span class="gwert" style="color: var(--t-heiss)">{jetzt.uv ?? 6}</span>
    </div>
    <div class="spalte">
      <div><b>{(jetzt.uv ?? 0) >= 6 ? "Hoch" : (jetzt.uv ?? 0) >= 3 ? "Mittel" : "Niedrig"}</b></div>
      <div class="klein-txt dimm">Schutz um die Mittagszeit</div>
    </div>
  </div>
{:else if typ === "pollen"}
  {#if pollenDaten}
    <div class="pollen-kopf">
      <span class="pollen-region">{pollenDaten.region.name}{#if pollenDaten.region.partregion_name}&nbsp;<span class="dimm">&middot; {pollenDaten.region.partregion_name}</span>{/if}</span>
    </div>
    <div class="pollen-tabs">
      {#each pollenTage as t}
        <button class="pollen-tab" class:aktiv={pollenTag === t.key} onclick={() => (pollenTag = t.key)}>{t.label}</button>
      {/each}
    </div>
    <div class="pollen-liste">
      {#each pollenSortiert as p}
        <div class="pollen-zeile" class:allergie={p.allergie} class:hat-last={p.stufe.value > 0} class:viel-last={p.stufe.value >= 2}>
          <span class="pollen-info"><span class="pollen-emoji">{p.icon}</span><span class="pollen-name">{p.name}</span>{#if p.allergie}<span class="allergie-punkt" title="Deine Allergie">🔴</span>{/if}</span>
          <span class="pollen-pegel">
            <span class="pegel-bahn"><span class="pegel-fuell" style="width: {pollenBreite(p.stufe.value)}%; background: {p.stufe.color}"></span></span>
            <span class="pegel-label" style="color: {p.stufe.color}">{p.stufe.label}</span>
          </span>
        </div>
      {/each}
    </div>
    <div class="pollen-stand">Stand: {pollenDaten.last_update}</div>
  {:else}
    <div class="kw-leer"><i class="fa-solid fa-seedling"></i><div>Keine Pollendaten</div></div>
  {/if}
{:else if typ === "barometer"}
  <div class="baro-wert">
    <span class="zahl">{jetzt.druck}</span><span class="dimm" use:tipp={begriffe.hpa}>hPa</span>
    {#if druckTrend}
      <span class="tendenz" style="color: {druckTrend.delta > 0.3 ? 'var(--gut)' : druckTrend.delta < -0.3 ? 'var(--gefahr)' : 'var(--text-3)'}">
        <i class="fa-solid {druckTrend.delta > 0.3 ? 'fa-arrow-trend-up' : druckTrend.delta < -0.3 ? 'fa-arrow-trend-down' : 'fa-arrow-right-long'}"></i>
        {druckTrend.delta > 0 ? "+" : ""}{druckTrend.delta} / 3 h
      </span>
    {/if}
  </div>
  {#if druckPunkte.length}
    <LinienChart punkte={druckPunkte} farbe="#8b5cf6" jetztIndex={0} />
  {/if}
  <div class="klein-txt dimm">Tendenz {druckTrend?.richtung ?? "gleichbleibend"}</div>
{:else if typ === "blitze"}
  <div class="reihe" style="gap: var(--a3)">
    <img class="mc mittel" src={meteocon("lightning-bolt")} alt="" />
    <div><span class="blitz-zahl">{blitze?.anzahl ?? 0}</span> <span class="dimm klein-txt">letzte Stunde</span></div>
  </div>
  {#if blitze?.liste?.length}
    <div class="blitz-liste">{#each blitze.liste as b}<div class="bz"><span>{b.zeit}</span><span>{b.distanz}</span></div>{/each}</div>
  {:else}
    <div class="klein-txt dimm" style="margin-top: var(--a2)">Keine Blitze in der Nähe</div>
  {/if}
{:else if typ === "verlauf"}
  <LinienChart punkte={verlaufPunkte} farbe="#f59e0b" einheit="&deg;" jetztIndex={0} />
{/if}
