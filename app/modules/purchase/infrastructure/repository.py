from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.infrastructure.model import CustomerModel
from app.modules.purchase.domain.entity import Purchase
from app.modules.purchase.domain.repository import PurchaseRepository
from app.shared.tenancy import owner_match

from .mapper import PurchaseMapper
from .model import PurchaseModel


class SqlAlchemyPurchaseRepository(PurchaseRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, purchase: Purchase) -> None:
        self.session.add(PurchaseMapper.to_model(purchase))

    async def update(self, purchase: Purchase) -> None:
        model = await self.session.get(PurchaseModel, purchase.id)
        if model is None:
            return

        model.amount = purchase.amount
        model.points_earned = purchase.points_earned
        model.notes = purchase.notes
        model.updated_at = purchase.updated_at

    async def get_by_id(self, purchase_id: UUID) -> Purchase | None:
        stmt = select(PurchaseModel).where(PurchaseModel.id == purchase_id).join(
            CustomerModel, CustomerModel.id == PurchaseModel.customer_id
        ).where(owner_match(CustomerModel.owner_id))
        result = await self.session.execute(stmt.limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return PurchaseMapper.to_domain(model)

    async def list(
        self,
        *,
        skip: int,
        limit: int,
        customer_id: UUID | None,
        search: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[list[Purchase], int]:
        filters = self._build_filters(
            customer_id=customer_id,
            search=search,
            from_date=from_date,
            to_date=to_date,
        )

        count_stmt = (
            select(func.count())
            .select_from(PurchaseModel)
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
        )
        list_stmt = (
            select(PurchaseModel)
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
        )

        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)

        total = await self.session.scalar(count_stmt) or 0
        result = await self.session.execute(
            list_stmt.order_by(PurchaseModel.created_at.desc()).offset(skip).limit(limit)
        )
        items = [PurchaseMapper.to_domain(model) for model in result.scalars().all()]
        return items, int(total)

    async def sum_amount(
        self,
        *,
        customer_id: UUID | None,
        search: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> Decimal:
        filters = self._build_filters(
            customer_id=customer_id,
            search=search,
            from_date=from_date,
            to_date=to_date,
        )
        stmt = select(func.coalesce(func.sum(PurchaseModel.amount), 0)).select_from(PurchaseModel)
        stmt = stmt.join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
        if filters:
            stmt = stmt.where(*filters)
        total = await self.session.scalar(stmt)
        return Decimal(str(total or 0))

    def _build_filters(
        self,
        *,
        customer_id: UUID | None,
        search: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> list:
        filters = [owner_match(CustomerModel.owner_id)]
        if customer_id is not None:
            filters.append(PurchaseModel.customer_id == customer_id)
        if from_date is not None:
            filters.append(PurchaseModel.created_at >= from_date)
        if to_date is not None:
            filters.append(PurchaseModel.created_at < to_date)
        if search and search.strip():
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    CustomerModel.name.ilike(term),
                    CustomerModel.phone.ilike(term),
                )
            )
        return filters
