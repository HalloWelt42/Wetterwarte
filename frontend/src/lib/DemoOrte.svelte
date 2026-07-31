<script lang="ts">
  // Demo-Orte: kuratierte Orte mit Extremwetter + bekannte Orte weltweit, zum
  // Ausprobieren und Vorfuehren. Ein Klick fuegt sie der Ortsliste hinzu.
  import { onMount } from "svelte";
  import { hole } from "./api";
  import { ui } from "./ui.svelte";
  import { orteState, fuegeOrtHinzu } from "./orte.svelte";

  interface DemoOrt {
    name: string;
    region: string;
    land: string;
    lat: number;
    lon: number;
    zeitzone: string;
    kategorie: string;
    notiz: string;
  }

  let orte = $state<DemoOrt[]>([]);
  let laedt = $state<Record<string, boolean>>({});

  onMount(async () => {
    try {
      orte = await hole<DemoOrt[]>("/orte/demo");
    } catch {
      /* still */
    }
  });

  const gruppen = $derived([
    { titel: "Extremwetter", orte: orte.filter((o) => o.kategorie === "extremwetter") },
    { titel: "Bekannte Orte", orte: orte.filter((o) => o.kategorie === "bekannt") },
  ]);

  function vorhanden(o: DemoOrt): boolean {
    return orteState.liste.some((x) => x.name === o.name || (Math.abs(x.lat - o.lat) < 0.05 && Math.abs(x.lon - o.lon) < 0.05));
  }

  async function hinzu(o: DemoOrt): Promise<void> {
    if (vorhanden(o) || laedt[o.name]) return;
    laedt[o.name] = true;
    await fuegeOrtHinzu({ name: o.name, region: o.region, land: o.land, lat: o.lat, lon: o.lon, zeitzone: o.zeitzone });
    laedt[o.name] = false;
  }

  async function alle(liste: DemoOrt[]): Promise<void> {
    for (const o of liste) if (!vorhanden(o)) await hinzu(o);
  }

  function zu(): void {
    ui.demoOrte = false;
  }
</script>

<div class="modal-hg" role="presentation" onclick={zu}>
  <div class="modal breit" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="modal-kopf">
      <h2><i class="fa-solid fa-earth-americas"></i> Demo-Orte</h2>
      <span style="flex: 1"></span>
      <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-inhalt">
      <p class="dimm klein-txt" style="margin: 0">
        Zum Ausprobieren und Vorführen: Orte mit Extremwetter und bekannte Orte weltweit. Ein Klick fügt sie deiner
        Ortsliste hinzu - Uhr, Sonne und Mond stimmen dank hinterlegter Zeitzone sofort.
      </p>

      {#each gruppen as g}
        <div class="reihe" style="justify-content: space-between; align-items: center; margin-top: var(--a4)">
          <div class="kat-gruppe" style="margin: 0">{g.titel}</div>
          <button class="chip chip-knopf" onclick={() => alle(g.orte)}>Alle hinzufügen</button>
        </div>
        <div class="demo-liste">
          {#each g.orte as o}
            <button class="demo-ort" class:demo-da={vorhanden(o)} onclick={() => hinzu(o)} disabled={vorhanden(o)}>
              <span class="demo-haupt">
                <span class="demo-name"><b>{o.name}</b> <small class="dimm">{o.land}</small></span>
                {#if o.notiz}<span class="demo-notiz klein-txt dimm">{o.notiz}</span>{/if}
              </span>
              <i class="fa-solid {vorhanden(o) ? 'fa-circle-check' : 'fa-circle-plus'}"></i>
            </button>
          {/each}
        </div>
      {/each}
    </div>
  </div>
</div>
