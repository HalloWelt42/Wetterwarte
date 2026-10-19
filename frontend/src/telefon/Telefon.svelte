<script lang="ts">
  // Wurzel der Telefonansicht (docs/TELEFON.md): Seiten Karte, Wetter, Gesundheit und Mehr,
  // darüber Blätter. Schriftstufe und Nachtbetrieb setzen data-Attribute an .tel, alle Farben
  // und Größen folgen daraus über die Variablen in telefon.css.
  import { onMount } from "svelte";
  import { einstellung, telefonKatalog } from "../kern/gemeinsam";
  import { orteState } from "../kern/orte.svelte";
  import { fassungVerfolgen, vielleichtNeuLaden } from "../kern/fassung.svelte";
  import { ansicht, adresseSpiegeln, nachtAktiv, profilAusAdresse, schliesse, waehleOrt } from "./ansicht.svelte";
  import { geraet } from "./geraet.svelte";
  import { ladeProfile, profile } from "./profil.svelte";
  import { gueltigerOrt, ladeOrteTelefon } from "./orte.svelte";
  import { ladeWennAlt, standVon, verfolge } from "./wetter.svelte";
  import { telefonTypen } from "./katalog";
  import Seite from "./Seite.svelte";
  import Reiterleiste from "./Reiterleiste.svelte";
  import Blatt from "./Blatt.svelte";
  import Karte from "./ansichten/Karte.svelte";
  import Orte from "./ansichten/Orte.svelte";
  import Mehr from "./ansichten/Mehr.svelte";
  import WarnungenBlatt from "./blaetter/Warnungen.svelte";
  import Schaukasten from "./Schaukasten.svelte";

  onMount(() => {
    void (async () => {
      await Promise.all([ladeOrteTelefon(), ladeProfile(profilAusAdresse)]);
      waehleOrt(gueltigerOrt(ansicht.ort));
    })();
    const stopWetter = verfolge(() => ansicht.ort);
    const stopFassung = fassungVerfolgen();
    return () => {
      stopWetter();
      stopFassung();
    };
  });

  // Ortswechsel: Daten holen, falls nicht frisch; Adresse nachführen; neue Fassung nachladen.
  $effect(() => {
    if (ansicht.ort) ladeWennAlt(ansicht.ort);
  });
  $effect(() => {
    void ansicht.reiter;
    void ansicht.ort;
    void profile.aktivId;
    adresseSpiegeln();
    vielleichtNeuLaden("ortswechsel");
  });

  const stand = $derived(standVon(ansicht.ort));
  const ortName = $derived(orteState.liste.find((o) => o.slug === ansicht.ort)?.name ?? "");
  const blatt = $derived(ansicht.blatt);
  const detailTyp = $derived(blatt?.art === "detail" ? telefonTypen[blatt.kachel.typ] : null);
  // Titel des Blatts aus dem Katalog; beim Messwert der gewählte Wert ("Luftdruck" statt "Messwert").
  const detailTitel = $derived.by(() => {
    if (blatt?.art !== "detail") return "";
    const def = telefonKatalog.typen[blatt.kachel.typ];
    const wahl = def?.einstellungen.find((e) => e.schluessel === "groesse");
    if (wahl) {
      const wert = einstellung<string>(blatt.kachel.typ, blatt.kachel.conf, "groesse");
      return wahl.optionen.find((o) => o.wert === wert)?.titel ?? def.titel;
    }
    return def?.titel ?? "";
  });
</script>

<div class="tel" data-stufe={geraet.stufe === "normal" ? undefined : geraet.stufe} data-modus={nachtAktiv() ? "nacht" : undefined}>
  <div class="schale">
    {#if ansicht.reiter === "karte"}
      <Karte />
    {:else if ansicht.reiter === "mehr"}
      <Mehr />
    {:else}
      {#key ansicht.reiter}<Seite seite={ansicht.reiter} />{/key}
    {/if}
    <Reiterleiste />
  </div>

  {#if blatt?.art === "schaukasten"}
    <Blatt titel="Alle Kachelformen" unter={ortName} schliessen={schliesse} voll><Schaukasten {stand} /></Blatt>
  {:else if blatt?.art === "orte"}
    <Blatt titel="Orte" schliessen={schliesse} voll><Orte /></Blatt>
  {:else if blatt?.art === "warnungen" && stand.daten}
    <Blatt titel="Warnungen" unter={ortName} schliessen={schliesse}>
      <WarnungenBlatt kachel={{ id: "warnband", typ: "warnungen", x: 0, y: 0, w: 3, h: 2, conf: {} }} daten={stand.daten} zone={stand.daten.ort.zeitzone} />
    </Blatt>
  {:else if blatt?.art === "detail" && detailTyp?.detail && stand.daten}
    <Blatt titel={detailTitel} unter={ortName} schliessen={schliesse}>
      <detailTyp.detail kachel={blatt.kachel} daten={stand.daten} zone={stand.daten.ort.zeitzone} />
    </Blatt>
  {/if}
</div>
