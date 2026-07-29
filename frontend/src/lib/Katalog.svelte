<script lang="ts">
  import { ui } from "./ui.svelte";

  interface Eintrag {
    icon: string;
    name: string;
    beschreibung: string;
  }
  const gruppen: { name: string; eintraege: Eintrag[] }[] = [
    {
      name: "Wetter",
      eintraege: [
        { icon: "fa-temperature-half", name: "Aktuell", beschreibung: "Zustand, Temperatur und Kennwerte" },
        { icon: "fa-clock", name: "Stundenvorhersage", beschreibung: "Nächste 48 Stunden" },
        { icon: "fa-calendar-days", name: "Tagesvorhersage", beschreibung: "7 bis 16 Tage" },
        { icon: "fa-square", name: "Mini-Kachel", beschreibung: "Nur Ort, Icon und Temperatur" },
        { icon: "fa-table-columns", name: "Orte-Vergleich", beschreibung: "Mehrere Standorte nebeneinander" },
        { icon: "fa-align-left", name: "Wetterbericht in Worten", beschreibung: "Ausformulierte Tageslage" },
      ],
    },
    {
      name: "Karte",
      eintraege: [
        { icon: "fa-map-location-dot", name: "Karte", beschreibung: "Basiskarte mit Ebenen" },
        { icon: "fa-satellite-dish", name: "Radar-Animation", beschreibung: "Niederschlag im Zeitraffer" },
        { icon: "fa-bolt", name: "Blitze", beschreibung: "Live-Entladungen im Umkreis" },
        { icon: "fa-cloud-showers-heavy", name: "Regen-Nowcast", beschreibung: "Regen in den nächsten Minuten" },
        { icon: "fa-wind", name: "Wind-Overlay", beschreibung: "Windfeld auf der Karte" },
      ],
    },
    {
      name: "Umwelt",
      eintraege: [
        { icon: "fa-triangle-exclamation", name: "Warnungen", beschreibung: "Amtliche Unwetterwarnungen" },
        { icon: "fa-smog", name: "Luftqualität", beschreibung: "AQI und Schadstoffe" },
        { icon: "fa-seedling", name: "Pollenflug", beschreibung: "Belastung je Pollenart" },
        { icon: "fa-sun", name: "UV-Index", beschreibung: "Sonnenbrandgefahr" },
        { icon: "fa-moon", name: "Sonne und Mond", beschreibung: "Auf- und Untergang, Mondphase" },
        { icon: "fa-heart-pulse", name: "Komfort", beschreibung: "Gefühlt, Taupunkt, Schwüle" },
      ],
    },
    {
      name: "Detail",
      eintraege: [
        { icon: "fa-wind", name: "Wind", beschreibung: "Böen, Richtung, Windrose" },
        { icon: "fa-snowflake", name: "Niederschlag und Schnee", beschreibung: "Menge und Schneehöhe" },
        { icon: "fa-gauge", name: "Barometer", beschreibung: "Luftdruck und Tendenz" },
        { icon: "fa-eye", name: "Sicht und Nebel", beschreibung: "Sichtweite, Wolkenuntergrenze" },
      ],
    },
    {
      name: "Archiv",
      eintraege: [
        { icon: "fa-chart-line", name: "Historie-Graph", beschreibung: "Verlauf aus dem Archiv" },
        { icon: "fa-award", name: "Rekorde", beschreibung: "Klima-Abweichung und Rekorde" },
        { icon: "fa-calendar", name: "Jahres-Heatmap", beschreibung: "Temperatur je Tag" },
      ],
    },
    {
      name: "Rahmen",
      eintraege: [
        { icon: "fa-clock", name: "Uhr und Standort", beschreibung: "Zeit, Ort, Kurzlage" },
        { icon: "fa-bell", name: "Schwellenwert-Alarm", beschreibung: "Benachrichtigung bei Grenzwert" },
        { icon: "fa-circle-info", name: "Datenquellen und Status", beschreibung: "Frische und Herkunft" },
      ],
    },
  ];

  function zu() {
    ui.katalog = false;
  }
</script>

<div class="ueberlagerung" role="presentation" onclick={zu}></div>
<aside class="seiten-panel">
  <div class="detail-kopf">
    <h2><i class="fa-solid fa-shapes"></i> Kachel hinzufügen</h2>
    <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
  </div>
  <div class="detail-block">
    <div class="feld-such">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" placeholder="Kacheltyp suchen ..." />
    </div>
  </div>
  <div style="flex: 1; overflow-y: auto; padding: 0 var(--a4) var(--a4)">
    {#each gruppen as g}
      <div class="kat-gruppe">{g.name}</div>
      {#each g.eintraege as e}
        <div class="kat-item">
          <i class="fa-solid {e.icon}"></i>
          <span class="kat-txt">{e.name}<small>{e.beschreibung}</small></span>
          <i class="fa-solid fa-grip-vertical griff"></i>
        </div>
      {/each}
    {/each}
  </div>
</aside>
