// Symbol eines Profils: das selbst gewählte, sonst das Standardsymbol nach Namen. Eine Stelle für
// Desktop und Telefon.
const SYMBOL_NACH_NAME: Record<string, string> = {
  Zuhause: "fa-house",
  Garten: "fa-seedling",
  Reise: "fa-suitcase-rolling",
  Unwetter: "fa-triangle-exclamation",
};

export function profilSymbol(p: { name: string; icon?: string | null }): string {
  return p.icon || SYMBOL_NACH_NAME[p.name] || "fa-table-cells-large";
}
