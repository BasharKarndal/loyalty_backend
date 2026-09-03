from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.domain.unit_of_work import CustomerUnitOfWork

from .repository import SqlAlchemyCustomerRepository


class SqlAlchemyCustomerUnitOfWork(CustomerUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session
        self._customers = SqlAlchemyCustomerRepository(session)

    @property
    def customers(self) -> SqlAlchemyCustomerRepository:
        return self._customers

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
