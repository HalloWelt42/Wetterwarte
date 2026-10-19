// WMO-Wettercode zu Wettersymbol und Text (aus gemeinsam/wettercodes.json).
import { wettercodes, type Wettercodes } from "./gemeinsam";

const tabelle = new Map<number, Wettercodes["gruppen"][number]>();
for (const g of wettercodes.gruppen) for (const c of g.codes) tabelle.set(c, g);

export function bildName(code: number, tag: boolean): string {
  const g = tabelle.get(code) ?? wettercodes.sonst;
  return tag ? g.tag : g.nacht;
}

export function zustandText(code: number): string {
  return (tabelle.get(code) ?? wettercodes.sonst).text;
}
