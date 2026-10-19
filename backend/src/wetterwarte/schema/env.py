"""Alembic-Umgebung: läuft nur mit einer übergebenen Verbindung (siehe schema/__init__.py)."""

from alembic import context
from sqlmodel import SQLModel

from wetterwarte import models  # noqa: F401 - alle Tabellen registrieren (für spätere Vergleiche)

verbindung = context.config.attributes.get("verbindung")
if verbindung is None:
    raise RuntimeError("Migrationen laufen nur über wetterwarte.schema.aktualisiere()")

context.configure(connection=verbindung, target_metadata=SQLModel.metadata, compare_type=True)
with context.begin_transaction():
    context.run_migrations()
