// Bruecke Katalog -> Brett: der Katalog setzt hier den hinzuzufuegenden Kacheltyp,
// das Brett nimmt ihn auf und setzt zurueck.
export const kachelAktion = $state<{ add: string | null }>({ add: null });

// Bruecke Brett -> Katalog: das Brett spiegelt hier, wie oft jeder Kacheltyp im
// aktuellen Layout gesetzt ist, damit der Katalog es je Kachel anzeigen kann.
export const brettState = $state<{ anzahlJeTyp: Record<string, number> }>({ anzahlJeTyp: {} });
