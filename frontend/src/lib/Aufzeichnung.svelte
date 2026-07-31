<script lang="ts">
  // Aufzeichnungs-Manager: steuert je Ort und Variable, was dauerhaft archiviert wird.
  // Echte Daten aus dem Backend (/aufzeichnung); jede Aenderung wird sofort gespeichert.
  import { onMount } from "svelte";
  import { hole, sende } from "./api";
  import HilfeLink from "./HilfeLink.svelte";

  interface Eintrag {
    ort: string;
    name: string;
    region: string;
    variablen: string[];
    aktiv: boolean;
    anzahl: number;
  }
  interface VarDef {
    wert: string;
    label: string;
  }

  interface RadarArchiv {
    aktiv: boolean;
    stunden: number;
    anzahl: number;
    aeltest: string | null;
    neuest: string | null;
    bytes: number;
  }
  interface Takt {
    intervall_min: number;
    min: number;
    max: number;
    standard: number;
  }

  let orte = $state<Eintrag[]>([]);
  let verfuegbar = $state<VarDef[]>([]);
  let geladen = $state(false);
  let radar = $state<RadarArchiv | null>(null);
  let takt = $state<Takt | null>(null);

  // Auswahl an Takt-Stufen (Minuten), auf den erlaubten Bereich begrenzt.
  const taktStufen = $derived((takt ? [5, 10, 15, 20, 30, 45, 60] : []).filter((m) => takt && m >= takt.min && m <= takt.max));
  const taktMin = $derived(takt?.intervall_min ?? 10);

  async function lade(): Promise<void> {
    try {
      const d = await hole<{ orte: Eintrag[]; verfuegbar: VarDef[]; takt: Takt }>("/aufzeichnung");
      orte = d.orte;
      verfuegbar = d.verfuegbar;
      takt = d.takt;
    } catch {
      /* leer lassen */
    }
    try {
      radar = await hole<RadarArchiv>("/radar/archiv");
    } catch {
      /* Radar-Archiv optional */
    }
    geladen = true;
  }
  onMount(lade);

  async function setzeTakt(minuten: number): Promise<void> {
    try {
      const d = await sende<{ intervall_min: number }>("/aufzeichnung/takt", "PUT", { intervall_min: minuten });
      if (takt) takt = { ...takt, intervall_min: d.intervall_min };
    } catch {
      /* still */
    }
  }

  async function setzeRadar(aktiv: boolean, stunden: number): Promise<void> {
    try {
      radar = await sende<RadarArchiv>("/radar/archiv", "PUT", { aktiv, stunden });
    } catch {
      /* still */
    }
  }
  function fmtBytes(b: number): string {
    if (b < 1024) return `${b} B`;
    if (b < 1048576) return `${Math.round(b / 1024)} KB`;
    return `${(b / 1048576).toFixed(1)} MB`;
  }
  const radarZeitraum = $derived.by(() => {
    if (!radar?.aeltest || !radar?.neuest) return "";
    const f = (s: string) => new Date(s).toLocaleString("de-DE", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
    return `${f(radar.aeltest)} - ${f(radar.neuest)}`;
  });

  async function speichere(e: Eintrag): Promise<void> {
    try {
      await sende(`/aufzeichnung/${e.ort}`, "PUT", { variablen: e.variablen, aktiv: e.aktiv });
    } catch {
      /* still */
    }
  }
  function toggleAktiv(e: Eintrag): void {
    e.aktiv = !e.aktiv;
    void speichere(e);
  }
  function toggleVar(e: Eintrag, v: string): void {
    e.variablen = e.variablen.includes(v) ? e.variablen.filter((x) => x !== v) : [...e.variablen, v];
    void speichere(e);
  }

  const gesamt = $derived(orte.reduce((s, e) => s + e.anzahl, 0));
</script>

<section class="inhalt">
  <div class="seite">
    <h1>Aufzeichnungs-Manager <HilfeLink topic="aufzeichnung" /></h1>
    <p class="unter-gross">
      Die PostgreSQL zeichnet ausgewählte Orte langfristig auf. Lege je Ort und Variable fest, was dauerhaft
      archiviert wird. Neue Orte werden automatisch aufgezeichnet, bis du es hier änderst.
    </p>

    {#if takt}
      <div class="panel">
        <h2><i class="fa-solid fa-clock"></i> Aufzeichnungs-Takt</h2>
        <p class="unter">
          Abstand zwischen zwei Messpunkten. Ein enger Takt liefert mehr Auflösung für die Statistik - gerade bei
          kleinschrittigen Einzelwerten. Gilt für alle aufgezeichneten Orte und Variablen.
        </p>
        <div class="formzeile">
          <label for="takt-wahl">Alle</label>
          <select id="takt-wahl" class="feld" value={takt.intervall_min} onchange={(e) => setzeTakt(+e.currentTarget.value)}>
            {#each taktStufen as m}
              <option value={m}>{m} Minuten{m === takt.standard ? " (Standard)" : ""}</option>
            {/each}
          </select>
        </div>
      </div>
    {/if}

    <div class="panel">
      <h2><i class="fa-solid fa-database"></i> Aufgezeichnete Orte</h2>
      <p class="unter">Der Schalter je Zeile startet oder beendet die Aufzeichnung; die Felder wählen die Variablen.</p>

      {#if geladen && orte.length === 0}
        <div class="kw-leer"><i class="fa-solid fa-database"></i><div>Noch keine Orte. Füge oben über die Suche einen Ort hinzu.</div></div>
      {/if}

      {#each orte as e}
        <div class="tabzeile">
          <i class="fa-solid fa-location-dot" style="color: var(--akzent)"></i>
          <span class="tz-name">{e.name} <small>{e.region}</small></span>
          <span class="reihe" style="flex-wrap: wrap; gap: var(--a1)">
            {#each verfuegbar as v}
              <button class="chip chip-knopf" class:chip-an={e.variablen.includes(v.wert)} onclick={() => toggleVar(e, v.wert)}>{v.label}</button>
            {/each}
          </span>
          <span class="tz-meta tnum">{e.anzahl.toLocaleString("de-DE")} Werte</span>
          <button class="schalter" class:an={e.aktiv} onclick={() => toggleAktiv(e)} aria-label="Aufzeichnung {e.name}"></button>
        </div>
      {/each}
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-satellite-dish"></i> Radar-Archiv <HilfeLink topic="karte" find="Radar" /></h2>
      <p class="unter">
        Speichert die gemessenen Radar-Bilder historisch, damit du im Radar-Abspieler weiter in die
        Vergangenheit zurückblättern kannst. Optional - beansprucht Speicher in der Datenbank.
      </p>
      <div class="formzeile-quer">
        <span class="fz-lab">Radar historisch speichern</span>
        <button
          class="schalter"
          class:an={radar?.aktiv}
          onclick={() => setzeRadar(!radar?.aktiv, radar?.stunden ?? 24)}
          aria-label="Radar historisch speichern"
        ></button>
      </div>
      {#if radar?.aktiv}
        <div class="formzeile">
          <label for="radar-stunden">Aufbewahrung (Stunden)</label>
          <input
            id="radar-stunden"
            class="feld"
            type="number"
            min="1"
            max="336"
            value={radar.stunden}
            onchange={(e) => setzeRadar(true, +e.currentTarget.value)}
          />
        </div>
        <p class="unter">
          Gespeichert: <b class="tnum">{radar.anzahl}</b> Frames &middot; <b class="tnum">{fmtBytes(radar.bytes)}</b>
          {#if radarZeitraum}&middot; {radarZeitraum}{/if}. Neue Frames kommen alle {taktMin} Minuten dazu.
        </p>
      {/if}
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-hard-drive"></i> Archiv</h2>
      <p class="unter">
        Insgesamt <b class="tnum">{gesamt.toLocaleString("de-DE")}</b> gespeicherte Messwerte über {orte.length}
        {orte.length === 1 ? "Ort" : "Orte"}. Neue Werte kommen alle {taktMin} Minuten dazu; der Verlauf steht in der
        Historie-Kachel und unter Archiv zur Verfügung.
      </p>
    </div>
  </div>
</section>
