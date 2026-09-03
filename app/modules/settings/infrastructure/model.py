from datetime import datetime
from decimal import Decimal
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserSettingsModel(Base):
    __tablename__ = "user_settings"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    cafe_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    logo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    currency: Mapped[str] = mapped_column(String(50), nullable=False, default="د.ع")

    visit_reward_target: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    points_reward_target: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    currency_per_point: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("1000"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
