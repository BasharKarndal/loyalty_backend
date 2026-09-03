from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.exceptions import AppException
from app.core.responses import ResponseBuilder
from app.core.security import require_super_admin
from app.modules.subscription.infrastructure.model import SubscriptionModel
from app.modules.user.domain.entity import User
from app.modules.user.infrastructure.model import UserModel
from app.modules.user_role.infrastructure.model import UserRoleModel
from app.shared.access import days_remaining, subscription_is_active
from app.shared.tenancy import SUPER_ADMIN_ROLE

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


class CreateSubscriptionPayload(BaseModel):
    user_id: UUID
    duration_days: int | None = Field(default=30, ge=1, le=3650)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)


class SubscriptionItem(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    username: str
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    days_remaining: int
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionList(BaseModel):
    items: list[SubscriptionItem]
    total: int
    active_count: int
    expired_count: int


def _item(model: SubscriptionModel, user: UserModel, now: datetime) -> SubscriptionItem:
    remaining = days_remaining(model.ends_at, now)
    return SubscriptionItem(
        id=model.id,
        user_id=model.user_id,
        user_name=user.full_name,
        username=user.username,
        starts_at=model.starts_at,
        ends_at=model.ends_at,
        is_active=subscription_is_active(model.starts_at, model.ends_at, now),
        days_remaining=remaining,
        notes=model.notes,
        created_at=model.created_at,
    )


@router.get("")
async def list_subscriptions(
    _: User = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(SubscriptionModel, UserModel)
        .join(UserModel, UserModel.id == SubscriptionModel.user_id)
        .order_by(SubscriptionModel.ends_at.desc())
    )
    items: list[SubscriptionItem] = []
    active_count = 0
    expired_count = 0
    for sub, user in result.all():
        view = _item(sub, user, now)
        items.append(view)
        if view.is_active:
            active_count += 1
        elif view.ends_at < now:
            expired_count += 1
    return ResponseBuilder.success(
        data=SubscriptionList(
            items=items,
            total=len(items),
            active_count=active_count,
            expired_count=expired_count,
        )
    )


@router.post("")
async def create_subscription(
    payload: CreateSubscriptionPayload,
    current_user: User = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(
        UserModel,
        payload.user_id,
        options=[selectinload(UserModel.user_roles).selectinload(UserRoleModel.role)],
    )
    if user is None:
        raise AppException("User not found.", status_code=status.HTTP_404_NOT_FOUND, errors=["USER_NOT_FOUND"])

    roles = [link.role.name for link in user.user_roles if link.role]
    if SUPER_ADMIN_ROLE in roles:
        raise AppException(
            message="Super admin does not require a subscription.",
            status_code=status.HTTP_409_CONFLICT,
            errors=["SUPER_ADMIN_NO_SUBSCRIPTION"],
        )

    now = datetime.now(timezone.utc)
    if payload.starts_at and payload.ends_at:
        starts = payload.starts_at
        ends = payload.ends_at
        if starts.tzinfo is None:
            starts = starts.replace(tzinfo=timezone.utc)
        if ends.tzinfo is None:
            ends = ends.replace(tzinfo=timezone.utc)
    else:
        latest = (
            await session.execute(
                select(SubscriptionModel)
                .where(SubscriptionModel.user_id == user.id)
                .order_by(SubscriptionModel.ends_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        starts = now
        if latest and subscription_is_active(latest.starts_at, latest.ends_at, now):
            starts = latest.ends_at
        days = payload.duration_days or 30
        ends = starts + timedelta(days=days)

    if ends <= starts:
        raise AppException(
            message="Invalid subscription range.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=["INVALID_RANGE"],
        )

    model = SubscriptionModel(
        id=uuid4(),
        user_id=user.id,
        starts_at=starts,
        ends_at=ends,
        notes=payload.notes.strip() if payload.notes else None,
        created_by=current_user.id,
        created_at=now,
        updated_at=now,
    )
    session.add(model)
    if not user.is_active:
        user.is_active = True
    await session.commit()
    await session.refresh(model)
    return ResponseBuilder.created(
        data=_item(model, user, now),
        message="Subscription created.",
    )
