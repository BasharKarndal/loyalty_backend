from datetime import datetime, timezone

from app.core.exceptions import AppException
from app.modules.auth.application.dto.me_dto import MeDto, SubscriptionSummaryDto
from app.modules.auth.application.queries.get_me_query import GetMeQuery
from app.modules.user.domain.unit_of_work import UserUnitOfWork
from app.shared.access import days_remaining, get_active_subscription, get_latest_subscription
from app.shared.tenancy import SUPER_ADMIN_ROLE


class GetMeHandler:

    def __init__(self, uow: UserUnitOfWork, session):
        self.uow = uow
        self.session = session

    async def handle(self, query: GetMeQuery) -> MeDto:
        user = await self.uow.users.get_by_id(query.user_id)

        if user is None:
            raise AppException("User not found.", status_code=404)

        user_permissions = await self.uow.users.get_permissions(query.user_id)

        all_permissions = [
            perm.name
            for role in (user_permissions.roles if user_permissions else [])
            for perm in role.permissions
        ]
        role_names = [
            role.name for role in (user_permissions.roles if user_permissions else [])
        ]
        is_super = SUPER_ADMIN_ROLE in role_names

        subscription_dto = None
        if not is_super:
            now = datetime.now(timezone.utc)
            active = await get_active_subscription(self.session, user.id)
            current = active or await get_latest_subscription(self.session, user.id)
            if current is not None:
                remaining = days_remaining(current.ends_at, now)
                subscription_dto = SubscriptionSummaryDto(
                    id=current.id,
                    starts_at=current.starts_at,
                    ends_at=current.ends_at,
                    is_active=active is not None,
                    days_remaining=remaining,
                )

        return MeDto(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            national_id=user.national_id,
            is_active=user.is_active,
            permissions=all_permissions,
            roles=role_names,
            is_super_admin=is_super,
            subscription=subscription_dto,
        )
