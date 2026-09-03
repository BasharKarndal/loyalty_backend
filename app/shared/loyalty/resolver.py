from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.settings.application.user_settings_service import UserSettingsService
from app.modules.settings.infrastructure.repository import SqlAlchemyUserSettingsRepository
from app.shared.loyalty.service import LoyaltyService


async def resolve_loyalty_service(session: AsyncSession, user_id: UUID) -> LoyaltyService:
    repo = SqlAlchemyUserSettingsRepository(session)
    service = UserSettingsService(repo)
    settings = await service.get_or_create(user_id)
    return LoyaltyService(
        currency_per_point=settings.currency_per_point,
        visit_reward_target=settings.visit_reward_target,
        points_reward_target=settings.points_reward_target,
    )
