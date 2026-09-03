from abc import ABC, abstractmethod

from .repository import CustomerRepository


class CustomerUnitOfWork(ABC):

    @property
    @abstractmethod
    def customers(self) -> CustomerRepository:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
