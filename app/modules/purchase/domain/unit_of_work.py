from abc import ABC, abstractmethod

from app.modules.customer.domain.repository import CustomerRepository
from app.modules.gift.domain.repository import GiftRedemptionRepository
from app.modules.purchase.domain.repository import PurchaseRepository


class PurchaseUnitOfWork(ABC):

    @property
    @abstractmethod
    def purchases(self) -> PurchaseRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def customers(self) -> CustomerRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def gift_redemptions(self) -> GiftRedemptionRepository:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
