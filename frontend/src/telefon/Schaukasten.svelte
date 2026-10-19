<script lang="ts">
  // Alle Telefon-Kacheltypen in allen erlaubten Größen mit den echten Daten des Orts, nach Familien.
  // Dient als Übersicht unter "Mehr" und als Vorschau im Editor am Desktop.
  import { telefonKatalog, type TelefonTypDef } from "../kern/gemeinsam";
  import Kachel from "./Kachel.svelte";
  import type { OrtStand } from "./wetter.svelte";

  let { stand, nurTyp = "" }: { stand: OrtStand; nurTyp?: string } = $props();

  const familien = $derived(
    telefonKatalog.familien
      .map((f) => ({ ...f, typen: Object.entries(telefonKatalog.typen).filter(([t, d]) => d.familie === f.schluessel && (!nurTyp || t === nurTyp)) }))
      .filter((f) => f.typen.length),
  );
  const masse = (g: string) => g.split("x").map(Number) as [number, number];

  // Varianten der Einstellungen in der kleinsten Größe: jede Auswahl einzeln, bei Mehrfachauswahl
  // ein Beispiel mit den ersten beiden Werten.
  type Variante = { titel: string; conf: Record<string, unknown> };
  function varianten(d: TelefonTypDef): Variante[] {
    return d.einstellungen.flatMap((e): Variante[] =>
      e.art === "auswahl"
        ? e.optionen.filter((o) => o.wert !== e.standard).map((o) => ({ titel: o.titel, conf: { [e.schluessel]: o.wert } }))
        : [{ titel: `${e.titel}: ${e.optionen.slice(0, 2).map((o) => o.titel).join(", ")}`, conf: { [e.schluessel]: e.optionen.slice(0, 2).map((o) => o.wert) } }],
    );
  }
</script>

{#each familien as fam (fam.schluessel)}
  <section class="abschnitt">
    <h3>{fam.titel}</h3>
    {#each fam.typen as [typ, def] (typ)}
      <div class="sk-typ">
        <div class="sk-name"><i class="fa-solid {def.symbol}"></i> {def.titel} <small>{def.beschreibung}</small></div>
        <div class="sk-formen">
          {#each def.groessen as g (g)}
            {@const [w, h] = masse(g)}
            <figure>
              <div class="raster" style="grid-template-columns: repeat({w}, var(--feld)); grid-template-rows: repeat({h}, var(--feld)); padding: 0">
                <Kachel kachel={{ id: `${typ}-${g}`, typ, x: 0, y: 0, w, h, conf: {} }} {stand} />
              </div>
              <figcaption>{w}×{h}</figcaption>
            </figure>
          {/each}
          {#each varianten(def) as v (v.titel)}
            {@const [w, h] = masse(def.groessen[0])}
            <figure>
              <div class="raster" style="grid-template-columns: repeat({w}, var(--feld)); grid-template-rows: repeat({h}, var(--feld)); padding: 0">
                <Kachel kachel={{ id: `${typ}-${v.titel}`, typ, x: 0, y: 0, w, h, conf: v.conf }} {stand} />
              </div>
              <figcaption>{v.titel}</figcaption>
            </figure>
          {/each}
        </div>
      </div>
    {/each}
  </section>
{/each}

<style>
  .sk-typ {
    margin-bottom: 18px;
  }
  .sk-name {
    font-weight: 700;
    margin: 0 4px 8px;
  }
  .sk-name i {
    color: var(--text-3);
    width: 1.3em;
  }
  .sk-name small {
    display: block;
    font-weight: 500;
    font-size: var(--s15);
    color: var(--text-3);
  }
  .sk-formen {
    display: flex;
    flex-wrap: wrap;
    gap: 12px var(--fuge);
  }
  figure {
    margin: 0;
  }
  figcaption {
    font-size: var(--s13);
    color: var(--text-3);
    font-weight: 700;
    margin: 4px 0 0 4px;
  }
</style>
