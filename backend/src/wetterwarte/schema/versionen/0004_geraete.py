"""Geräte für aktive Warnungen: Einstellungen und Push-Abo, Gedächtnis je Kanal und Ort, Protokoll (docs/WARNUNGEN.md)."""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "geraet",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("einstellungen", sa.JSON(), nullable=False),
        sa.Column("push_endpunkt", sa.String(), nullable=True),
        sa.Column("push_p256dh", sa.String(), nullable=True),
        sa.Column("push_auth", sa.String(), nullable=True),
        sa.Column("erstellt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gesehen", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "meldegedaechtnis",
        sa.Column("geraet_id", sa.String(), sa.ForeignKey("geraet.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("kanal", sa.String(), primary_key=True),
        sa.Column("ort", sa.String(), primary_key=True),
        sa.Column("eintraege", sa.JSON(), nullable=False),
        sa.Column("aktualisiert", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "meldung",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("geraet_id", sa.String(), sa.ForeignKey("geraet.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kanal", sa.String(), nullable=False),
        sa.Column("ort", sa.String(), nullable=False),
        sa.Column("art", sa.String(), nullable=False),
        sa.Column("schluessel", sa.String(), nullable=False),
        sa.Column("stufe", sa.Integer(), nullable=False),
        sa.Column("titel", sa.String(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("zeit", sa.DateTime(timezone=True), nullable=False),
        sa.Column("zugestellt", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_meldung_geraet_id", "meldung", ["geraet_id"])
    op.create_index("ix_meldung_zeit", "meldung", ["zeit"])


def downgrade() -> None:
    op.drop_table("meldung")
    op.drop_table("meldegedaechtnis")
    op.drop_table("geraet")
