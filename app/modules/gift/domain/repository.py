from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.gift.domain.gift_redemption_entity import GiftRedemption
from app.modules.gift.domain.gift_type_entity import GiftType


class GiftTypeRepository(ABC):

    @abstractmethod
    async def add(self, gift_type: GiftType) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, gift_type: GiftType) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, gift_type_id: UUID) -> GiftType | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        active_only: bool | None = None,
    ) -> list[GiftType]:
        raise NotImplementedError


class GiftRedemptionRepository(ABC):

    @abstractmethod
    async def add(self, redemption: GiftRedemption) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, redemption: GiftRedemption) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, redemption_id: UUID) -> GiftRedemption | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        skip: int,
        limit: int,
        customer_id: UUID | None,
        status: str | None,
        exclude_cancelled: bool,
    ) -> tuple[list[GiftRedemption], int]:
        raise NotImplementedError

    @abstractmethod
    async def has_pending_for_track(self, customer_id: UUID, reward_track: str) -> bool:
        raise NotImplementedError
