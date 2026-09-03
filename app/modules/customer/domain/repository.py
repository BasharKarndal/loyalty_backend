from abc import ABC, abstractmethod
from uuid import UUID

from .entity import Customer


class CustomerRepository(ABC):

    @abstractmethod
    async def add(self, customer: Customer) -> None:
        pass

    @abstractmethod
    async def update(self, customer: Customer) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        pass

    @abstractmethod
    async def get_by_phone(
        self,
        phone: str,
        *,
        exclude_id: UUID | None = None,
        active_only: bool = False,
    ) -> Customer | None:
        pass

    @abstractmethod
    async def list(
        self,
        *,
        skip: int,
        limit: int,
        search: str | None,
        active_only: bool = True,
        inactive_only: bool = False,
    ) -> tuple[list[Customer], int]:
        pass
