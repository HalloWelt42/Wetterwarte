<script lang="ts">
  import { ui } from "./ui.svelte";

  interface Layout {
    name: string;
    info: string;
    standard?: boolean;
    warn?: boolean;
  }
  const layouts: Layout[] = [
    { name: "Zuhause", info: "14 Kacheln - 5 Orte", standard: true },
    { name: "Garten", info: "8 Kacheln - Regen, Frost, Pollen" },
    { name: "Reise", info: "4 Städte nebeneinander" },
    { name: "Unwetter", info: "Warnungen, Radar, Blitze, Nowcast", warn: true },
  ];

  // Mini-Vorschau: acht Bloecke, betonte Kacheln in Akzent bzw. Warnfarbe.
  function bloecke(l: Layout): string[] {
    const betont = l.warn ? "var(--gefahr-weich)" : "var(--akzent-weich)";
    return [betont, "var(--flaeche-3)", "var(--flaeche-3)", betont, "var(--flaeche-3)", betont, "var(--flaeche-3)", "var(--flaeche-3)"];
  }

  function zu() {
    ui.layouts = false;
  }
</script>

<div class="modal-hg" role="presentation" onclick={zu}>
  <div class="modal breit" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="modal-kopf">
      <h2><i class="fa-solid fa-object-group"></i> Layouts verwalten</h2>
      <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-inhalt">
      <p class="dimm klein-txt" style="margin: 0">
        Ein Layout ist eine benannte Kachel-Anordnung. Du wechselst oben in der Kopfleiste zwischen den Layouts.
      </p>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--a3)">
        {#each layouts as l}
          <div style="border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3); background: var(--flaeche)">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 20px; gap: 3px; margin-bottom: var(--a2)">
              {#each bloecke(l) as farbe}
                <span style="background: {farbe}; border-radius: 3px"></span>
              {/each}
            </div>
            <div class="reihe" style="justify-content: space-between">
              <b>{l.name}</b>
              {#if l.standard}<span class="pille gut">Standard</span>{/if}
            </div>
            <div class="klein-txt dimm">{l.info}</div>
            <div class="reihe" style="gap: 2px; margin-top: var(--a2)">
              <button class="icon-knopf" title="Umbenennen" style="width: 30px; height: 30px"><i class="fa-solid fa-pen"></i></button>
              <button class="icon-knopf" title="Duplizieren" style="width: 30px; height: 30px"><i class="fa-solid fa-copy"></i></button>
              <button class="icon-knopf gefahr" title="Löschen" style="width: 30px; height: 30px"><i class="fa-solid fa-trash"></i></button>
            </div>
          </div>
        {/each}
        <button
          style="border: 2px dashed var(--rand-stark); border-radius: var(--r2); background: transparent; display: grid; place-items: center; color: var(--text-3); min-height: 160px; cursor: pointer; font: inherit"
        >
          <span style="text-align: center"><i class="fa-solid fa-plus" style="font-size: 1.4rem"></i><br />Neues Layout</span>
        </button>
      </div>
    </div>
    <div class="modal-fuss">
      <button class="knopf primaer" onclick={zu}>Fertig</button>
    </div>
  </div>
</div>
