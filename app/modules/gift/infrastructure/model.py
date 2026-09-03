from datetime import datetime
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GiftTypeModel(Base):
    __tablename__ = "gift_types"
    __table_args__ = (
        Index("ix_gift_types_is_active", "is_active"),
        Index("ix_gift_types_sort_order", "sort_order"),
        Index("ix_gift_types_owner_id", "owner_id"),
    )

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon_key: Mapped[str] = mapped_column(String(100), nullable=False, default="card_giftcard")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class GiftRedemptionModel(Base):
    __tablename__ = "gift_redemptions"
    __table_args__ = (
        Index("ix_gift_redemptions_customer_id", "customer_id"),
        Index("ix_gift_redemptions_status", "status"),
        Index("ix_gift_redemptions_created_at", "created_at"),
    )

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False
    )
    gift_type_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gift_types.id", ondelete="SET NULL"), nullable=True
    )
    gift_type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gift_type_icon: Mapped[str] = mapped_column(String(100), nullable=False, default="card_giftcard")
    points_used: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_track: Mapped[str] = mapped_column(String(20), nullable=False, default="amount")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    balance_deducted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
