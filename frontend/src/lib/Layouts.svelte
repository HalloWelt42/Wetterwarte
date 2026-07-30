<script lang="ts">
  import { ui } from "./ui.svelte";
  import {
    layoutState,
    setzeAktiv,
    erstelleLayout,
    benenneLayout,
    dupliziereLayout,
    loescheLayout,
    setzeStandard,
    setzeAufProfil,
    type Layout,
  } from "./layout.svelte";

  let bearbeiteId = $state<string | null>(null);
  let bearbeiteName = $state("");
  let loeschId = $state<string | null>(null);

  function starteBearbeiten(l: Layout): void {
    bearbeiteId = l.id;
    bearbeiteName = l.name;
    loeschId = null;
  }
  async function speichereName(): Promise<void> {
    if (bearbeiteId) await benenneLayout(bearbeiteId, bearbeiteName);
    bearbeiteId = null;
  }
  function taste(e: KeyboardEvent): void {
    if (e.key === "Enter") void speichereName();
    else if (e.key === "Escape") bearbeiteId = null;
  }
  async function loeschen(id: string): Promise<void> {
    if (loeschId !== id) {
      loeschId = id; // erster Klick schaerft, zweiter loescht
      return;
    }
    loeschId = null;
    await loescheLayout(id);
  }
  async function neu(): Promise<void> {
    const l = await erstelleLayout();
    if (l) setzeAktiv(l.id);
  }
  function anzahl(l: Layout): number {
    return Array.isArray(l.daten) ? l.daten.length : 0;
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
        {#each layoutState.liste as l (l.id)}
          <div class="layout-karte" class:aktiv-rahmen={layoutState.aktivId === l.id}>
            <button class="layout-vorschau" onclick={() => setzeAktiv(l.id)} title="Dieses Layout anzeigen" aria-label="Layout {l.name} anzeigen">
              {#each l.daten as d}<span style="grid-column: {(d.x ?? 0) + 1} / span {d.w}; grid-row: {(d.y ?? 0) + 1} / span {d.h}"></span>{/each}
            </button>
            <div class="reihe" style="justify-content: space-between; gap: var(--a2)">
              {#if bearbeiteId === l.id}
                <!-- svelte-ignore a11y_autofocus -->
                <input
                  class="feld"
                  style="height: 28px; padding: 2px 6px"
                  bind:value={bearbeiteName}
                  onkeydown={taste}
                  onblur={speichereName}
                  autofocus
                />
              {:else}
                <b>{l.name}</b>
              {/if}
              {#if l.ist_standard}
                <span class="pille gut">Standard</span>
              {:else}
                <button class="pille pille-knopf" onclick={() => setzeStandard(l.id)} title="Als Standard setzen">Standard?</button>
              {/if}
            </div>
            <div class="klein-txt dimm">{anzahl(l)} Kacheln</div>
            <div class="reihe" style="gap: 2px; margin-top: var(--a2)">
              <button class="icon-knopf" title="Umbenennen" style="width: 30px; height: 30px" onclick={() => starteBearbeiten(l)} aria-label="Umbenennen"><i class="fa-solid fa-pen"></i></button>
              <button class="icon-knopf" title="Duplizieren" style="width: 30px; height: 30px" onclick={() => dupliziereLayout(l.id)} aria-label="Duplizieren"><i class="fa-solid fa-copy"></i></button>
              <button class="icon-knopf" title="Auf Profil-Standard zurücksetzen" style="width: 30px; height: 30px" onclick={() => setzeAufProfil(l.id)} aria-label="Auf Profil-Standard zurücksetzen"><i class="fa-solid fa-rotate-left"></i></button>
              <button
                class="icon-knopf gefahr"
                title={loeschId === l.id ? "Wirklich löschen?" : "Löschen"}
                style="height: 30px; {loeschId === l.id ? 'width: auto; padding: 0 8px' : 'width: 30px'}"
                onclick={() => loeschen(l.id)}
                aria-label="Löschen"
              >
                {#if loeschId === l.id}<span class="klein-txt">Sicher?</span>{:else}<i class="fa-solid fa-trash"></i>{/if}
              </button>
            </div>
          </div>
        {/each}
        <button class="layout-neu" onclick={neu}>
          <span style="text-align: center"><i class="fa-solid fa-plus" style="font-size: 1.4rem"></i><br />Neues Layout</span>
        </button>
      </div>
    </div>
    <div class="modal-fuss">
      <button class="knopf primaer" onclick={zu}>Fertig</button>
    </div>
  </div>
</div>
