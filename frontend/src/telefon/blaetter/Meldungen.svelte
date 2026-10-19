<script lang="ts">
  // Blatt "Meldungen" (docs/WARNUNGEN.md): Mitteilungen aufs Telefon (Web Push) mit Orten, und Tonansagen bei
  // offener App; darunter, was gemeldet wird, ab welcher Stärke, wie früh, und die Nachtruhe. Die Einstellungen
  // gelten für dieses Gerät und liegen beim Server, weil der Melder auch bei geschlossener App danach handelt.
  import { onMount } from "svelte";
  import { meldekatalog, type Meldeart } from "../../kern/gemeinsam";
  import { orteState } from "../../kern/orte.svelte";
  import { ansicht } from "../ansicht.svelte";
  import { ansagen, ansagenSchalten, probeansage } from "../ansagen/ansagen.svelte";
  import { einstellen, konto, ladeKonto, probe, sicheresKonto, type Meldeeinstellungen } from "../meldungen/konto.svelte";
  import { ausschalten, einschalten, pushLage, serverSchluessel } from "../meldungen/push";

  const VORGABE: Meldeeinstellungen = { orte: [], ...meldekatalog.optionen.vorgabe };

  let lage = $state(pushLage());
  let beschaeftigt = $state(false);
  let meldung = $state("");
  let sichereAdresse = $state("");

  const einst = $derived(konto.daten?.einstellungen ?? { ...VORGABE, orte: ansicht.ort ? [ansicht.ort] : [] });
  const pushAn = $derived(Boolean(konto.daten?.push));

  onMount(() => {
    void ladeKonto();
    if (lage === "unsicher") void serverSchluessel().then((s) => (sichereAdresse = s.sichere_adresse)).catch(() => undefined);
  });

  async function aendern(teil: Partial<Meldeeinstellungen>): Promise<void> {
    if (!konto.daten) await sicheresKonto(ansicht.ort);
    await einstellen(teil);
  }

  async function pushSchalten(): Promise<void> {
    if (beschaeftigt) return;
    beschaeftigt = true;
    meldung = "";
    try {
      if (pushAn) await ausschalten();
      else {
        const ergebnis = await einschalten(ansicht.ort);
        if (ergebnis === "verweigert") meldung = "Mitteilungen sind für die Wetterwarte nicht erlaubt. Das lässt sich in den Einstellungen des Telefons ändern.";
        if (ergebnis === "fehler") meldung = "Das Einschalten hat nicht geklappt. Bitte später noch einmal versuchen.";
      }
    } catch {
      meldung = "Der Server ist gerade nicht erreichbar.";
    } finally {
      lage = pushLage();
      beschaeftigt = false;
    }
  }

  async function probeSenden(): Promise<void> {
    meldung = "";
    const ergebnis = await probe().catch(() => "fehler" as const);
    meldung = {
      ok: "Probemitteilung ist unterwegs.",
      weg: "Das Abo gibt es nicht mehr; bitte Mitteilungen neu einschalten.",
      fehler: "Die Probemitteilung kam nicht durch.",
      kein_abo: "Erst Mitteilungen einschalten.",
    }[ergebnis];
  }

  function ortUmschalten(slug: string): void {
    const orte = einst.orte.includes(slug) ? einst.orte.filter((o) => o !== slug) : [...einst.orte, slug];
    void aendern({ orte });
  }

  function artUmschalten(art: Meldeart): void {
    const arten = einst.arten.includes(art) ? einst.arten.filter((a) => a !== art) : [...einst.arten, art];
    void aendern({ arten });
  }

  function ruhe(teil: Partial<Meldeeinstellungen["nachtruhe"]>): void {
    void aendern({ nachtruhe: { ...einst.nachtruhe, ...teil } });
  }

  const stunde = (h: number) => (h + 24) % 24;
</script>

