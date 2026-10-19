"""Alle Tabellen; der Import registriert sie in SQLModel.metadata."""

from .aufzeichnung import AufzeichnungOrt
from .einstellung import Einstellung
from .geraet import Geraet, Meldegedaechtnis, Meldung
from .klima import KlimaNormale
from .klima_aggregat import KlimaAggregat
from .layout import Layout
from .messwert import Messwert
from .ort import Ort
from .radar_archiv import RadarArchivFrame

__all__ = ["AufzeichnungOrt", "Einstellung", "Geraet", "Meldegedaechtnis", "Meldung", "KlimaAggregat", "KlimaNormale", "Layout", "Messwert", "Ort", "RadarArchivFrame"]
