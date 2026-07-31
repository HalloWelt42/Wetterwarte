<script lang="ts">
  import { ui } from "./ui.svelte";
  import { konf } from "./kachelConf.svelte";
  import { registry, type Feld } from "./kacheln/registry";
  import { orteState } from "./orte.svelte";

  const def = $derived(registry[konf.typ]);
  const felder = $derived(def?.einstellungen ?? []);

  // Alle echten IANA-Zeitzonen (fuer das Zeitzonen-Feld der Uhr).
  const zeitzonen: string[] = (Intl as unknown as { supportedValuesOf?: (k: string) => string[] }).supportedValuesOf?.("timeZone") ?? [];

  function setzeFeld(schluessel: string, wert: string): void {
    konf.werte[schluessel] = wert;
    geaendert();
  }

  function geaendert(): void {
    konf.version++;
  }

  // Ort dieser Kachel; leer = folgt dem aktiven Ort oben.
  function ortEingabe(e: Event): void {
    konf.werte.ort = (e.target as HTMLSelectElement).value;
    geaendert();
  }

  // Mehrfachauswahl (Checkbox-artige Schalter je Option)
  function istAn(feld: Feld, wert: string | number): boolean {
    const arr = konf.werte[feld.schluessel] as (string | number)[] | undefined;
    if (arr === undefined) return !feld.leerStandard;
    return arr.includes(wert);
  }
  function toggle(feld: Feld, wert: string | number): void {
    let arr = konf.werte[feld.schluessel] as (string | number)[] | undefined;
    if (arr === undefined) arr = feld.leerStandard ? [] : (feld.optionen ?? []).map((o) => o.wert);
    arr = arr.includes(wert) ? arr.filter((x) => x !== wert) : [...arr, wert];
    konf.werte[feld.schluessel] = arr;
    geaendert();
  }

  // Einfachauswahl (Segment)
  function aktuelleAuswahl(feld: Feld): string | number | undefined {
    const w = konf.werte[feld.schluessel] as string | number | undefined;
    if (w !== undefined) return w;
    const opt = feld.optionen ?? [];
    return opt.length ? opt[opt.length - 1].wert : undefined;
  }
  function setzeAuswahl(feld: Feld, wert: string | number): void {
    konf.werte[feld.schluessel] = wert;
    geaendert();
  }

  function titelEingabe(e: Event): void {
    konf.werte.titel = (e.target as HTMLInputElement).value;
    geaendert();
  }

  function zu(): void {
    ui.einstellungen = false;
  }
</script>

<div class="modal-hg" role="presentation" onclick={zu}>
  <div class="modal" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="modal-kopf">
      <h2><i class="fa-solid {def?.icon ?? 'fa-sliders'}"></i> {def?.titel ?? "Kachel"} - Einstellungen</h2>
      <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-inhalt">
      <div class="formzeile">
        <label for="kachel-titel">Eigener Titel (optional)</label>
        <input
          id="kachel-titel"
          class="feld"
          type="text"
          placeholder={def?.titel ?? ""}
          value={(konf.werte.titel as string) ?? ""}
          oninput={titelEingabe}
        />
      </div>

      <div class="formzeile">
        <label for="kachel-ort">Ort dieser Kachel</label>
        <select id="kachel-ort" class="feld" value={(konf.werte.ort as string) ?? ""} onchange={ortEingabe}>
          <option value="">Aktiver Ort (folgt oben)</option>
          {#each orteState.liste as o}
            <option value={o.slug}>{o.name}{#if o.region}&nbsp;({o.region}){/if}</option>
          {/each}
        </select>
      </div>

      {#each felder as feld}
        {#if feld.art === "mehrfach"}
          <div>
            <div class="kat-gruppe">{feld.label}</div>
            {#each feld.optionen ?? [] as o}
              <div class="formzeile-quer">
                <span class="fz-lab">{o.label}</span>
                <button class="schalter" class:an={istAn(feld, o.wert)} onclick={() => toggle(feld, o.wert)} aria-label={o.label}></button>
              </div>
            {/each}
          </div>
        {:else if feld.art === "auswahl"}
          <div class="formzeile-quer">
            <span class="fz-lab">{feld.label}</span>
            <span class="segment">
              {#each feld.optionen ?? [] as o}
                <button class:aktiv={aktuelleAuswahl(feld) === o.wert} onclick={() => setzeAuswahl(feld, o.wert)}>{o.label}</button>
              {/each}
            </span>
          </div>
        {:else if feld.art === "zeitzone"}
          <div class="formzeile">
            <label for="feld-{feld.schluessel}">{feld.label}</label>
            <select
              id="feld-{feld.schluessel}"
              class="feld"
              value={(konf.werte[feld.schluessel] as string) ?? ""}
              onchange={(e) => setzeFeld(feld.schluessel, e.currentTarget.value)}
            >
              <option value="">Automatisch (Gerät)</option>
              {#each zeitzonen as z}<option value={z}>{z.replace(/_/g, " ")}</option>{/each}
            </select>
          </div>
        {/if}
      {/each}

      {#if felder.length === 0}
        <p class="dimm klein-txt" style="padding: var(--a2) 0">Diese Kachel hat ausser dem Titel keine weiteren Optionen.</p>
      {/if}
    </div>
    <div class="modal-fuss">
      <button class="knopf primaer" onclick={zu}>Fertig</button>
    </div>
  </div>
</div>
