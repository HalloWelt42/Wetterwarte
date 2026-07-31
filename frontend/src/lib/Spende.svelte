<script lang="ts">
  // "Danke sagen"-Overlay: Ko-fi als wichtigster Weg (mit QR zum Scannen) plus
  // Krypto-Adressen (QR + Kopieren). Alles freiwillig, kein Tracking, keine Werbung.
  import { ui } from "./ui.svelte";
  import { qrSvg } from "./qr";

  const KOFI = "https://ko-fi.com/HalloWelt42";

  interface Krypto {
    id: string;
    label: string;
    symbol: string;
    icon: string;
    farbe: string;
    adresse: string;
  }
  const kryptos: Krypto[] = [
    { id: "btc", label: "Bitcoin", symbol: "BTC", icon: "fa-brands fa-bitcoin", farbe: "#f7931a", adresse: "bc1qnd599khdkv3v3npmj9ufxzf6h4fzanny2acwqr" },
    { id: "doge", label: "Dogecoin", symbol: "DOGE", icon: "fa-solid fa-dog", farbe: "#c3a634", adresse: "DL7tuiYCqm3xQjMDXChdxeQxqUGMACn1ZV" },
    { id: "eth", label: "Ethereum", symbol: "ETH", icon: "fa-brands fa-ethereum", farbe: "#627eea", adresse: "0x8A28fc47bFFFA03C8f685fa0836E2dBe1CA14F27" },
  ];

  // QR-Codes einmalig erzeugen (statische Adressen, kein Neuberechnen noetig).
  const kofiQr = qrSvg(KOFI);
  const kryptoQr: Record<string, string> = Object.fromEntries(kryptos.map((k) => [k.id, qrSvg(k.adresse)]));

  let offen = $state<string | null>(null);
  let kopiert = $state<string | null>(null);

  function waehle(id: string): void {
    offen = offen === id ? null : id;
  }
  async function kopiere(adresse: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(adresse);
      kopiert = adresse;
      setTimeout(() => (kopiert = null), 1800);
    } catch {
      /* Zwischenablage nicht verfuegbar - dann bleibt die Adresse zum Markieren sichtbar. */
    }
  }
  function zu(): void {
    ui.spende = false;
  }
</script>

<div class="modal-hg" role="presentation" onclick={zu}>
  <div class="modal" role="dialog" tabindex="-1" onclick={(e) => e.stopPropagation()}>
    <div class="modal-kopf">
      <h2><i class="fa-solid fa-heart" style="color: var(--gefahr)"></i> Danke sagen</h2>
      <span style="flex: 1"></span>
      <button class="icon-knopf" onclick={zu} aria-label="Schließen"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="modal-inhalt">
      <p class="spende-intro">
        Die Wetterwarte ist ein privates Projekt - kein Tracking, keine Werbung, alles selbst gehostet. Wenn sie dir
        gefällt, kannst du auf einen Kaffee einladen. Freut mich sehr - danke!
      </p>

      <div class="kofi-block">
        <a href={KOFI} target="_blank" rel="noopener" class="kofi-knopf">
          <i class="fa-solid fa-mug-hot"></i> <span>Einen Kaffee spendieren (Ko-fi)</span>
        </a>
        <div class="qr-feld gross">
          <!-- eslint-disable-next-line svelte/no-at-html-tags (statischer, selbst erzeugter QR) -->
          {@html kofiQr}
          <small class="dimm">Mit dem Handy scannen</small>
        </div>
      </div>

      <div class="spende-trenner"><span></span><small>oder per Krypto</small><span></span></div>

      <div class="krypto-liste">
        {#each kryptos as k}
          <button class="krypto-karte" class:offen={offen === k.id} onclick={() => waehle(k.id)}>
            <i class={k.icon} style="color: {k.farbe}"></i>
            <span class="kk-name"><b>{k.label}</b> <small class="dimm">{k.symbol}</small></span>
            <i class="fa-solid fa-chevron-down kk-pfeil"></i>
          </button>
          {#if offen === k.id}
            <div class="krypto-auf">
              <div class="qr-feld">
                <!-- eslint-disable-next-line svelte/no-at-html-tags (statischer, selbst erzeugter QR) -->
                {@html kryptoQr[k.id]}
              </div>
              <div class="krypto-adresse">
                <code>{k.adresse}</code>
                <button class="knopf" onclick={() => kopiere(k.adresse)}>
                  <i class="fa-solid {kopiert === k.adresse ? 'fa-check' : 'fa-copy'}"></i>
                  {kopiert === k.adresse ? "Kopiert" : "Kopieren"}
                </button>
              </div>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </div>
</div>
