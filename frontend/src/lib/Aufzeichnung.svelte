<script lang="ts">
  interface Station {
    icon: string;
    name: string;
    kennung: string;
    variablen: string[];
    zeitraum: string;
  }

  const stationen: Station[] = [
    { icon: "fa-tower-broadcast", name: "Köln", kennung: "DWD 04501 · 51,05° N 12,14° O", variablen: ["Temperatur", "Niederschlag", "Wind", "Druck", "Feuchte"], zeitraum: "seit 2019" },
    { icon: "fa-tower-broadcast", name: "Frankfurt-Holzhausen", kennung: "DWD 02928 · 51,31° N 12,45° O", variablen: ["Temperatur", "Niederschlag", "Wind", "Feuchte"], zeitraum: "seit 2021" },
    { icon: "fa-tower-broadcast", name: "Berlin-Tempelhof", kennung: "DWD 00433 · 52,47° N 13,40° O", variablen: ["Temperatur", "Niederschlag", "Druck"], zeitraum: "unbegrenzt" },
    { icon: "fa-location-dot", name: "Garten Köln", kennung: "Eigener Punkt · 51,05° N 12,14° O", variablen: ["Temperatur", "Niederschlag", "Feuchte"], zeitraum: "seit 2023" },
  ];

  let aktiv = $state(stationen.map(() => true));
  let aufbewahrung = $state("Unbegrenzt");
</script>

<section class="inhalt">
  <div class="seite">
    <h1>Aufzeichnungs-Manager</h1>
    <p class="unter-gross">
      Die große PostgreSQL zeichnet ausgewählte Stationen und Orte langfristig auf. Lege pro Station/Ort
      und Variable fest, was dauerhaft archiviert wird.
    </p>

    <div class="panel">
      <h2><i class="fa-solid fa-database"></i> Aufgezeichnete Stationen und Orte</h2>
      <p class="unter">Vier Quellen laufen dauerhaft in das Archiv. Der Schalter je Zeile beendet oder startet die Aufzeichnung.</p>

      <div class="tabzeile tabkopf">
        <span></span><span>Station / Ort</span><span>Variablen</span><span>Zeitraum</span><span>Aktiv</span>
      </div>
      {#each stationen as s, i}
        <div class="tabzeile">
          <i class="fa-solid {s.icon}" style="color: var(--akzent)"></i>
          <span class="tz-name">{s.name} <small>{s.kennung}</small></span>
          <span class="reihe" style="flex-wrap: wrap; gap: var(--a1)">
            {#each s.variablen as v}<span class="chip">{v}</span>{/each}
          </span>
          <span class="tz-meta">{s.zeitraum}</span>
          <button class="schalter" class:an={aktiv[i]} onclick={() => (aktiv[i] = !aktiv[i])} aria-label="Aufzeichnung {s.name}"></button>
        </div>
      {/each}
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-hard-drive"></i> Speicher und Aufbewahrung</h2>
      <p class="unter">Wie lange und wie sparsam die Zeitreihen abgelegt werden.</p>

      <div class="formzeile-quer">
        <span class="fz-lab">Aufbewahrung <small>Ältere Werte werden nach Ablauf entfernt.</small></span>
        <span class="segment">
          {#each ["Unbegrenzt", "10 Jahre", "5 Jahre"] as opt}
            <button class:aktiv={aufbewahrung === opt} onclick={() => (aufbewahrung = opt)}>{opt}</button>
          {/each}
        </span>
      </div>

      <div class="formzeile" style="margin-top: var(--a3)">
        <label>Archiv 3,8 GB von 200 GB (externe SSD)</label>
        <div style="height: 6px; border-radius: 3px; background: var(--flaeche-3)">
          <span style="display: block; height: 100%; width: 12%; background: var(--akzent); border-radius: 3px"></span>
        </div>
      </div>

      <div class="klein-txt dimm" style="margin-top: var(--a2)">
        <i class="fa-solid fa-compress"></i> Kompression aktiv (TimescaleDB) - ältere Daten werden verdichtet.
      </div>
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-plus"></i> Station oder Ort aufnehmen</h2>
      <p class="unter">Suche im DWD-Stationsnetz oder gib einen eigenen Punkt ein und nimm ihn in die Aufzeichnung auf.</p>
      <div class="reihe" style="gap: var(--a2)">
        <div class="feld-such" style="flex: 1">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" placeholder="Station oder Ort suchen (DWD-Stationsnetz) ..." />
        </div>
        <button class="knopf primaer"><i class="fa-solid fa-plus"></i> Aufnehmen</button>
      </div>
    </div>
  </div>
</section>
