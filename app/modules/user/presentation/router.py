from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.exceptions import AppException
from app.core.responses import ResponseBuilder
from app.core.security import require_super_admin
from app.core.security.hashing import PasswordHasher
from app.modules.customer.infrastructure.model import CustomerModel
from app.modules.gift.infrastructure.model import GiftRedemptionModel, GiftTypeModel
from app.modules.purchase.infrastructure.model import PurchaseModel
from app.modules.Permission.infrastructure.model import PermissionModel
from app.modules.role.infrastructure.model import RoleModel
from app.modules.role_permission.infrastructure.model import RolePermissionModel
from app.modules.settings.infrastructure.model import UserSettingsModel
from app.modules.subscription.infrastructure.model import SubscriptionModel
from app.modules.user.domain.entity import User
from app.modules.user.infrastructure.model import UserModel
from app.modules.user_role.infrastructure.model import UserRoleModel
from app.shared.access import days_remaining, subscription_is_active
from app.shared.tenancy import ADMIN_ROLE, SUPER_ADMIN_ROLE

router = APIRouter(prefix="/users", tags=["Users"])


class CreateAdminPayload(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    full_name: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    duration_days: int = Field(default=30, ge=1, le=3650)
    notes: str | None = Field(default=None, max_length=500)


class UpdateAdminPayload(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=5, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool = True
    password: str | None = Field(default=None, min_length=8, max_length=128)


class SubscriptionView(BaseModel):
    id: UUID
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    days_remaining: int
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ManagedUserView(BaseModel):
    id: UUID
    username: str
    full_name: str
    email: str
    phone: str | None = None
    is_active: bool
    roles: list[str]
    cafe_name: str | None = None
    system_password: str | None = None
    customers_count: int = 0
    subscription: SubscriptionView | None = None

    model_config = ConfigDict(from_attributes=True)


class ManagedUserListView(BaseModel):
    items: list[ManagedUserView]
    total: int
    active_subscriptions: int
    expired_subscriptions: int
    expiring_soon: int


class TenantStatsView(BaseModel):
    customers_count: int
    customers_inactive: int
    purchases_count: int
    purchases_today: int
    sales_total: Decimal
    sales_today: Decimal
    gifts_count: int
    gifts_pending: int
    gifts_delivered: int
    gift_types_count: int
    last_activity_at: datetime | None = None


class TenantSettingsView(BaseModel):
    cafe_name: str | None = None
    currency: str = "د.ع"
    visit_reward_target: int = 10
    points_reward_target: int = 100
    currency_per_point: Decimal = Decimal("1000")


class OverviewCustomerView(BaseModel):
    id: UUID
    name: str
    phone: str
    points: int
    visit_count: int
    total_spent: Decimal
    created_at: datetime


class OverviewActivityView(BaseModel):
    id: UUID
    type: str
    title: str
    subtitle: str
    occurred_at: datetime
    customer_id: UUID | None = None
    customer_name: str | None = None


class ManagedUserOverview(BaseModel):
    user: ManagedUserView
    stats: TenantStatsView
    settings: TenantSettingsView
    top_customers: list[OverviewCustomerView]
    recent_customers: list[OverviewCustomerView]
    recent_activity: list[OverviewActivityView]


def _to_subscription_view(model: SubscriptionModel | None, now: datetime) -> SubscriptionView | None:
    if model is None:
        return None
    remaining = days_remaining(model.ends_at, now)
    return SubscriptionView(
        id=model.id,
        starts_at=model.starts_at,
        ends_at=model.ends_at,
        is_active=subscription_is_active(model.starts_at, model.ends_at, now),
        days_remaining=remaining,
        notes=model.notes,
    )


ADMIN_PERMISSION_PREFIXES = ("customers.", "purchases.", "gift_types.", "gifts.")


async def _admin_role(session: AsyncSession) -> RoleModel:
    result = await session.execute(select(RoleModel).where(RoleModel.name == ADMIN_ROLE))
    role = result.scalar_one_or_none()
    if role is None:
        role = RoleModel(
            id=uuid4(),
            name=ADMIN_ROLE,
            description="Cafe tenant administrator",
            is_active=True,
        )
        session.add(role)
        await session.flush()

    permissions = (
        await session.execute(
            select(PermissionModel).where(
                or_(*(PermissionModel.name.like(f"{prefix}%") for prefix in ADMIN_PERMISSION_PREFIXES))
            )
        )
    ).scalars().all()
    existing_ids = set(
        (
            await session.execute(
                select(RolePermissionModel.permission_id).where(RolePermissionModel.role_id == role.id)
            )
        ).scalars().all()
    )
    for perm in permissions:
        if perm.id not in existing_ids:
            session.add(
                RolePermissionModel(id=uuid4(), role_id=role.id, permission_id=perm.id)
            )
    await session.flush()
    return role


async def _user_roles(session: AsyncSession, user_id: UUID) -> list[str]:
    return list(
        (
            await session.execute(
                select(RoleModel.name)
                .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
                .where(UserRoleModel.user_id == user_id, RoleModel.is_active.is_(True))
            )
        ).scalars().all()
    )


async def _latest_subscription(session: AsyncSession, user_id: UUID) -> SubscriptionModel | None:
    return (
        await session.execute(
            select(SubscriptionModel)
            .where(SubscriptionModel.user_id == user_id)
            .order_by(SubscriptionModel.ends_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()


def _managed_user_view(
    user: UserModel,
    *,
    roles: list[str],
    cafe_name: str | None,
    subscription: SubscriptionModel | None,
    now: datetime,
    customers_count: int = 0,
) -> ManagedUserView:
    return ManagedUserView(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        roles=roles,
        cafe_name=cafe_name,
        system_password=user.system_password,
        customers_count=customers_count,
        subscription=_to_subscription_view(subscription, now),
    )


@router.get("")
async def list_managed_users(
    search: str | None = Query(default=None, max_length=100),
    _: User = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    stmt = (
        select(UserModel)
        .options(selectinload(UserModel.user_roles).selectinload(UserRoleModel.role))
        .order_by(UserModel.full_name.asc())
    )
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            (UserModel.username.ilike(term))
            | (UserModel.full_name.ilike(term))
            | (UserModel.email.ilike(term))
        )

    users = (await session.execute(stmt)).scalars().unique().all()
    settings_rows = (await session.execute(select(UserSettingsModel))).scalars().all()
    cafe_by_user = {row.user_id: row.cafe_name for row in settings_rows}
    customer_counts = dict(
        (
            await session.execute(
                select(CustomerModel.owner_id, func.count())
                .where(CustomerModel.is_active.is_(True))
                .group_by(CustomerModel.owner_id)
            )
        ).all()
    )

    items: list[ManagedUserView] = []
    active_count = 0
    expired_count = 0
    expiring_soon = 0

    for user in users:
        roles = [link.role.name for link in user.user_roles if link.role and link.role.is_active]
        if SUPER_ADMIN_ROLE in roles:
            continue
        latest = (
            await session.execute(
                select(SubscriptionModel)
                .where(SubscriptionModel.user_id == user.id)
                .order_by(SubscriptionModel.ends_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        sub_view = _to_subscription_view(latest, now)
        if sub_view and sub_view.is_active:
            active_count += 1
            if sub_view.days_remaining <= 7:
                expiring_soon += 1
        else:
            expired_count += 1
        items.append(
            _managed_user_view(
                user,
                roles=roles,
                cafe_name=cafe_by_user.get(user.id) or None,
                subscription=latest,
                now=now,
                customers_count=int(customer_counts.get(user.id, 0)),
            )
        )

    return ResponseBuilder.success(
        data=ManagedUserListView(
            items=items,
            total=len(items),
            active_subscriptions=active_count,
            expired_subscriptions=expired_count,
            expiring_soon=expiring_soon,
        )
    )


@router.post("")
async def create_admin_user(
    payload: CreateAdminPayload,
    current_user: User = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session),
):
    username = payload.username.strip().lower()
    email = str(payload.email).strip().lower()

    existing_username = await session.execute(select(UserModel).where(UserModel.username == username))
    if existing_username.scalar_one_or_none() is not None:
        raise AppException(
            message="Username already exists.",
            status_code=status.HTTP_409_CONFLICT,
            errors=["USERNAME_EXISTS"],
        )
    existing_email = await session.execute(select(UserModel).where(UserModel.email == email))
    if existing_email.scalar_one_or_none() is not None:
        raise AppException(
            message="Email already exists.",
            status_code=status.HTTP_409_CONFLICT,
            errors=["EMAIL_EXISTS"],
        )

    role = await _admin_role(session)
    now = datetime.now(timezone.utc)
    user = UserModel(
        id=uuid4(),
        username=username,
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=PasswordHasher.hash(payload.password),
        system_password=payload.password,
        phone=payload.phone.strip() if payload.phone else None,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    session.add(UserRoleModel(id=uuid4(), user_id=user.id, role_id=role.id))
    session.add(
        UserSettingsModel(
            id=uuid4(),
            user_id=user.id,
            cafe_name=payload.full_name.strip(),
        )
    )
    subscription = SubscriptionModel(
        id=uuid4(),
        user_id=user.id,
        starts_at=now,
        ends_at=now + timedelta(days=payload.duration_days),
        notes=payload.notes.strip() if payload.notes else "حجز أولي",
        created_by=current_user.id,
        created_at=now,
        updated_at=now,
    )
    session.add(subscription)
    await session.commit()
    await session.refresh(user)

    return ResponseBuilder.created(
        data=ManagedUserView(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            roles=[ADMIN_ROLE],
            cafe_name=payload.full_name.strip(),
            system_password=payload.password,
            customers_count=0,
            subscription=_to_subscription_view(subscription, now),
        ),
        message="Admin user created.",
    )


@router.get("/{user_id}")
async def get_managed_user_overview(
    user_id: UUID,
    _: User = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(UserModel, user_id)
    if user is None:
        raise AppException("User not found.", status_code=status.HTTP_404_NOT_FOUND, errors=["USER_NOT_FOUND"])

    roles = await _user_roles(session, user.id)
    if SUPER_ADMIN_ROLE in roles:
        raise AppException(
            message="Cannot inspect the super admin from this panel.",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=["SUPER_ADMIN_LOCKED"],
        )

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    settings = (
        await session.execute(select(UserSettingsModel).where(UserSettingsModel.user_id == user.id))
    ).scalar_one_or_none()
    latest = await _latest_subscription(session, user.id)

    customers_count = int(
        await session.scalar(
            select(func.count()).select_from(CustomerModel).where(
                CustomerModel.owner_id == user.id,
                CustomerModel.is_active.is_(True),
            )
        )
        or 0
    )
    customers_inactive = int(
        await session.scalar(
            select(func.count()).select_from(CustomerModel).where(
                CustomerModel.owner_id == user.id,
                CustomerModel.is_active.is_(False),
            )
        )
        or 0
    )
    gift_types_count = int(
        await session.scalar(
            select(func.count()).select_from(GiftTypeModel).where(
                GiftTypeModel.owner_id == user.id,
                GiftTypeModel.is_active.is_(True),
            )
        )
        or 0
    )

    purchase_base = (
        select(PurchaseModel)
        .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
        .where(CustomerModel.owner_id == user.id)
    )
    purchases_count = int(
        await session.scalar(select(func.count()).select_from(purchase_base.subquery())) or 0
    )
    sales_total = Decimal(
        str(
            await session.scalar(
                select(func.coalesce(func.sum(PurchaseModel.amount), 0))
                .select_from(PurchaseModel)
                .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
                .where(CustomerModel.owner_id == user.id)
            )
            or 0
        )
    )
    purchases_today = int(
        await session.scalar(
            select(func.count())
            .select_from(PurchaseModel)
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
            .where(CustomerModel.owner_id == user.id, PurchaseModel.created_at >= today_start)
        )
        or 0
    )
    sales_today = Decimal(
        str(
            await session.scalar(
                select(func.coalesce(func.sum(PurchaseModel.amount), 0))
                .select_from(PurchaseModel)
                .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
                .where(CustomerModel.owner_id == user.id, PurchaseModel.created_at >= today_start)
            )
            or 0
        )
    )

    gift_base = (
        GiftRedemptionModel.customer_id == CustomerModel.id,
        CustomerModel.owner_id == user.id,
        GiftRedemptionModel.status != "cancelled",
    )
    gifts_count = int(
        await session.scalar(
            select(func.count())
            .select_from(GiftRedemptionModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
            .where(*gift_base)
        )
        or 0
    )
    gifts_pending = int(
        await session.scalar(
            select(func.count())
            .select_from(GiftRedemptionModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
            .where(*gift_base, GiftRedemptionModel.status == "pending")
        )
        or 0
    )
    gifts_delivered = int(
        await session.scalar(
            select(func.count())
            .select_from(GiftRedemptionModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
            .where(*gift_base, GiftRedemptionModel.status == "delivered")
        )
        or 0
    )

    last_purchase_at = await session.scalar(
        select(func.max(PurchaseModel.created_at))
        .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
        .where(CustomerModel.owner_id == user.id)
    )
    last_gift_at = await session.scalar(
        select(func.max(GiftRedemptionModel.created_at))
        .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
        .where(CustomerModel.owner_id == user.id, GiftRedemptionModel.status != "cancelled")
    )
    last_customer_at = await session.scalar(
        select(func.max(CustomerModel.created_at)).where(CustomerModel.owner_id == user.id)
    )
    activity_times = [item for item in (last_purchase_at, last_gift_at, last_customer_at) if item is not None]
    last_activity_at = max(activity_times) if activity_times else None

    top_rows = (
        await session.execute(
            select(CustomerModel)
            .where(CustomerModel.owner_id == user.id, CustomerModel.is_active.is_(True))
            .order_by(CustomerModel.total_spent.desc(), CustomerModel.visit_count.desc())
            .limit(5)
        )
    ).scalars().all()
    recent_customer_rows = (
        await session.execute(
            select(CustomerModel)
            .where(CustomerModel.owner_id == user.id, CustomerModel.is_active.is_(True))
            .order_by(CustomerModel.created_at.desc())
            .limit(5)
        )
    ).scalars().all()

    recent_purchases = (
        await session.execute(
            select(PurchaseModel, CustomerModel)
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
            .where(CustomerModel.owner_id == user.id)
            .order_by(PurchaseModel.created_at.desc())
            .limit(8)
        )
    ).all()
    recent_gifts = (
        await session.execute(
            select(GiftRedemptionModel, CustomerModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
            .where(CustomerModel.owner_id == user.id, GiftRedemptionModel.status != "cancelled")
            .order_by(GiftRedemptionModel.created_at.desc())
            .limit(8)
        )
    ).all()

    currency = settings.currency if settings else "د.ع"
    activity: list[OverviewActivityView] = []
    for purchase, customer in recent_purchases:
        activity.append(
            OverviewActivityView(
                id=purchase.id,
                type="purchase",
                title="مشترى",
                subtitle=f"{purchase.amount} {currency}",
                occurred_at=purchase.created_at,
                customer_id=customer.id,
                customer_name=customer.name,
            )
        )
    for gift, customer in recent_gifts:
        status_label = "معلّقة" if gift.status == "pending" else "مُسلّمة"
        activity.append(
            OverviewActivityView(
                id=gift.id,
                type="gift",
                title=f"هدية {status_label}",
                subtitle=gift.gift_type_name,
                occurred_at=gift.created_at,
                customer_id=customer.id,
                customer_name=customer.name,
            )
        )
    activity.sort(key=lambda item: item.occurred_at, reverse=True)
    activity = activity[:10]

    def _customer_view(row: CustomerModel) -> OverviewCustomerView:
        return OverviewCustomerView(
            id=row.id,
            name=row.name,
            phone=row.phone,
            points=row.points,
            visit_count=row.visit_count,
            total_spent=row.total_spent,
            created_at=row.created_at,
        )

    return ResponseBuilder.success(
        data=ManagedUserOverview(
            user=_managed_user_view(
                user,
                roles=roles,
                cafe_name=settings.cafe_name if settings and settings.cafe_name else None,
                subscription=latest,
                now=now,
                customers_count=customers_count,
            ),
            stats=TenantStatsView(
                customers_count=customers_count,
                customers_inactive=customers_inactive,
                purchases_count=purchases_count,
                purchases_today=purchases_today,
                sales_total=sales_total,
                sales_today=sales_today,
                gifts_count=gifts_count,
                gifts_pending=gifts_pending,
                gifts_delivered=gifts_delivered,
                gift_types_count=gift_types_count,
                last_activity_at=last_activity_at,
            ),
            settings=TenantSettingsView(
                cafe_name=settings.cafe_name if settings else None,
                currency=currency,
                visit_reward_target=settings.visit_reward_target if settings else 10,
                points_reward_target=settings.points_reward_target if settings else 100,
                currency_per_point=settings.currency_per_point if settings else Decimal("1000"),
            ),
            top_customers=[_customer_view(row) for row in top_rows],
            recent_customers=[_customer_view(row) for row in recent_customer_rows],
            recent_activity=activity,
        )
    )


@router.put("/{user_id}")
async def update_admin_user(
    user_id: UUID,
    payload: UpdateAdminPayload,
    _: User = Depends(require_super_admin),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(UserModel, user_id)
    if user is None:
        raise AppException("User not found.", status_code=status.HTTP_404_NOT_FOUND, errors=["USER_NOT_FOUND"])

    roles = (
        await session.execute(
            select(RoleModel.name)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
            .where(UserRoleModel.user_id == user.id)
        )
    ).scalars().all()
    if SUPER_ADMIN_ROLE in roles:
        raise AppException(
            message="Cannot modify the super admin from this panel.",
            status_code=status.HTTP_403_FORBIDDEN,
            errors=["SUPER_ADMIN_LOCKED"],
        )

    email = str(payload.email).strip().lower()
    conflict = await session.execute(
        select(UserModel).where(UserModel.email == email, UserModel.id != user.id)
    )
    if conflict.scalar_one_or_none() is not None:
        raise AppException(
            message="Email already exists.",
            status_code=status.HTTP_409_CONFLICT,
            errors=["EMAIL_EXISTS"],
        )

    user.full_name = payload.full_name.strip()
    user.email = email
    user.phone = payload.phone.strip() if payload.phone else None
    user.is_active = payload.is_active
    if payload.password:
        user.password_hash = PasswordHasher.hash(payload.password)
        user.system_password = payload.password
    await session.commit()

    now = datetime.now(timezone.utc)
    latest = (
        await session.execute(
            select(SubscriptionModel)
            .where(SubscriptionModel.user_id == user.id)
            .order_by(SubscriptionModel.ends_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    settings = (
        await session.execute(select(UserSettingsModel).where(UserSettingsModel.user_id == user.id))
    ).scalar_one_or_none()
    customers_count = int(
        await session.scalar(
            select(func.count()).select_from(CustomerModel).where(
                CustomerModel.owner_id == user.id,
                CustomerModel.is_active.is_(True),
            )
        )
        or 0
    )
    return ResponseBuilder.success(
        data=_managed_user_view(
            user,
            roles=list(roles),
            cafe_name=settings.cafe_name if settings and settings.cafe_name else None,
            subscription=latest,
            now=now,
            customers_count=customers_count,
        ),
        message="User updated.",
    )
