<script lang="ts">
  // Onboarding-/Rettungsring-Overlay: begruesst Erstnutzer und zeigt die ersten
  // Schritte. Beim ersten Start automatisch, danach jederzeit ueber den
  // Rettungsring-Knopf im Kopf wieder aufrufbar.
  import { ui } from "./ui.svelte";

  const schritte = [
    { icon: "fa-location-dot", titel: "Orte hinzufügen", text: "Oben suchen oder über den Globus Demo-Orte (Extremwetter + bekannte Orte) übernehmen." },
    { icon: "fa-table-cells-large", titel: "Kacheln zusammenstellen", text: "Mit „Kachel“ Widgets aus dem Katalog holen, frei anordnen und in der Größe ziehen." },
    { icon: "fa-object-group", titel: "Layouts umschalten", text: "Benannte Anordnungen (Zuhause, Garten, Reise, Unwetter) oben in der Kopfleiste." },
    { icon: "fa-map-location-dot", titel: "Grosse Karte", text: "Radar, Warnungen, Temperatur, Wind und Blitze - links über „Grosse Karte“." },
  ];

  function los(): void {
    ui.willkommen = false;
  }
  function hilfe(): void {
    ui.willkommen = false;
    ui.hilfe = true;
  }
  function demo(): void {
    ui.willkommen = false;
    ui.demoOrte = true;
  }
</script>

<div class="modal-hg" role="presentation" onclick={los}>
  <div class="modal willkommen" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="wk-kopf">
      <div class="wk-ring"><i class="fa-solid fa-life-ring"></i></div>
      <h2>Willkommen bei der Wetterwarte</h2>
      <p class="dimm">Dein frei aufbaubares, selbst gehostetes Wetter-Dashboard. In wenigen Schritten startklar.</p>
    </div>
    <div class="wk-schritte">
      {#each schritte as s, i}
        <div class="wk-schritt">
          <div class="wk-nr">{i + 1}</div>
          <div class="wk-icon"><i class="fa-solid {s.icon}"></i></div>
          <div class="wk-text"><b>{s.titel}</b><span class="dimm klein-txt">{s.text}</span></div>
        </div>
      {/each}
    </div>
    <div class="wk-aktionen">
      <button class="knopf" onclick={demo}><i class="fa-solid fa-earth-americas"></i> Demo-Orte</button>
      <button class="knopf" onclick={hilfe}><i class="fa-solid fa-circle-question"></i> Hilfe öffnen</button>
      <button class="knopf primaer" onclick={los}>Los geht's</button>
    </div>
  </div>
</div>
