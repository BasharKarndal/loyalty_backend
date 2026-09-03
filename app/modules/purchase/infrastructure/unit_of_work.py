from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.infrastructure.repository import SqlAlchemyCustomerRepository
from app.modules.gift.infrastructure.repository import SqlAlchemyGiftRedemptionRepository
from app.modules.purchase.domain.unit_of_work import PurchaseUnitOfWork

from .repository import SqlAlchemyPurchaseRepository


class SqlAlchemyPurchaseUnitOfWork(PurchaseUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session
        self._purchases = SqlAlchemyPurchaseRepository(session)
        self._customers = SqlAlchemyCustomerRepository(session)
        self._gift_redemptions = SqlAlchemyGiftRedemptionRepository(session)

    @property
    def purchases(self) -> SqlAlchemyPurchaseRepository:
        return self._purchases

    @property
    def customers(self) -> SqlAlchemyCustomerRepository:
        return self._customers

    @property
    def gift_redemptions(self) -> SqlAlchemyGiftRedemptionRepository:
        return self._gift_redemptions

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
