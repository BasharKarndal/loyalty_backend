from abc import ABC, abstractmethod

from .repository import UserRepository


class UserUnitOfWork(ABC):

    @property
    @abstractmethod
    def users(self) -> UserRepository:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass