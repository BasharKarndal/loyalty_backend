from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.modules.settings.application.dto.settings_dto import UserSettingsDto
from app.modules.settings.domain.entity import UserSettings
from app.modules.settings.infrastructure.repository import SqlAlchemyUserSettingsRepository
from app.shared.loyalty.service import (
    DEFAULT_CURRENCY_PER_POINT,
    DEFAULT_POINTS_REWARD_TARGET,
    DEFAULT_VISIT_REWARD_TARGET,
)


class UserSettingsService:
    """Loads or creates per-user settings and maps to DTO."""

    def __init__(self, repository: SqlAlchemyUserSettingsRepository):
        self.repository = repository

    async def get_or_create(self, user_id: UUID) -> UserSettings:
        settings = await self.repository.get_by_user_id(user_id)
        if settings is not None:
            return settings

        now = datetime.now(timezone.utc)
        settings = UserSettings(
            id=uuid4(),
            user_id=user_id,
            cafe_name="",
            logo_path=None,
            currency="د.ع",
            visit_reward_target=DEFAULT_VISIT_REWARD_TARGET,
            points_reward_target=DEFAULT_POINTS_REWARD_TARGET,
            currency_per_point=Decimal(str(DEFAULT_CURRENCY_PER_POINT)),
            created_at=now,
            updated_at=now,
        )
        await self.repository.add(settings)
        return settings

    @staticmethod
    def to_dto(settings: UserSettings) -> UserSettingsDto:
        logo_url = None
        if settings.logo_path:
            ts = int(settings.updated_at.timestamp())
            logo_url = f"/api/v1/settings/me/logo?v={ts}"
        return UserSettingsDto(
            id=settings.id,
            user_id=settings.user_id,
            cafe_name=settings.cafe_name,
            logo_url=logo_url,
            currency=settings.currency,
            visit_reward_target=settings.visit_reward_target,
            points_reward_target=settings.points_reward_target,
            currency_per_point=settings.currency_per_point,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
        )
