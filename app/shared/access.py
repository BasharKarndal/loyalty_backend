from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.modules.role.infrastructure.model import RoleModel
from app.modules.subscription.infrastructure.model import SubscriptionModel
from app.modules.user.domain.entity import User
from app.modules.user_role.infrastructure.model import UserRoleModel
from app.shared.tenancy import SUPER_ADMIN_ROLE


async def get_role_names(session: AsyncSession, user_id: UUID) -> list[str]:
    result = await session.execute(
        select(RoleModel.name)
        .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
        .where(UserRoleModel.user_id == user_id, RoleModel.is_active.is_(True))
    )
    return [row[0] for row in result.all()]


async def is_super_admin(session: AsyncSession, user_id: UUID) -> bool:
    return SUPER_ADMIN_ROLE in await get_role_names(session, user_id)


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def subscription_is_active(starts_at: datetime, ends_at: datetime, now: datetime | None = None) -> bool:
    current = as_utc(now or datetime.now(timezone.utc))
    return as_utc(starts_at) <= current <= as_utc(ends_at)


def days_remaining(ends_at: datetime, now: datetime | None = None) -> int:
    current = as_utc(now or datetime.now(timezone.utc))
    delta = as_utc(ends_at) - current
    if delta.total_seconds() <= 0:
        return 0
    return delta.days


async def get_latest_subscription(session: AsyncSession, user_id: UUID) -> SubscriptionModel | None:
    result = await session.execute(
        select(SubscriptionModel)
        .where(SubscriptionModel.user_id == user_id)
        .order_by(SubscriptionModel.ends_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_active_subscription(session: AsyncSession, user_id: UUID) -> SubscriptionModel | None:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(SubscriptionModel)
        .where(
            SubscriptionModel.user_id == user_id,
            SubscriptionModel.starts_at <= now,
            SubscriptionModel.ends_at >= now,
        )
        .order_by(SubscriptionModel.ends_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def assert_workspace_access(session: AsyncSession, user: User) -> None:
    if await is_super_admin(session, user.id):
        return
    subscription = await get_active_subscription(session, user.id)
    if subscription is None:
        raise AppException(
            message="Subscription expired.",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=["SUBSCRIPTION_EXPIRED"],
        )
