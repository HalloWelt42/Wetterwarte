<script lang="ts">
  import Kopf from "./lib/Kopf.svelte";
  import Nav from "./lib/Nav.svelte";
  import Brett from "./lib/Brett.svelte";
</script>

<div class="app">
  <Kopf />
  <Nav />
  <section class="inhalt">
    <div class="werkzeuge">
      <div class="orts-titel">Köln <small>Sachsen-Anhalt &middot; aktualisiert vor 3 Min</small></div>
      <span class="luecke"></span>
      <button class="knopf klein"><i class="fa-solid fa-pen"></i> Layout bearbeiten</button>
    </div>
    <Brett />
  </section>
</div>
