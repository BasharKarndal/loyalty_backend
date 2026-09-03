from abc import ABC, abstractmethod
from uuid import UUID

from .entity import User


class UserRepository(ABC):

    @abstractmethod
    async def add(self, user: User) -> None:
        pass

    @abstractmethod
    async def update(self, user: User) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def list(self) -> list[User]:
        pass

    @abstractmethod
    async def get_permissions(self, user_id: UUID):
        pass

    @abstractmethod
    async def get_by_id_no_ditels(self, user_id: UUID) -> User | None:
        pass
