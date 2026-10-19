"""Alle Zeitspalten mit Zeitzone, Messwerte eindeutig und mit Verbundindex.

Vorher wurden naive Zeitstempel in drei verschiedenen Zeitbasen geschrieben:

- Nachtrag beim ersten Start (nur Temperatur, volle Stunden) in Berliner Ortszeit,
- laufende Messwerte und Klima-Stände per datetime.now() in der Zeitzone des Prozesses
  (im Container UTC, am Entwicklungsrechner Berlin),
- Radar-Archiv in UTC.

Jede Gruppe wird mit ihrer eigenen Zeitbasis umgerechnet. Der Nachtrag hatte außerdem die
Vorhersage der restlichen Stunden des Starttags als Messwert gespeichert; diese Zeilen liegen
nach dem ersten echten Messwert und werden gelöscht. Doppelte Messwerte (gleicher Ort, gleiche
Größe, gleiche Zeit) werden auf einen zusammengelegt, danach erzwingt ein eindeutiger
Verbundindex das."""

from alembic import op

from wetterwarte.zeit import prozess_zone

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    lokal = prozess_zone().replace("'", "")

    # Nachtrag erkennen: Temperatur zur vollen Stunde ohne gleichzeitige andere Größe.
    op.execute("ALTER TABLE messwert ADD COLUMN nachtrag boolean NOT NULL DEFAULT false")
    op.execute(
        """
        UPDATE messwert m SET nachtrag = true
        WHERE m.variable = 'temperatur'
          AND m.zeit = date_trunc('hour', m.zeit)
          AND NOT EXISTS (
            SELECT 1 FROM messwert a
            WHERE a.ort = m.ort AND a.zeit = m.zeit AND a.variable <> 'temperatur'
          )
        """
    )
    op.execute(
        f"""
        ALTER TABLE messwert ALTER COLUMN zeit TYPE timestamptz USING (
          CASE WHEN nachtrag THEN zeit AT TIME ZONE 'Europe/Berlin' ELSE zeit AT TIME ZONE '{lokal}' END
        )
        """
    )
    # Vorhersagewerte aus dem Nachtrag: alles nach dem ersten echten Messwert.
    op.execute(
        """
        DELETE FROM messwert
        WHERE nachtrag
          AND zeit > (SELECT min(zeit) FROM messwert WHERE NOT nachtrag)
        """
    )
    op.execute("ALTER TABLE messwert DROP COLUMN nachtrag")

    # Doppelte zusammenlegen, dann eindeutig und mit Verbundindex.
    op.execute(
        """
        DELETE FROM messwert a USING messwert b
        WHERE a.ort = b.ort AND a.variable = b.variable AND a.zeit = b.zeit AND a.id > b.id
        """
    )
    op.drop_index("ix_messwert_ort", table_name="messwert")
    op.drop_index("ix_messwert_variable", table_name="messwert")
    op.create_index("uq_messwert_ort_variable_zeit", "messwert", ["ort", "variable", "zeit"], unique=True)

    # Klima-Stände wurden in der Zeitzone des Prozesses geschrieben.
    for tabelle in ("klimanormale", "klimaaggregat"):
        op.execute(f"ALTER TABLE {tabelle} ALTER COLUMN stand TYPE timestamptz USING (stand AT TIME ZONE '{lokal}')")
    # Der eindeutige Verbund (ort, variable, jahr, monat) deckt alle Abfragen ab.
    for index in ("ix_klimaaggregat_jahr", "ix_klimaaggregat_ort", "ix_klimaaggregat_variable"):
        op.drop_index(index, table_name="klimaaggregat")

    # Radar-Archiv war schon UTC.
    for spalte in ("zeit", "angelegt"):
        op.execute(f"ALTER TABLE radararchivframe ALTER COLUMN {spalte} TYPE timestamptz USING ({spalte} AT TIME ZONE 'UTC')")


def downgrade() -> None:
    raise NotImplementedError("Die Umstellung auf Zeitzonen wird nicht zurückgedreht.")
