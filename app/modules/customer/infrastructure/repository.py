from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.domain.entity import Customer
from app.modules.customer.domain.repository import CustomerRepository
from app.shared.tenancy import can_access_owner, owner_match

from .mapper import CustomerMapper
from .model import CustomerModel


def _owner_filter():
    return owner_match(CustomerModel.owner_id)


class SqlAlchemyCustomerRepository(CustomerRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, customer: Customer) -> None:
        self.session.add(CustomerMapper.to_model(customer))

    async def update(self, customer: Customer) -> None:
        model = await self.session.get(CustomerModel, customer.id)
        if model is None:
            return
        if not can_access_owner(model.owner_id):
            return

        model.name = customer.name
        model.phone = customer.phone
        model.notes = customer.notes
        model.points = customer.points
        model.visit_count = customer.visit_count
        model.total_spent = customer.total_spent
        model.is_active = customer.is_active
        model.updated_at = customer.updated_at

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        stmt = select(CustomerModel).where(CustomerModel.id == customer_id, _owner_filter())
        result = await self.session.execute(stmt.limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return CustomerMapper.to_domain(model)

    async def get_by_phone(
        self,
        phone: str,
        *,
        exclude_id: UUID | None = None,
        active_only: bool = False,
    ) -> Customer | None:
        stmt = select(CustomerModel).where(CustomerModel.phone == phone.strip(), _owner_filter())
        if exclude_id is not None:
            stmt = stmt.where(CustomerModel.id != exclude_id)
        if active_only:
            stmt = stmt.where(CustomerModel.is_active.is_(True))

        result = await self.session.execute(stmt.limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return CustomerMapper.to_domain(model)

    async def list(
        self,
        *,
        skip: int,
        limit: int,
        search: str | None,
        active_only: bool = True,
        inactive_only: bool = False,
    ) -> tuple[list[Customer], int]:
        filters = [_owner_filter()]
        if inactive_only:
            filters.append(CustomerModel.is_active.is_(False))
        elif active_only:
            filters.append(CustomerModel.is_active.is_(True))
        if search and search.strip():
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    CustomerModel.name.ilike(term),
                    CustomerModel.phone.ilike(term),
                )
            )

        count_stmt = select(func.count()).select_from(CustomerModel)
        list_stmt = select(CustomerModel)
        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)

        total = await self.session.scalar(count_stmt) or 0
        result = await self.session.execute(
            list_stmt.order_by(CustomerModel.created_at.desc()).offset(skip).limit(limit)
        )
        items = [CustomerMapper.to_domain(model) for model in result.scalars().all()]
        return items, int(total)
