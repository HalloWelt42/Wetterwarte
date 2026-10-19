"""Datenbankschema über Alembic-Migrationen (Ordner versionen/).

Läuft bei jedem Start vor allem anderen. Eine Datenbank aus der Zeit vor den Migrationen
(Tabellen da, aber keine alembic_version) wird zuerst auf den Grundstand gebracht und als
solcher markiert; danach laufen alle offenen Migrationen. Eine leere Datenbank durchläuft
einfach alle Migrationen von vorn."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.engine import Connection

GRUNDSTAND = "0001"

# Was der alte Start per Hand nachzog. Auf alten Datenbanken vor dem Markieren ausführen,
# damit sie dem Grundstand genau entsprechen.
_ALTE_NACHZUEGE = (
    "ALTER TABLE ort ADD COLUMN IF NOT EXISTS zeitzone VARCHAR DEFAULT ''",
    "ALTER TABLE layout ADD COLUMN IF NOT EXISTS icon VARCHAR NOT NULL DEFAULT ''",
)


def _konfiguration(verbindung: Connection) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(__file__).parent))
    cfg.set_main_option("version_locations", str(Path(__file__).parent / "versionen"))
    cfg.attributes["verbindung"] = verbindung
    return cfg


def aktualisiere(verbindung: Connection) -> None:
    """Schema auf den neuesten Stand bringen (synchron, innerhalb einer offenen Transaktion)."""
    cfg = _konfiguration(verbindung)
    tabellen = set(inspect(verbindung).get_table_names())
    if "alembic_version" not in tabellen and "layout" in tabellen:
        for sql in _ALTE_NACHZUEGE:
            verbindung.exec_driver_sql(sql)
        command.stamp(cfg, GRUNDSTAND)
    command.upgrade(cfg, "head")
