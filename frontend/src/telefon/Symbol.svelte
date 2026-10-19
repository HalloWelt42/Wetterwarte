<script lang="ts">
  // Wettersymbol: farbig (Meteocons), im Nachtbetrieb als einfarbige Maske in Textfarbe (rot).
  import { meteocon, meteoconMaske } from "../kern/icons";
  import { bildName } from "../kern/wetterbild";
  import { getContext } from "svelte";
  import { nachtAktiv } from "./ansicht.svelte";

  let {
    code = undefined,
    tag = true,
    name = undefined,
    klasse = "",
    stil = "",
  }: { code?: number; tag?: boolean; name?: string; klasse?: string; stil?: string } = $props();

  const bild = $derived(name ?? bildName(code ?? 3, tag));
  // Der Editor am Desktop schaltet Tag und Nacht der Vorschau selbst (Kontext "telefon-nacht").
  const nacht = getContext<(() => boolean) | undefined>("telefon-nacht") ?? nachtAktiv;
</script>

{#if nacht()}
  <span class="mc mcm {klasse}" style="--i: url({meteoconMaske(bild)}); {stil}" aria-hidden="true"></span>
{:else}
  <img class="mc {klasse}" style={stil} src={meteocon(bild)} alt="" />
{/if}
