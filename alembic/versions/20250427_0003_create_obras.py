"""Create obras table.

Revision ID: 0003
Revises: 0002
Create Date: 2025-04-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "obras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("direccion", sa.String(length=300), nullable=False, server_default=""),
        sa.Column("provincia_id", sa.Integer(), nullable=True),
        sa.Column("superficie_m2", sa.Float(), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin_estimada", sa.Date(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="borrador"),
        sa.Column("presupuesto_inicial", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_obras_usuario_id", "obras", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_obras_usuario_id", table_name="obras")
    op.drop_table("obras")
