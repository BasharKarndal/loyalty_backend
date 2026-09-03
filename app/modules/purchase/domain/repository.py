from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.modules.purchase.domain.entity import Purchase


class PurchaseRepository(ABC):

    @abstractmethod
    async def add(self, purchase: Purchase) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, purchase: Purchase) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, purchase_id: UUID) -> Purchase | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        skip: int,
        limit: int,
        customer_id: UUID | None,
        search: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[list[Purchase], int]:
        raise NotImplementedError

    @abstractmethod
    async def sum_amount(
        self,
        *,
        customer_id: UUID | None,
        search: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> Decimal:
        raise NotImplementedError
