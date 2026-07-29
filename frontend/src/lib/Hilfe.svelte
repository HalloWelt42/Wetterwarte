<script lang="ts">
  import { ui } from "./ui.svelte";
</script>

<div class="hilfe-fenster">
  <div class="hilfe-kopf">
    <i class="fa-solid fa-circle-question" style="color: var(--akzent)"></i>
    <h3>Hilfe und Wissen</h3>
    <button class="icon-knopf" onclick={() => (ui.hilfe = false)} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
  </div>
  <div class="hilfe-inhalt">
    <div class="feld-such" style="margin-bottom: var(--a3)">
      <i class="fa-solid fa-magnifying-glass"></i>
      <input type="text" placeholder="In der Hilfe suchen ..." />
    </div>

    <h4>Erste Schritte</h4>
    <p>Kacheln ziehst du aus dem Katalog auf das Brett und ordnest sie frei an. An der Ecke ziehst du eine Kachel größer oder kleiner.</p>
    <div class="spalte" style="gap: var(--a1); margin-bottom: var(--a3)">
      <span class="tiefenlink" role="button" tabindex="0" onclick={() => { ui.hilfe = false; ui.katalog = true; }}><i class="fa-solid fa-arrow-right"></i> Kachel hinzufügen</span>
      <span class="tiefenlink" role="button" tabindex="0" onclick={() => { ui.hilfe = false; ui.layouts = true; }}><i class="fa-solid fa-arrow-right"></i> Layout speichern</span>
    </div>

    <h4>Kacheln und Größe</h4>
    <p>Alle Kacheln lassen sich frei anordnen und in der Größe ziehen. Das Raster rückt die übrigen Kacheln nach. Über das Zahnrad passt du Ort, Zeitraum und Darstellung je Kachel an.</p>

    <h4>Benannte Layouts</h4>
    <p>Lege mehrere Dashboards an und schalte oben in der Kopfleiste zwischen ihnen um: Zuhause, Garten, Reise und Unwetter sind schon vorbereitet.</p>
    <span class="tiefenlink" role="button" tabindex="0" onclick={() => { ui.hilfe = false; ui.layouts = true; }}><i class="fa-solid fa-arrow-right"></i> Layouts verwalten</span>

    <h4>Langzeit-Aufzeichnung</h4>
    <p>Wähle Stationen und Variablen, die dauerhaft in die große Datenbank geschrieben werden.</p>

    <h4>Datenquellen</h4>
    <p>Wetterdaten kommen vom Deutschen Wetterdienst (Deutschland) und Open-Meteo (weltweit), lokal aufbereitet. Karten stammen aus OpenStreetMap und werden lokal gehostet.</p>

    <p class="klein-txt dimm" style="margin-top: var(--a3)">Tipp: Die kleinen i-Symbole an jeder Kachel öffnen die passende Hilfe direkt.</p>
  </div>
</div>
