<script lang="ts">
  // Offline-Kartencache: Speicher-Statistik je Thema + Fuell-Bot (Start/Stopp,
  // Fortschritt, Fehler-/Fertig-Logik). Fragt das Backend, pollt waehrend des Laufs.
  import { onMount, onDestroy } from "svelte";
  import { hole, sende } from "./api";

  interface Thema {
    anbieter: string;
    anzahl: number;
    bytes: number;
  }
  interface Bot {
    laufend: boolean;
    gesamt: number;
    fertig: number;
    fehler: number;
    anbieter: string;
    gebiet: string;
    fehlermeldung: string;
    stand: string | null;
  }
  interface Statistik {
    themen: Thema[];
    anzahl: number;
    bytes: number;
    bot: Bot;
  }

  const NAME: Record<string, string> = { dark: "Karte dunkel", light: "Karte hell", satellite: "Satellit", voyager: "Beschriftung" };

  let stat = $state<Statistik | null>(null);
  let auswahl = $state<Record<string, boolean>>({ dark: true, light: true, satellite: true, voyager: true });
  let zoomDe = $state(8);
  let zoomHeim = $state(11);
  let poll: ReturnType<typeof setInterval> | undefined;
  let schaetzung = $state<{ anzahl: number; bytes: number } | null>(null);
  let schaetzTimer: ReturnType<typeof setTimeout> | undefined;

  // Grob-Schaetzung des Datenvolumens vorab (aktualisiert sich entprellt mit der Auswahl).
  $effect(() => {
    const anbieter = Object.entries(auswahl)
      .filter(([, an]) => an)
      .map(([k]) => k)
      .join(",");
    const zd = zoomDe;
    const zh = zoomHeim;
    if (stat?.bot.laufend) return; // waehrend des Laufs nicht schaetzen
    clearTimeout(schaetzTimer);
    schaetzTimer = setTimeout(async () => {
      try {
        schaetzung = await hole<{ anzahl: number; bytes: number }>(
          `/kachel/schaetzung?anbieter=${anbieter}&zoom_deutschland=${zd}&zoom_heimat=${zh}`,
        );
      } catch {
        /* still */
      }
    }, 300);
  });

  function fmt(b: number): string {
    if (b < 1024) return `${b} B`;
    if (b < 1048576) return `${Math.round(b / 1024)} KB`;
    if (b < 1073741824) return `${(b / 1048576).toFixed(1)} MB`;
    return `${(b / 1073741824).toFixed(2)} GB`;
  }

  async function lade(): Promise<void> {
    try {
      stat = await hole<Statistik>("/kachel/statistik");
      // Waehrend der Bot laeuft, engmaschig pollen; sonst ruhen lassen.
      if (stat.bot.laufend && !poll) poll = setInterval(lade, 1500);
      if (!stat.bot.laufend && poll) {
        clearInterval(poll);
        poll = undefined;
      }
    } catch {
      /* still */
    }
  }

  async function starten(): Promise<void> {
    const anbieter = Object.entries(auswahl)
      .filter(([, an]) => an)
      .map(([k]) => k);
    try {
      const bot = await sende<Bot>("/kachel/fuellbot", "POST", { anbieter, zoom_deutschland: zoomDe, zoom_heimat: zoomHeim });
      if (stat) stat.bot = bot;
      if (!poll) poll = setInterval(lade, 1500);
    } catch {
      /* still */
    }
  }

  async function stoppen(): Promise<void> {
    try {
      await sende("/kachel/fuellbot", "DELETE");
      void lade();
    } catch {
      /* still */
    }
  }

  onMount(lade);
  onDestroy(() => poll && clearInterval(poll));

  const bot = $derived(stat?.bot);
  const anteilProzent = $derived(bot && bot.gesamt > 0 ? Math.round((bot.fertig + bot.fehler) / bot.gesamt * 100) : 0);
  const maxBytes = $derived(stat ? Math.max(1, ...stat.themen.map((t) => t.bytes)) : 1);
