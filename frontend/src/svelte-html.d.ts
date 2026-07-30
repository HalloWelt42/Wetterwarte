// gridstack setzt/liest eigene Attribute an den Kachel-Elementen. Hier fuer die
// Svelte-Typpruefung bekannt machen, damit `svelte-check` sie akzeptiert.
declare namespace svelteHTML {
  interface HTMLAttributes<T> {
    "gs-id"?: string;
    "gs-x"?: number;
    "gs-y"?: number;
    "gs-w"?: number;
    "gs-h"?: number;
  }
}
