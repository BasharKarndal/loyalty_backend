"""add balance_deducted to gift_redemptions

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-09-03 09:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "gift_redemptions",
        sa.Column(
            "balance_deducted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    # Legacy pending gifts already deducted points/visits on create.
    op.execute(
        "UPDATE gift_redemptions SET balance_deducted = true WHERE status = 'pending'"
    )


def downgrade() -> None:
    op.drop_column("gift_redemptions", "balance_deducted")