</script>

<div class="speicher">
  <h3 class="sp-titel">Offline-Kartencache</h3>
  <p class="unter">
    Kartenkacheln werden auf dem Server dauerhaft gespeichert (getrennt nach Thema), damit die Karte auch bei
    Ausfall lädt und schneller wird. Der Füll-Bot lädt Deutschland vor - rund um den Wohnort in mehr Details.
  </p>

  {#if stat}
    <div class="sp-themen">
      {#each stat.themen as t}
        <div class="sp-thema">
          <span class="sp-name">{NAME[t.anbieter] ?? t.anbieter}</span>
          <span class="sp-bahn"><span class="sp-fuell" style="width: {Math.round((t.bytes / maxBytes) * 100)}%"></span></span>
          <span class="sp-meta tnum">{t.anzahl.toLocaleString("de-DE")} · {fmt(t.bytes)}</span>
        </div>
      {/each}
    </div>
    <p class="sp-gesamt">Gesamt: <b class="tnum">{stat.anzahl.toLocaleString("de-DE")}</b> Kacheln · <b class="tnum">{fmt(stat.bytes)}</b></p>

    <div class="sp-bot">
      <div class="sp-chips">
        {#each Object.keys(NAME) as a}
          <button class="chip chip-knopf" class:chip-an={auswahl[a]} onclick={() => (auswahl[a] = !auswahl[a])} disabled={bot?.laufend}>{NAME[a]}</button>
        {/each}
      </div>
      <div class="sp-zooms">
        <label class="sp-zoom">Deutschland bis Zoom <b class="tnum">{zoomDe}</b>
          <input type="range" min="5" max="9" bind:value={zoomDe} disabled={bot?.laufend} /></label>
        <label class="sp-zoom">Wohnort bis Zoom <b class="tnum">{zoomHeim}</b>
          <input type="range" min={zoomDe} max="13" bind:value={zoomHeim} disabled={bot?.laufend} /></label>
      </div>

      {#if bot?.laufend}
        <div class="sp-fortschritt">
          <div class="sp-pbahn"><span class="sp-pfuell" style="width: {anteilProzent}%"></span></div>
          <div class="sp-pinfo klein-txt">
            <span>{bot.fertig.toLocaleString("de-DE")} / {bot.gesamt.toLocaleString("de-DE")} ({anteilProzent}%)</span>
            <span class="dimm">{NAME[bot.anbieter] ?? bot.anbieter} · {bot.gebiet}</span>
            {#if bot.fehler > 0}<span style="color: var(--warn)">{bot.fehler} Fehler</span>{/if}
          </div>
        </div>
        <button class="knopf" onclick={stoppen}><i class="fa-solid fa-stop"></i> Stoppen</button>
      {:else}
        {#if bot && bot.stand}
          <p class="sp-fertig klein-txt">
            <i class="fa-solid fa-circle-check" style="color: var(--gut)"></i>
            Zuletzt: {bot.fertig.toLocaleString("de-DE")} geladen{#if bot.fehler > 0}, <span style="color: var(--warn)">{bot.fehler} Fehler</span>{/if}.
          </p>
        {/if}
        {#if bot?.fehlermeldung}<p class="klein-txt" style="color: var(--gefahr)">{bot.fehlermeldung}</p>{/if}
        {#if schaetzung}
          <p class="klein-txt dimm" style="margin: 0">
            Diese Aktion lädt grob <b class="tnum">{schaetzung.anzahl.toLocaleString("de-DE")}</b> Kacheln
            (~<b class="tnum">{fmt(schaetzung.bytes)}</b>). Nur neue Kacheln werden geladen.
          </p>
        {/if}
        <button class="knopf primaer" onclick={starten}><i class="fa-solid fa-download"></i> Füllen starten</button>
      {/if}
    </div>
  {:else}
    <div class="kw-leer"><i class="fa-solid fa-spinner fa-spin"></i><div>Speicher wird geladen ...</div></div>
  {/if}
</div>
