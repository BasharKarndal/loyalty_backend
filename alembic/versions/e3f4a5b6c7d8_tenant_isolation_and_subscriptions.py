"""tenant isolation + subscriptions

Revision ID: e3f4a5b6c7d8
Revises: e2f3a4b5c6d7
Create Date: 2026-09-03 10:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e3f4a5b6c7d8"
down_revision: Union[str, Sequence[str], None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("gift_types", sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True))

    op.execute(
        """
        UPDATE customers
        SET owner_id = (SELECT id FROM users ORDER BY username ASC LIMIT 1)
        WHERE owner_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE gift_types
        SET owner_id = (SELECT id FROM users ORDER BY username ASC LIMIT 1)
        WHERE owner_id IS NULL
        """
    )

    op.alter_column("customers", "owner_id", nullable=False)
    op.alter_column("gift_types", "owner_id", nullable=False)

    op.create_foreign_key(
        "fk_customers_owner_id_users",
        "customers",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_gift_types_owner_id_users",
        "gift_types",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_customers_owner_id", "customers", ["owner_id"])
    op.create_index("ix_gift_types_owner_id", "gift_types", ["owner_id"])

    op.drop_index("uq_customers_phone_active", table_name="customers")
    op.create_index(
        "uq_customers_owner_phone_active",
        "customers",
        ["owner_id", "phone"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_ends_at", "subscriptions", ["ends_at"])


def downgrade() -> None:
    op.drop_index("ix_subscriptions_ends_at", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("uq_customers_owner_phone_active", table_name="customers")
    op.create_index(
        "uq_customers_phone_active",
        "customers",
        ["phone"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )
    op.drop_index("ix_gift_types_owner_id", table_name="gift_types")
    op.drop_index("ix_customers_owner_id", table_name="customers")
    op.drop_constraint("fk_gift_types_owner_id_users", "gift_types", type_="foreignkey")
    op.drop_constraint("fk_customers_owner_id_users", "customers", type_="foreignkey")
    op.drop_column("gift_types", "owner_id")
    op.drop_column("customers", "owner_id")
