<script lang="ts">
  let variable = $state("Temperatur");
  let zeitraum = $state("30 Tage");

  const rekorde = [
    { wert: "18,4°", klasse: "t-mild", label: "Monatsmittel", pille: "+1,2 K vs. Normal", pilleArt: "warn" },
    { wert: "34,6°", klasse: "t-extrem", label: "Tagesrekord Höchstwert", sub: "20.07.2022" },
    { wert: "42 mm", klasse: "", label: "Niederschlag", pille: "78% des Solls", pilleArt: "" },
    { wert: "232 h", klasse: "", label: "Sonnenstunden", pille: "+18 h vs. Normal", pilleArt: "gut" },
    { wert: "0", klasse: "t-frost", label: "Frosttage", sub: "unter 0° Tiefstwert" },
    { wert: "6", klasse: "t-heiss", label: "Hitzetage", sub: "ab 30° Höchstwert" },
  ];

  // Jahres-Heatmap programmatisch: Winter kuehl, Hochsommer warm, eine Zelle je ~2 Tage.
  const skala = ["--t-frost", "--t-kalt", "--t-kuehl", "--t-mild", "--t-warm", "--t-heiss", "--t-extrem"];
  function heatmapFarbe(i: number, n: number): string {
    const jahr = i / n; // 0 = Januar ... 1 = Dezember
    const grund = 0.5 - 0.5 * Math.cos(jahr * Math.PI * 2); // Minimum Winter, Maximum Sommer
    const wackeln = (((i * 7) % 5) - 2) * 0.04; // leichte Tagesstreuung
    const wert = Math.max(0, Math.min(0.999, grund + wackeln));
    return `var(${skala[Math.floor(wert * skala.length)]})`;
  }
  const zellen = Array.from({ length: 159 }, (_, i) => heatmapFarbe(i, 159));
</script>

<section class="inhalt">
  <div class="seite">
    <h1>Archiv und Analyse</h1>
    <p class="unter-gross">
      Langzeitdaten aus der eigenen PostgreSQL - Verläufe, Rekorde und Abweichungen vom Klimamittel
      (Normalperiode 1991-2020).
    </p>

    <div class="reihe" style="gap: var(--a3); flex-wrap: wrap; margin-bottom: var(--a4)">
      <select class="feld" style="width: auto; min-width: 210px">
        <option>Station: Köln (04501)</option>
        <option>Station: Frankfurt-Holzhausen (02928)</option>
        <option>Station: Berlin-Tempelhof (00433)</option>
        <option>Station: Hamburg-Fuhlsbüttel (01975)</option>
        <option>Station: München-Stadt (03379)</option>
      </select>
      <span class="segment">
        {#each ["Temperatur", "Niederschlag", "Wind", "Druck"] as v}
          <button class:aktiv={variable === v} onclick={() => (variable = v)}>{v}</button>
        {/each}
      </span>
      <span class="segment">
        {#each ["24 h", "7 Tage", "30 Tage", "Jahr"] as z}
          <button class:aktiv={zeitraum === z} onclick={() => (zeitraum = z)}>{z}</button>
        {/each}
      </span>
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-chart-line"></i> Verlauf</h2>
      <p class="unter">Tagesmittel der Lufttemperatur, letzte 30 Tage &middot; Station Köln (04501)</p>
      <svg class="chart-flaeche" viewBox="0 0 600 180" preserveAspectRatio="none" style="height: 180px; width: 100%">
        <defs>
          <linearGradient id="tflaeche" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#2f7ce0" stop-opacity="0.30" />
            <stop offset="1" stop-color="#2f7ce0" stop-opacity="0" />
          </linearGradient>
        </defs>
        <g style="stroke: var(--rand); stroke-width: 1">
          <line x1="0" y1="46" x2="600" y2="46" /><line x1="0" y1="98" x2="600" y2="98" /><line x1="0" y1="150" x2="600" y2="150" />
        </g>
        <path d="M0,137 L21,131 L41,118 L62,124 L83,111 L103,98 L124,105 L145,118 L165,131 L186,124 L207,111 L228,92 L248,79 L269,66 L290,53 L310,40 L331,46 L352,59 L372,85 L393,105 L414,118 L434,98 L455,85 L476,72 L497,59 L517,46 L538,66 L559,92 L579,111 L600,124 L600,180 L0,180 Z" fill="url(#tflaeche)" />
        <polyline points="0,137 21,131 41,118 62,124 83,111 103,98 124,105 145,118 165,131 186,124 207,111 228,92 248,79 269,66 290,53 310,40 331,46 352,59 372,85 393,105 414,118 434,98 455,85 476,72 497,59 517,46 538,66 559,92 579,111 600,124" style="fill: none; stroke: var(--akzent); stroke-width: 2" />
      </svg>
      <div class="reihe" style="justify-content: space-between; margin-top: var(--a2)">
        <span class="klein-txt dimm">30. Juni</span><span class="klein-txt dimm">14. Juli</span><span class="klein-txt dimm">29. Juli</span>
      </div>
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-award"></i> Rekorde und Klima-Abweichung</h2>
      <p class="unter">Juli 2026 im Vergleich zur Normalperiode 1991-2020</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--a3)">
        {#each rekorde as r}
          <div style="background: var(--flaeche-2); border: 1px solid var(--rand); border-radius: var(--r2); padding: var(--a3)">
            <div class="tnum {r.klasse}" style="font-size: 1.9rem; font-weight: 600; line-height: 1">{r.wert}</div>
            <div class="klein-txt dimm" style="margin: 4px 0 var(--a2)">{r.label}</div>
            {#if r.pille}
              <span class="pille {r.pilleArt}">{r.pille}</span>
            {:else if r.sub}
              <small class="dimm tnum">{r.sub}</small>
            {/if}
          </div>
        {/each}
      </div>
    </div>

    <div class="panel">
      <h2><i class="fa-solid fa-calendar"></i> Jahresrückblick (Temperatur je Tag)</h2>
      <p class="unter">Tagesmittel Januar bis Dezember - eine Zelle je Tag, Farbe nach Temperatur</p>
      <div class="heatmap">
        {#each zellen as farbe}
          <span class="hz" style="background: {farbe}"></span>
        {/each}
      </div>
      <div class="reihe" style="gap: var(--a2); margin-top: var(--a3); font-size: 0.72rem; color: var(--text-3)">
        <span>kalt</span>
        <span style="height: 8px; width: 140px; border-radius: 4px; background: linear-gradient(90deg, var(--t-frost), var(--t-kalt), var(--t-kuehl), var(--t-mild), var(--t-warm), var(--t-heiss), var(--t-extrem))"></span>
        <span>heiß</span>
      </div>
    </div>
  </div>
</section>
