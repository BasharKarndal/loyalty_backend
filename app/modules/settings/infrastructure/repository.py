from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.settings.domain.entity import UserSettings
from app.modules.settings.domain.repository import UserSettingsRepository

from .mapper import UserSettingsMapper
from .model import UserSettingsModel


class SqlAlchemyUserSettingsRepository(UserSettingsRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, settings: UserSettings) -> None:
        self.session.add(UserSettingsMapper.to_model(settings))

    async def update(self, settings: UserSettings) -> None:
        model = await self.session.get(UserSettingsModel, settings.id)
        if model is None:
            return
        model.cafe_name = settings.cafe_name
        model.logo_path = settings.logo_path
        model.currency = settings.currency
        model.visit_reward_target = settings.visit_reward_target
        model.points_reward_target = settings.points_reward_target
        model.currency_per_point = settings.currency_per_point
        model.updated_at = settings.updated_at

    async def get_by_user_id(self, user_id: UUID) -> UserSettings | None:
        result = await self.session.execute(
            select(UserSettingsModel).where(UserSettingsModel.user_id == user_id).limit(1)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return UserSettingsMapper.to_domain(model)
