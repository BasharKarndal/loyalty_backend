from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.domain.entity import User
from app.modules.user.domain.unit_of_work import  UserUnitOfWork
from app.modules.user.infrastructure.repository import SqlAlchemyUserRepository
    




class SqlAlchemyUserUnitOfWork(UserUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session
        self._users = SqlAlchemyUserRepository(session)

    @property
    def users(self) -> SqlAlchemyUserRepository:
        return self._users

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()