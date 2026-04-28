"""Create gastos table.

Revision ID: 0004
Revises: 0003
Create Date: 2025-04-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "gastos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("obra_id", sa.Integer(), nullable=False),
        sa.Column("rubro_id", sa.Integer(), nullable=True),
        sa.Column("descripcion", sa.String(length=300), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("comprobante_url", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["obra_id"], ["obras.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rubro_id"], ["rubros.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gastos_obra_id", "gastos", ["obra_id"])


def downgrade() -> None:
    op.drop_index("ix_gastos_obra_id", table_name="gastos")
    op.drop_table("gastos")
