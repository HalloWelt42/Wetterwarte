// Bruecke Katalog -> Brett: der Katalog setzt hier den hinzuzufuegenden Kacheltyp,
// das Brett nimmt ihn auf und setzt zurueck.
export const kachelAktion = $state<{ add: string | null }>({ add: null });
