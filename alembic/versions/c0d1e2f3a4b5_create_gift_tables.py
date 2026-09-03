"""create gift_types and gift_redemptions tables

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-09-02 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c0d1e2f3a4b5"
down_revision: Union[str, Sequence[str], None] = "b9c0d1e2f3a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gift_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("icon_key", sa.String(length=100), server_default="card_giftcard", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_gift_types")),
    )
    op.create_index("ix_gift_types_is_active", "gift_types", ["is_active"], unique=False)
    op.create_index("ix_gift_types_sort_order", "gift_types", ["sort_order"], unique=False)

    op.create_table(
        "gift_redemptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("gift_type_id", sa.UUID(), nullable=True),
        sa.Column("gift_type_name", sa.String(length=255), nullable=False),
        sa.Column("gift_type_icon", sa.String(length=100), server_default="card_giftcard", nullable=False),
        sa.Column("points_used", sa.Integer(), nullable=False),
        sa.Column("reward_track", sa.String(length=20), server_default="amount", nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name=op.f("fk_gift_redemptions_customer_id_customers"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["gift_type_id"],
            ["gift_types.id"],
            name=op.f("fk_gift_redemptions_gift_type_id_gift_types"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_gift_redemptions")),
    )
    op.create_index("ix_gift_redemptions_customer_id", "gift_redemptions", ["customer_id"], unique=False)
    op.create_index("ix_gift_redemptions_status", "gift_redemptions", ["status"], unique=False)
    op.create_index("ix_gift_redemptions_created_at", "gift_redemptions", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_gift_redemptions_created_at", table_name="gift_redemptions")
    op.drop_index("ix_gift_redemptions_status", table_name="gift_redemptions")
    op.drop_index("ix_gift_redemptions_customer_id", table_name="gift_redemptions")
    op.drop_table("gift_redemptions")
    op.drop_index("ix_gift_types_sort_order", table_name="gift_types")
    op.drop_index("ix_gift_types_is_active", table_name="gift_types")
    op.drop_table("gift_types")
