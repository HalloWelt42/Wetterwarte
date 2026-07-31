<script lang="ts">
  // System- & Dienste-Uebersicht: welche Dienste die Wetterwarte nutzt und ob sie
  // gerade erreichbar sind - gruppiert nach intern / lokal / extern.
  import { onMount } from "svelte";
  import { ui } from "./ui.svelte";
  import { hole } from "./api";
  import HilfeLink from "./HilfeLink.svelte";
  import Speicher from "./Speicher.svelte";

  interface Dienst {
    key: string;
    name: string;
    rolle: string;
    art: string;
    technik: string;
    status: string;
    latenz_ms: number | null;
    code: number | null;
  }

  let dienste = $state<Dienst[]>([]);
  let laedt = $state(true);
  let stand = $state("");

  async function lade(): Promise<void> {
    laedt = true;
    try {
      const d = await hole<{ dienste: Dienst[] }>("/dienste");
      dienste = d.dienste;
      stand = new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
      dienste = [];
    }
    laedt = false;
  }
  onMount(lade);

  const gruppen = [
    { art: "intern", titel: "Intern (dieser Stack)", info: "Laeuft im selben Docker-Verbund." },
    { art: "lokal", titel: "Lokal auf dem Pi", info: "Eigene Dienste - kein externer Abruf zur Laufzeit." },
    { art: "extern", titel: "Externe Rohdaten", info: "Einzige Aussenanbindung: die Wetter-Rohdaten." },
  ];
  function fuerArt(art: string): Dienst[] {
    return dienste.filter((d) => d.art === art);
  }
  const statusText: Record<string, string> = { ok: "erreichbar", gestoert: "gestoert", offline: "nicht erreichbar" };

  const erreichbar = $derived(dienste.filter((d) => d.status === "ok").length);

  function zu(): void {
    ui.dienste = false;
  }
</script>

<div class="modal-hg" role="presentation" onclick={zu}>
  <div class="modal breit" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="modal-kopf">
      <h2><i class="fa-solid fa-diagram-project"></i> System &amp; Dienste <HilfeLink topic="dienste" /></h2>
      <span style="flex: 1"></span>
      <button class="icon-knopf" title="Neu prüfen" aria-label="Neu prüfen" onclick={lade}><i class="fa-solid fa-rotate" class:fa-spin={laedt}></i></button>
      <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-inhalt">
      <p class="dimm klein-txt" style="margin: 0">
        Welche Dienste die Wetterwarte nutzt und ob sie gerade erreichbar sind.
        {#if dienste.length}<b>{erreichbar}/{dienste.length}</b> erreichbar{#if stand} &middot; Stand {stand}{/if}.{/if}
      </p>

      {#each gruppen as g}
        {#if fuerArt(g.art).length}
          <div class="kat-gruppe" style="margin-top: var(--a4)">{g.titel}</div>
          <div class="klein-txt dimm" style="margin-bottom: var(--a2)">{g.info}</div>
          <div class="dienst-liste">
            {#each fuerArt(g.art) as d}
              <div class="dienst-zeile">
                <span class="dienst-punkt status-{d.status}" title={statusText[d.status] ?? d.status}></span>
                <div class="dienst-haupt">
                  <div><b>{d.name}</b> <span class="dimm klein-txt">&middot; {d.technik}</span></div>
                  <div class="klein-txt dimm">{d.rolle}</div>
                </div>
                <div class="dienst-status">
                  <span class="status-label status-{d.status}">{statusText[d.status] ?? d.status}</span>
                  {#if d.latenz_ms != null}<span class="klein-txt dimm tnum">{d.latenz_ms} ms</span>{/if}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      {/each}

      {#if !laedt && dienste.length === 0}
        <div class="kw-leer"><i class="fa-solid fa-plug-circle-xmark"></i><div>Status nicht abrufbar</div></div>
      {/if}

      <div class="kat-gruppe" style="margin-top: var(--a4)">Speicher &amp; Offline</div>
      <Speicher />
    </div>
    <div class="modal-fuss">
      <button class="knopf primaer" onclick={zu}>Fertig</button>
    </div>
  </div>
</div>
