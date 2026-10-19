"""Grundstand: das Schema, wie es vor der Einführung der Migrationen bestand.

Alte Datenbanken werden auf diesen Stand markiert, neue legen ihn hier an."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "aufzeichnungort",
        sa.Column("ort", sa.String(), primary_key=True),
        sa.Column("variablen", sa.String(), nullable=False),
        sa.Column("aktiv", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "einstellung",
        sa.Column("schluessel", sa.String(), primary_key=True),
        sa.Column("wert", sa.String(), nullable=False),
    )
    op.create_table(
        "klimaaggregat",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ort", sa.String(), nullable=False),
        sa.Column("variable", sa.String(), nullable=False),
        sa.Column("jahr", sa.Integer(), nullable=False),
        sa.Column("monat", sa.Integer(), nullable=False),
        sa.Column("mittel", sa.Float(), nullable=False),
        sa.Column("minimum", sa.Float(), nullable=False),
        sa.Column("maximum", sa.Float(), nullable=False),
        sa.Column("summe", sa.Float(), nullable=False),
        sa.Column("anzahl", sa.Integer(), nullable=False),
        sa.Column("stand", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("ort", "variable", "jahr", "monat", name="uq_klima_aggregat"),
    )
    op.create_index("ix_klimaaggregat_jahr", "klimaaggregat", ["jahr"])
    op.create_index("ix_klimaaggregat_ort", "klimaaggregat", ["ort"])
    op.create_index("ix_klimaaggregat_variable", "klimaaggregat", ["variable"])
    op.create_table(
        "klimanormale",
        sa.Column("ort", sa.String(), primary_key=True),
        sa.Column("daten", sa.String(), nullable=False),
        sa.Column("stand", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "layout",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("ist_standard", sa.Boolean(), nullable=False),
        sa.Column("daten", sa.JSON(), nullable=True),
        sa.Column("icon", sa.String(), nullable=False, server_default=""),
    )
    op.create_table(
        "messwert",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ort", sa.String(), nullable=False),
        sa.Column("zeit", sa.DateTime(), nullable=False),
        sa.Column("variable", sa.String(), nullable=False),
        sa.Column("wert", sa.Float(), nullable=False),
    )
    op.create_index("ix_messwert_ort", "messwert", ["ort"])
    op.create_index("ix_messwert_variable", "messwert", ["variable"])
    op.create_index("ix_messwert_zeit", "messwert", ["zeit"])
    op.create_table(
        "ort",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("land", sa.String(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("reihenfolge", sa.Integer(), nullable=False),
        sa.Column("ist_start", sa.Boolean(), nullable=False),
        sa.Column("zeitzone", sa.String(), nullable=True, server_default=""),
    )
    op.create_index("ix_ort_slug", "ort", ["slug"], unique=True)
    op.create_table(
        "radararchivframe",
        sa.Column("frame_id", sa.String(), primary_key=True),
        sa.Column("zeit", sa.DateTime(), nullable=False),
        sa.Column("png", sa.LargeBinary(), nullable=False),
        sa.Column("angelegt", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_radararchivframe_zeit", "radararchivframe", ["zeit"])


def downgrade() -> None:
    for tabelle in ("radararchivframe", "ort", "messwert", "layout", "klimanormale", "klimaaggregat", "einstellung", "aufzeichnungort"):
        op.drop_table(tabelle)
