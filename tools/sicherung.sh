# shellcheck shell=bash
# Sicherung der Datenbank im Betrieb (docs/DEPLOY-PI.md, Abschnitt Sicherung). Wird von ./wetter geladen
# (./wetter sicherung [regelmaessig|vor-ausrollen]) und nutzt dessen PROD, also das Compose des Betriebs mit .env.prod.
#
# Regel: regelmäßig erst, wenn die jüngste Sicherung SICHERUNG_ABSTAND_TAGE alt ist, vor dem Ausrollen erst ab
# SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN; nie ohne Änderung; höchstens SICHERUNG_BEHALTEN Stände, bei jedem Lauf
# durchgesetzt. Ob fällig, entscheidet der Lauf selbst, ein zu früher Aufruf tut nichts.
#
# Gesichert wird ein Auszug der Postgres: Profile und Ansichten, Orte, Einstellungen, Geräte samt Schlüssel für Web
# Push und das Langzeit-Archiv der Messwerte. Was von selbst neu entsteht, bleibt draußen: Redis (Zwischenspeicher mit
# Ablaufzeit), der Kachel-Cache (Dateien) und der Inhalt der Tabellen in SICHERUNG_OHNE_INHALT.

# Vorgaben der Sicherungsregel, nur hier; die Umgebung oder .env.prod überschreiben sie.
SICHERUNG_VORGABE_ABSTAND_TAGE=7
SICHERUNG_VORGABE_VOR_AUSROLLEN_AB_STUNDEN=24
SICHERUNG_VORGABE_BEHALTEN=3

# Tabellen, deren Inhalt von selbst neu entsteht; im Auszug steht nur ihr Aufbau.
#   radararchivframe: Radarbilder, rollend höchstens zwei Wochen, mehrere GB
#   klimanormale:     Klima-Normale, holt das Backend bei Bedarf neu aus dem Open-Meteo-Archiv
SICHERUNG_OHNE_INHALT=(radararchivframe klimanormale)

# Nur Dateien nach diesem Muster sind Sicherungen; nichts anderes im Ordner wird angefasst. Teildateien beginnen mit
# einem Punkt und passen nicht dazu.
SICHERUNG_MUSTER='wetterwarte-????????-??????.sql.gz'

