<script lang="ts">
  // Aufzeichnungs-Manager: steuert je Ort und Variable, was dauerhaft archiviert wird.
  // Echte Daten aus dem Backend (/aufzeichnung); jede Aenderung wird sofort gespeichert.
  import { onMount } from "svelte";
  import { hole, sende } from "./api";

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

  let orte = $state<Eintrag[]>([]);
  let verfuegbar = $state<VarDef[]>([]);
  let geladen = $state(false);

  async function lade(): Promise<void> {
    try {
      const d = await hole<{ orte: Eintrag[]; verfuegbar: VarDef[] }>("/aufzeichnung");
      orte = d.orte;
      verfuegbar = d.verfuegbar;
    } catch {
      /* leer lassen */
    }
    geladen = true;
  }
  onMount(lade);

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
    <h1>Aufzeichnungs-Manager</h1>
    <p class="unter-gross">
      Die PostgreSQL zeichnet ausgewählte Orte langfristig auf. Lege je Ort und Variable fest, was dauerhaft
      archiviert wird. Neue Orte werden automatisch aufgezeichnet, bis du es hier änderst.
    </p>

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
      <h2><i class="fa-solid fa-hard-drive"></i> Archiv</h2>
      <p class="unter">
        Insgesamt <b class="tnum">{gesamt.toLocaleString("de-DE")}</b> gespeicherte Messwerte über {orte.length}
        {orte.length === 1 ? "Ort" : "Orte"}. Neue Werte kommen alle 10 Minuten dazu; der Verlauf steht in der
        Historie-Kachel und unter Archiv zur Verfügung.
      </p>
    </div>
  </div>
</section>
