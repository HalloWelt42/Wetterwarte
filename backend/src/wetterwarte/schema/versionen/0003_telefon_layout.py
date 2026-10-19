"""Telefon-Layout je Profil: eigene Kachelliste für die Telefonansicht (siehe docs/TELEFON.md)."""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("layout", sa.Column("telefon", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("layout", "telefon")