# Wert aus der Umgebung, sonst aus .env.prod (Umgebung vor Datei, wie bei Compose), sonst die Vorgabe
sicherung_wert() {
  local name="$1" vorgabe="$2" wert="${!1:-}"
  [ -n "$wert" ] || wert="$(sed -n "s/^${name}=//p" .env.prod | tail -n 1)"
  case "$wert" in \"*\" | \'*\') wert="${wert:1:${#wert}-2}" ;; esac
  printf '%s' "${wert:-$vorgabe}"
}

sicherung_zahl_pruefen() {
  local name="$1" wert="$2" mindestens="$3"
  case "$wert" in
    '' | *[!0-9]*) echo "$name muss eine ganze Zahl sein, nicht '$wert'" >&2; return 1 ;;
  esac
  [ "$wert" -ge "$mindestens" ] || { echo "$name muss mindestens $mindestens sein" >&2; return 1; }
}

sicherung_werte_laden() {
  local data_dir
  SICHERUNG_ABSTAND_TAGE="$(sicherung_wert SICHERUNG_ABSTAND_TAGE "$SICHERUNG_VORGABE_ABSTAND_TAGE")"
  SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN="$(sicherung_wert SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN "$SICHERUNG_VORGABE_VOR_AUSROLLEN_AB_STUNDEN")"
  SICHERUNG_BEHALTEN="$(sicherung_wert SICHERUNG_BEHALTEN "$SICHERUNG_VORGABE_BEHALTEN")"
  sicherung_zahl_pruefen SICHERUNG_ABSTAND_TAGE "$SICHERUNG_ABSTAND_TAGE" 0 \
    && sicherung_zahl_pruefen SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN "$SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN" 0 \
    && sicherung_zahl_pruefen SICHERUNG_BEHALTEN "$SICHERUNG_BEHALTEN" 1 || return 1
  # Ort neben den übrigen Daten der App (DATA_DIR in .env.prod, aus der privaten Wahrheit des Hauses)
  data_dir="$(sicherung_wert DATA_DIR "")"
  [ -n "$data_dir" ] || { echo "DATA_DIR fehlt in .env.prod (Ordner der Daten, darunter sicherungen)" >&2; return 1; }
  SICHERUNG_ORDNER="$data_dir/sicherungen"
}

# Sicherungen, neueste zuerst (nach Änderungszeit)
sicherung_staende() {
  find "$SICHERUNG_ORDNER" -maxdepth 1 -type f -name "$SICHERUNG_MUSTER" -exec ls -1t {} +
}

# Alter einer Datei in ganzen Einheiten (gerundet): ein wöchentlicher cron-Lauf ist so auch dann fällig, wenn er
# Sekunden oder (Zeitumstellung) eine Stunde früher kommt als der Lauf vor einer Woche.
sicherung_alter() {
  local datei="$1" einheit_s="$2"
  echo $(( ($(date +%s) - $(date -r "$datei" +%s) + einheit_s / 2) / einheit_s ))
}

# Auszug als SQL aus dem laufenden Postgres-Container; Nutzer und Datenbank nimmt pg_dump aus dessen Umgebung
sicherung_auszug() {
  local ohne=() tabelle
  for tabelle in "${SICHERUNG_OHNE_INHALT[@]}"; do ohne+=("--exclude-table-data=$tabelle"); done
  # shellcheck disable=SC2016,SC2086
  $PROD exec -T postgres sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"' pg_dump "${ohne[@]}"
}

# Prüfsumme des Inhalts. Den Schlüssel in den Zeilen \restrict und \unrestrict würfelt pg_dump bei jedem Lauf neu,
# diese Zeilen zählen darum nicht mit.
sicherung_inhalt() {
  gzip -dc "$1" | sed '/^\\\(un\)\{0,1\}restrict /d' | sha256sum | cut -d' ' -f1
}

# Auszug in eine Teildatei; nur wenn er sich von der jüngsten Sicherung unterscheidet, wird er zur neuen Sicherung,
# mit dem Beginn des Auszugs als Name und Änderungszeit.
sicherung_anlegen() {
  local juengste="$1" beginn name
  beginn="$(date +%Y%m%d-%H%M%S)"
  name="wetterwarte-$beginn.sql.gz"
  # Teildatei ohne local: die Falle räumt sie erst beim Ende des Laufs weg, wenn diese Funktion schon zurück ist
  SICHERUNG_TEIL="$SICHERUNG_ORDNER/.$name.teil"
  trap 'rm -f "$SICHERUNG_TEIL"' EXIT
  sicherung_auszug | gzip -n > "$SICHERUNG_TEIL" || { echo "Auszug der Datenbank gescheitert" >&2; return 1; }
  if [ -n "$juengste" ] && [ "$(sicherung_inhalt "$SICHERUNG_TEIL")" = "$(sicherung_inhalt "$juengste")" ]; then
    echo "Keine Änderung seit $(basename "$juengste"), keine neue Sicherung"
    return 0
  fi
  touch -t "${beginn:0:8}${beginn:9:4}.${beginn:13:2}" "$SICHERUNG_TEIL"
  mv "$SICHERUNG_TEIL" "$SICHERUNG_ORDNER/$name"
  echo "Gesichert: $SICHERUNG_ORDNER/$name ($(du -h "$SICHERUNG_ORDNER/$name" | cut -f1))"
}

# Höchstens SICHERUNG_BEHALTEN Stände; ältere gehen, auch wenn keine neue Sicherung entstanden ist
sicherung_aufraeumen() {
  local alt
  sicherung_staende | tail -n +"$((SICHERUNG_BEHALTEN + 1))" | while IFS= read -r alt; do
    rm -f -- "$alt" && echo "Entfernt (älter als die $SICHERUNG_BEHALTEN neuesten): $(basename "$alt")"
  done
}

# Ein Lauf. Anlass regelmaessig (cron) oder vor-ausrollen (./wetter deploy vor dem Neustart).
sicherung_lauf() (
  set -euo pipefail
  umask 077
  local anlass="${1:-regelmaessig}" einheit_s einheit_name schwelle juengste
  case "$anlass" in
    regelmaessig) einheit_s=86400; einheit_name=Tage ;;
    vor-ausrollen) einheit_s=3600; einheit_name=Stunden ;;
    *) echo "Anlass unbekannt: $anlass (regelmaessig oder vor-ausrollen)" >&2; exit 2 ;;
  esac
  sicherung_werte_laden
  if [ "$anlass" = regelmaessig ]; then schwelle="$SICHERUNG_ABSTAND_TAGE"; else schwelle="$SICHERUNG_VOR_AUSROLLEN_AB_STUNDEN"; fi
  mkdir -p "$SICHERUNG_ORDNER"
  juengste="$(sicherung_staende | sed -n 1p)"
  if [ -n "$juengste" ] && [ "$(sicherung_alter "$juengste" "$einheit_s")" -lt "$schwelle" ]; then
    echo "Sicherung nicht fällig: die jüngste ($(basename "$juengste")) ist jünger als $schwelle $einheit_name"
  else
    sicherung_anlegen "$juengste"
  fi
  sicherung_aufraeumen
)
