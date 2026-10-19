<script lang="ts">
  // Stand eines Datenbereichs am Ende eines Blatts, in Ortszeit; bei altem Stand mit Hinweis.
  import type { Bereich } from "../../typen";
  import { uhr } from "../../../kern/uhr.svelte";
  import { uhrzeit } from "../../../kern/zeit";
  import { kalendertag, tagNah, vorLang } from "../datum";

  let { bereich, zone, quelle = "" }: { bereich: Bereich; zone: string; quelle?: string } = $props();

  const text = $derived.by(() => {
    if (!bereich.stand) return "";
    const tag = tagNah(kalendertag(bereich.stand, zone), kalendertag(uhr.jetzt, zone));
    const wann = `${tag === "heute" ? "" : `${tag} `}${uhrzeit(bereich.stand, zone)} Uhr`;
    return `Stand ${wann}, ${vorLang(bereich.stand, uhr.jetzt)}${bereich.status === "alt" ? " (älterer Stand)" : ""}`;
  });
</script>

{#if text || quelle}
  <p class="stand-zeile">{[quelle, text].filter(Boolean).join(" · ")}</p>
{/if}
