<script lang="ts">
  import { onMount, tick } from "svelte";
  import { GridStack } from "gridstack";
  import Kachel from "./Kachel.svelte";
  import { registry } from "./kacheln/registry";
  import { profilTypen } from "./profile";
  import { sende } from "./api";
  import { layoutState } from "./layout.svelte";
  import { kachelAktion, brettState } from "./kachelAktion.svelte";
  import { konf } from "./kachelConf.svelte";

  interface Instanz {
    id: string;
    typ: string;
    x?: number;
    y?: number;
    w: number;
    h: number;
    conf?: Record<string, unknown>;
  }

  let brettEl: HTMLElement;
  let grid: GridStack | undefined;
  let kacheln = $state<Instanz[]>([]);
  let aktivGeladen: string | null = null;
  let standGeladen = -1;
  let ladend = false;
  let entprellen: ReturnType<typeof setTimeout> | undefined;

  // Anzahl je Kacheltyp im aktuellen Layout fuer den Katalog spiegeln.
  $effect(() => {
    const zaehler: Record<string, number> = {};
    for (const k of kacheln) zaehler[k.typ] = (zaehler[k.typ] ?? 0) + 1;
    brettState.anzahlJeTyp = zaehler;
  });

  // Leeres Layout uebernimmt die zu seinem Namen passende Profil-Anordnung.
  function profilInstanzen(name: string): Instanz[] {
    return profilTypen(name).map((typ, i) => ({ id: `${typ}-${i}`, typ, w: registry[typ].w, h: registry[typ].h, conf: {} }));
  }

  function initGrid(): void {
    if (!brettEl) return;
    if (grid) {
      grid.offAll();
      grid.destroy(false);
    }
    grid = GridStack.init(
      {
        column: 12,
        cellHeight: 74,
        margin: 6,
        float: false,
        handle: ".kw-kopf",
        resizable: { handles: "se" },
        columnOpts: { breakpointForWindow: true, breakpoints: [{ w: 768, c: 1 }] },
      },
      brettEl,
    );
    grid.on("change", () => {
      if (!ladend) speichere();
    });
  }

  function speichere(): void {
    const id = layoutState.aktivId;
    if (!grid || !id) return;
    const pos = grid.save(false) as { id: string; x: number; y: number; w: number; h: number }[];
    const daten = pos.map((p) => {
      const k = kacheln.find((x) => x.id === p.id);
      return { ...p, typ: k?.typ, conf: k?.conf ?? {} };
    });
    clearTimeout(entprellen);
    entprellen = setTimeout(() => {
      void sende(`/layouts/${id}`, "PUT", { daten });
      const l = layoutState.liste.find((x) => x.id === id);
      if (l) l.daten = daten as never;
    }, 600);
  }

  // Aktuelle gridstack-Positionen in die Instanzen zurueckschreiben (vor Umbau).
  function synchronisiere(): void {
    if (!grid) return;
    const pos = grid.save(false) as { id: string; x: number; y: number; w: number; h: number }[];
    for (const p of pos) {
      const k = kacheln.find((x) => x.id === p.id);
      if (k) {
        k.x = p.x;
        k.y = p.y;
        k.w = p.w;
        k.h = p.h;
      }
    }
  }

  async function ladeLayout(id: string): Promise<void> {
    const l = layoutState.liste.find((x) => x.id === id);
    const hatDaten = l && Array.isArray(l.daten) && l.daten.length > 0 && (l.daten[0] as { typ?: string }).typ;
    const neu = hatDaten
      ? (l!.daten as unknown as Instanz[]).map((d) => ({
          id: d.id,
          // Migration: aus der fruehen kombinierten Kachel wird die reine Sonnen-Kachel.
          typ: d.typ === "sonnemond" ? "sonne" : d.typ,
          x: d.x,
          y: d.y,
          w: d.w,
          h: d.h,
          conf: (d as { conf?: Record<string, unknown> }).conf ?? {},
        }))
      : profilInstanzen(l?.name ?? "");
    ladend = true;
    kacheln = neu;
    await tick();
    initGrid();
    ladend = false;
    if (!hatDaten) speichere();
  }

  async function umbauen(mutation: () => void): Promise<void> {
    synchronisiere();
    mutation();
    await tick();
    ladend = true;
    initGrid();
    ladend = false;
    speichere();
  }

  function entferne(id: string): void {
    void umbauen(() => {
      kacheln = kacheln.filter((k) => k.id !== id);
    });
  }

  function hinzufuegen(typ: string): void {
    const def = registry[typ];
    if (!def) return;
    void umbauen(() => {
      kacheln = [...kacheln, { id: `${typ}-${crypto.randomUUID()}`, typ, w: def.w, h: def.h, conf: {} }];
    });
  }

  onMount(() => {
    return () => grid?.destroy(false);
  });

  // Aktives Layout laden/wechseln (auch bei erzwungenem Neuladen via stand-Nonce).
  $effect(() => {
    const id = layoutState.aktivId;
    const stand = layoutState.stand;
    if (!id) return;
    if (id === aktivGeladen && stand === standGeladen) return;
    aktivGeladen = id;
    standGeladen = stand;
    void ladeLayout(id);
  });

  // Kachel aus dem Katalog aufnehmen.
  $effect(() => {
    const typ = kachelAktion.add;
    if (!typ) return;
    kachelAktion.add = null;
    hinzufuegen(typ);
  });

  // Geaenderte Einstellungen einer Kachel uebernehmen (ohne Grid-Neuaufbau).
  let konfAngewandt = 0;
  $effect(() => {
    const v = konf.version;
    if (v === 0 || v === konfAngewandt || konf.id === null) return;
    konfAngewandt = v;
    const k = kacheln.find((x) => x.id === konf.id);
    if (k) {
      k.conf = { ...konf.werte };
      speichere();
    }
  });
</script>

<div class="brett-wrap">
  <div class="grid-stack" bind:this={brettEl}>
    {#each kacheln as k (k.id)}
      <div class="grid-stack-item" gs-id={k.id} gs-w={k.w} gs-h={k.h} gs-x={k.x} gs-y={k.y}>
        <div class="grid-stack-item-content">
          <Kachel typ={k.typ} id={k.id} conf={k.conf ?? {}} onEntfernen={() => entferne(k.id)} />
        </div>
      </div>
    {/each}
  </div>
</div>
