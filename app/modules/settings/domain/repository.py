from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.settings.domain.entity import UserSettings


class UserSettingsRepository(ABC):

    @abstractmethod
    async def add(self, settings: UserSettings) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, settings: UserSettings) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserSettings | None:
        raise NotImplementedError
