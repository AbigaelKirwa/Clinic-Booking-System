"""add cancellation_reason to appointment

Revision ID: a1b2c3d4e5f6
Revises: d34516af8315
Create Date: 2026-07-16 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "d34516af8315"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointment",
        sa.Column("cancellation_reason", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("appointment", "cancellation_reason")
