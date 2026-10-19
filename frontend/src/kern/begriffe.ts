// Kurze, allgemeinverstaendliche Erklaerungen fuer Fachbegriffe und Abkuerzungen
// auf den Kacheln. Zentral gepflegt, damit die Hover-Erklaerungen einheitlich sind.
export const begriffe = {
  aqi: "Europäischer Luftqualitätsindex: fasst mehrere Schadstoffe zu einem Wert von 0 (sehr gut) bis über 100 (sehr schlecht) zusammen.",
  pm25: "Feinstaub unter 2,5 Mikrometer - so klein, dass er tief in die Lunge gelangt. Angabe in Mikrogramm je Kubikmeter Luft.",
  pm10: "Feinstaub unter 10 Mikrometer, etwa Staub und Pollen. Angabe in Mikrogramm je Kubikmeter Luft.",
  ozon: "Ozon reizt in Bodennähe bei Hitze die Atemwege. Angabe in Mikrogramm je Kubikmeter Luft.",
  no2: "Stickstoffdioxid stammt vor allem aus Verkehr und Verbrennung. Angabe in Mikrogramm je Kubikmeter Luft.",
  hpa: "Hektopascal ist die Einheit des Luftdrucks. Auf Meereshöhe herrschen im Mittel rund 1013 hPa.",
  taupunkt: "Temperatur, bei der die Luft ihren Wasserdampf nicht mehr halten kann und Tau entsteht. Je höher, desto schwüler fühlt es sich an.",
  boeen: "Kurze, kräftige Windspitzen, die deutlich stärker sind als der mittlere Wind.",
  uv: "Der UV-Index zeigt die Stärke der Sonnen-Strahlung. Ab 3 ist Schutz sinnvoll, ab 8 wird sie sehr intensiv.",
  nowcast: "Sehr kurzfristige Vorhersage für die nächsten Minuten bis wenige Stunden - hier: Regen in deiner Nähe.",
} as const;
