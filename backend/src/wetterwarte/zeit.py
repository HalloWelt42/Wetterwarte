"""Zeit an genau einer Stelle: in der Datenbank immer UTC mit Zeitzone, in der Anzeige die
Zeitzone des Orts. Naive Zeitstempel kommen im Backend nicht mehr vor."""

import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

STANDARD_ZONE = "Europe/Berlin"


def jetzt() -> datetime:
    """Aktueller Zeitpunkt in UTC (mit Zeitzone)."""
    return datetime.now(UTC)


def zone(name: str | None) -> ZoneInfo:
    """IANA-Zeitzone eines Orts; leere oder unbekannte Namen fallen auf Berlin zurück."""
    try:
        return ZoneInfo(name or STANDARD_ZONE)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo(STANDARD_ZONE)


def lokal(text: str, zeitzone: str | None) -> datetime:
    """Ortszeit ohne Versatz (wie Open-Meteo sie mit timezone=auto liefert) als Zeitpunkt mit Zone."""
    wert = datetime.fromisoformat(text)
    return wert if wert.tzinfo else wert.replace(tzinfo=zone(zeitzone))


def prozess_zone() -> str:
    """Zeitzone, in der dieser Prozess naive Zeitstempel geschrieben hat (nur für die Migration
    alter Daten): TZ, sonst das Ziel von /etc/localtime, sonst UTC."""
    if os.environ.get("TZ"):
        return os.environ["TZ"]
    try:
        ziel = os.path.realpath("/etc/localtime")
    except OSError:
        return "UTC"
    return ziel.split("zoneinfo/", 1)[1] if "zoneinfo/" in ziel else "UTC"
