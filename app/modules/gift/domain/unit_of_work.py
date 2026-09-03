from abc import ABC, abstractmethod

from app.modules.customer.domain.repository import CustomerRepository
from app.modules.gift.domain.repository import GiftRedemptionRepository, GiftTypeRepository


class GiftUnitOfWork(ABC):

    @property
    @abstractmethod
    def gift_types(self) -> GiftTypeRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def gift_redemptions(self) -> GiftRedemptionRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def customers(self) -> CustomerRepository:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
