from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.infrastructure.repository import SqlAlchemyCustomerRepository
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork

from .repository import SqlAlchemyGiftRedemptionRepository, SqlAlchemyGiftTypeRepository


class SqlAlchemyGiftUnitOfWork(GiftUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session
        self._gift_types = SqlAlchemyGiftTypeRepository(session)
        self._gift_redemptions = SqlAlchemyGiftRedemptionRepository(session)
        self._customers = SqlAlchemyCustomerRepository(session)

    @property
    def gift_types(self) -> SqlAlchemyGiftTypeRepository:
        return self._gift_types

    @property
    def gift_redemptions(self) -> SqlAlchemyGiftRedemptionRepository:
        return self._gift_redemptions

    @property
    def customers(self) -> SqlAlchemyCustomerRepository:
        return self._customers

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
