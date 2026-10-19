<script lang="ts">
  // Kachelhülle: holt die Datenbereiche, die der Typ laut Katalog braucht, und zeichnet die
  // Kachel erst, wenn sie da sind. Bis dahin ein Skelett, bei Ausfall ein ehrlicher Hinweis,
  // bei altem Stand eine Altersmarke. Erfundene Ersatzwerte gibt es nie.
  import { registry } from "./registry";
  import { nutzeOrtDaten } from "../ortdaten.svelte";
  import { uhr } from "../../kern/uhr.svelte";

  let { typ, id, conf = {}, ort }: { typ: string; id: string; conf?: Record<string, any>; ort: string } = $props();

  // Typ und damit Komponente und Bereiche sind für eine Kachel fest.
  // svelte-ignore state_referenced_locally
  const def = registry[typ];
  const daten = nutzeOrtDaten(() => ort, def?.bereiche ?? []);

  const zustaende = $derived((def?.bereiche ?? []).map((b) => daten.zustand(b)));
  const laedt = $derived(zustaende.includes("laedt"));
  const fehlt = $derived(zustaende.includes("fehlt"));
  const altSeit = $derived.by(() => {
    const alt = (def?.bereiche ?? []).filter((b) => daten.zustand(b) === "alt").map((b) => daten.stand(b));
    const stand = alt.filter((s): s is string => !!s).sort()[0];
    if (!alt.length) return "";
    if (!stand) return "alt";
    const min = Math.max(0, Math.round((uhr.jetzt.getTime() - new Date(stand).getTime()) / 60000));
    return min < 60 ? `vor ${min} Min` : `vor ${Math.round(min / 60)} h`;
  });
</script>

{#if !def}
  <div class="kw-leer"><i class="fa-solid fa-circle-question"></i><div>Unbekannter Kacheltyp</div></div>
{:else if laedt}
  <div class="kw-laden" aria-busy="true" aria-label="Lädt">
    <span class="sk" style="width: 55%"></span>
    <span class="sk" style="width: 80%"></span>
    <span class="sk" style="width: 40%"></span>
  </div>
{:else if fehlt}
  <div class="kw-leer kw-fehlt"><i class="fa-solid fa-plug-circle-xmark"></i><div>{def.fehltHinweis ?? "Daten gerade nicht erreichbar, neuer Versuch folgt von selbst."}</div></div>
{:else}
  {#if altSeit}<span class="kw-alt" title="Die Quelle antwortet gerade nicht, gezeigt wird der letzte Stand.">Stand {altSeit}</span>{/if}
  <def.komponente {id} {conf} {ort} {daten} />
{/if}