<div class="einstellungen">
  <section class="abschnitt">
    <h3>Mitteilungen aufs Telefon</h3>
    {#if lage === "unsicher"}
      <p class="hinweis-z warn">
        <i class="fa-solid fa-lock"></i>
        <span>Mitteilungen gibt es nur über die sichere Adresse{sichereAdresse ? `: ${sichereAdresse}/telefon` : ""}. Dort öffnen, zum Home-Bildschirm hinzufügen und hier einschalten.</span>
      </p>
    {:else if lage === "heimbildschirm"}
      <p class="hinweis-z warn">
        <i class="fa-solid fa-square-plus"></i>
        <span>Auf dem iPhone kommen Mitteilungen nur in der App vom Home-Bildschirm: Teilen, Zum Home-Bildschirm, dann von dort starten.</span>
      </p>
    {:else if lage === "nicht-unterstuetzt"}
      <p class="hinweis-z warn"><i class="fa-solid fa-ban"></i><span>Dieser Browser kann keine Mitteilungen empfangen.</span></p>
    {:else}
      <div class="zeilen">
        <button class="zeile" onclick={pushSchalten} disabled={beschaeftigt || lage === "verweigert"}>
          <span class="sym"><i class="fa-solid fa-bell"></i></span>
          <span class="haupt"><b>Mitteilungen</b><small>{pushAn ? "Kommen auch bei geschlossener App" : "Aus"}</small></span>
          <span class="schalter" class:an={pushAn}></span>
        </button>
        {#if pushAn}
          <button class="zeile" onclick={probeSenden}>
            <span class="sym"><i class="fa-solid fa-paper-plane"></i></span>
            <span class="haupt"><b>Probemitteilung senden</b></span>
          </button>
        {/if}
      </div>
      {#if lage === "verweigert"}
        <p class="hinweis-z warn"><i class="fa-solid fa-bell-slash"></i><span>Mitteilungen sind in den Einstellungen des Telefons für die Wetterwarte abgeschaltet.</span></p>
      {/if}
    {/if}
    {#if meldung}<p class="hinweis-z warn"><i class="fa-solid fa-circle-info"></i><span>{meldung}</span></p>{/if}
    {#if konto.fehler}<p class="hinweis-z warn"><i class="fa-solid fa-plug-circle-xmark"></i><span>{konto.fehler}</span></p>{/if}
  </section>

  <section class="abschnitt">
    <h3>Für diese Orte</h3>
    <div class="zeilen">
      {#each orteState.liste as o (o.slug)}
        {@const gewaehlt = einst.orte.includes(o.slug)}
        <button class="zeile" class:an={gewaehlt} aria-pressed={gewaehlt} onclick={() => ortUmschalten(o.slug)}>
          <span class="sym"><i class="fa-solid fa-location-dot"></i></span>
          <span class="haupt"><b>{o.name}</b>{#if o.region}<small>{o.region}</small>{/if}</span>
          {#if gewaehlt}<span class="rechts"><i class="fa-solid fa-check"></i></span>{/if}
        </button>
      {/each}
    </div>
    {#if !einst.orte.length}<p class="hinweis-z warn"><i class="fa-solid fa-circle-info"></i><span>Ohne Ort kommen keine Mitteilungen.</span></p>{/if}
  </section>

  <section class="abschnitt">
    <h3>Tonansagen</h3>
    <div class="zeilen">
      <button class="zeile" onclick={() => ansagenSchalten(!ansagen.an, ansicht.ort)}>
        <span class="sym"><i class="fa-solid fa-volume-high"></i></span>
        <span class="haupt"><b>Ansagen bei offener App</b><small>Spricht neue Meldungen für den gezeigten Ort</small></span>
        <span class="schalter" class:an={ansagen.an}></span>
      </button>
      <button class="zeile" onclick={probeansage}>
        <span class="sym"><i class="fa-solid fa-play"></i></span>
        <span class="haupt"><b>Probeansage</b></span>
      </button>
    </div>
    <p class="hinweis-z"><i class="fa-solid fa-circle-info"></i><span>Auf dem iPhone muss der Ton an sein; nach dem Zurückkehren in die App einmal tippen.</span></p>
  </section>

  <section class="abschnitt">
    <h3>Was gemeldet wird</h3>
    <div class="zeilen">
      {#each meldekatalog.arten as a (a.schluessel)}
        {@const an = einst.arten.includes(a.schluessel)}
        <button class="zeile" class:an aria-pressed={an} onclick={() => artUmschalten(a.schluessel)}>
          <span class="sym"><i class="fa-solid {a.symbol}"></i></span>
          <span class="haupt"><b>{a.name}</b><small>{a.beschreibung}</small></span>
          {#if an}<span class="rechts"><i class="fa-solid fa-check"></i></span>{/if}
        </button>
      {/each}
    </div>
  </section>

  <section class="abschnitt">
    <div class="einstellung">
      <div class="einst-kopf"><b>Regen und Schnee</b><small>ab welcher Stärke</small></div>
      <div class="segmente" role="radiogroup" aria-label="Regen und Schnee ab">
        {#each meldekatalog.optionen.niederschlag_ab as o (o.wert)}
          <button class:an={einst.niederschlag_ab === o.wert} role="radio" aria-checked={einst.niederschlag_ab === o.wert} onclick={() => aendern({ niederschlag_ab: o.wert })}>{o.name}</button>
        {/each}
      </div>
    </div>
    <div class="einstellung">
      <div class="einst-kopf"><b>Sturm</b><small>Böen ab km/h</small></div>
      <div class="segmente" role="radiogroup" aria-label="Sturm ab">
        {#each meldekatalog.optionen.wind_ab as o (o.wert)}
          <button class:an={einst.wind_ab === o.wert} role="radio" aria-checked={einst.wind_ab === o.wert} onclick={() => aendern({ wind_ab: o.wert })}>{o.name}</button>
        {/each}
      </div>
    </div>
    <div class="einstellung">
      <div class="einst-kopf"><b>Vorlauf</b><small>erste Meldung, Stunden vorher</small></div>
      <div class="segmente" role="radiogroup" aria-label="Vorlauf in Stunden">
        {#each meldekatalog.optionen.vorlauf_min as o (o.wert)}
          <button class:an={einst.vorlauf_min === o.wert} role="radio" aria-checked={einst.vorlauf_min === o.wert} onclick={() => aendern({ vorlauf_min: o.wert })}>{o.name}</button>
        {/each}
      </div>
      <div class="einst-unter">Regen und Schnee meldet die Wetterwarte danach bei jeder neuen Stufe, zuletzt 15 Minuten vorher.</div>
    </div>
  </section>

  <section class="abschnitt">
    <div class="einstellung">
      <div class="einst-kopf"><b>Nachtruhe</b><small>nur Mitteilungen</small></div>
      <div class="segmente" role="radiogroup" aria-label="Nachtruhe">
        <button class:an={!einst.nachtruhe.an} role="radio" aria-checked={!einst.nachtruhe.an} onclick={() => ruhe({ an: false })}>Aus</button>
        <button class:an={einst.nachtruhe.an} role="radio" aria-checked={einst.nachtruhe.an} onclick={() => ruhe({ an: true })}>An</button>
      </div>
      {#if einst.nachtruhe.an}
        <div class="ruhezeit">
          <div class="stellrad">
            <span>von</span>
            <button class="knopf-rund flaeche" aria-label="Beginn früher" onclick={() => ruhe({ von: stunde(einst.nachtruhe.von - 1) })}><i class="fa-solid fa-minus"></i></button>
            <b>{einst.nachtruhe.von} Uhr</b>
            <button class="knopf-rund flaeche" aria-label="Beginn später" onclick={() => ruhe({ von: stunde(einst.nachtruhe.von + 1) })}><i class="fa-solid fa-plus"></i></button>
          </div>
          <div class="stellrad">
            <span>bis</span>
            <button class="knopf-rund flaeche" aria-label="Ende früher" onclick={() => ruhe({ bis: stunde(einst.nachtruhe.bis - 1) })}><i class="fa-solid fa-minus"></i></button>
            <b>{einst.nachtruhe.bis} Uhr</b>
            <button class="knopf-rund flaeche" aria-label="Ende später" onclick={() => ruhe({ bis: stunde(einst.nachtruhe.bis + 1) })}><i class="fa-solid fa-plus"></i></button>
          </div>
        </div>
        <div class="einst-unter">In dieser Zeit kommen nur Unwetter ab Stufe {einst.nachtruhe.ab_stufe}, in der Ortszeit des gemeldeten Orts.</div>
      {/if}
    </div>
  </section>
</div>

<style>
  .ruhezeit {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 18px;
    margin: 12px 8px 0;
  }
  .stellrad {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .stellrad span {
    min-width: 28px;
    color: var(--text-3);
    font-size: var(--s15);
  }
  .stellrad b {
    min-width: 64px;
    text-align: center;
    font-variant-numeric: tabular-nums;
  }
  button.zeile:disabled {
    opacity: 0.55;
  }
</style>
