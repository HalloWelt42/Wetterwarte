<script lang="ts">
  import { ui } from "./ui.svelte";

  const werte = ["Feuchte", "Wind", "Luftdruck", "Sicht", "Taupunkt", "Bewölkung", "UV-Index", "Sonnenzeiten"];
  let zustand = $state([true, true, true, true, true, true, false, false]);
  let intervall = $state("10 Min");
  let groesse = $state("Mittel");
  let iconStil = $state("Meteocons");

  function zu() {
    ui.einstellungen = null;
  }
</script>

<div class="modal-hg" role="presentation" onclick={zu}>
  <div class="modal" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="modal-kopf">
      <h2><i class="fa-solid fa-sliders"></i> Kachel-Einstellungen - {ui.einstellungen}</h2>
      <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-inhalt">
      <div class="formzeile">
        <label>Ort</label>
        <div class="feld" style="display: flex; align-items: center; justify-content: space-between">
          Köln, Sachsen-Anhalt <i class="fa-solid fa-chevron-down dimm"></i>
        </div>
      </div>
      <div class="formzeile">
        <label>Titel der Kachel</label>
        <input class="feld" type="text" value="Aktuell" />
      </div>

      <div>
        <div class="kat-gruppe">Angezeigte Werte</div>
        {#each werte as w, i}
          <div class="formzeile-quer">
            <span class="fz-lab">{w}</span>
            <button class="schalter" class:an={zustand[i]} onclick={() => (zustand[i] = !zustand[i])} aria-label={w}></button>
          </div>
        {/each}
      </div>

      <div class="formzeile-quer">
        <span class="fz-lab">Aktualisierung</span>
        <span class="segment">
          {#each ["5 Min", "10 Min", "30 Min"] as o}
            <button class:aktiv={intervall === o} onclick={() => (intervall = o)}>{o}</button>
          {/each}
        </span>
      </div>
      <div class="formzeile-quer">
        <span class="fz-lab">Größe</span>
        <span class="segment">
          {#each ["Klein", "Mittel", "Groß"] as o}
            <button class:aktiv={groesse === o} onclick={() => (groesse = o)}>{o}</button>
          {/each}
        </span>
      </div>
      <div class="formzeile-quer">
        <span class="fz-lab">Icon-Stil</span>
        <span class="segment">
          {#each ["Meteocons", "Font Awesome"] as o}
            <button class:aktiv={iconStil === o} onclick={() => (iconStil = o)}>{o}</button>
          {/each}
        </span>
      </div>
    </div>
    <div class="modal-fuss">
      <button class="knopf" onclick={zu}>Abbrechen</button>
      <button class="knopf primaer" onclick={zu}>Speichern</button>
    </div>
  </div>
</div>
