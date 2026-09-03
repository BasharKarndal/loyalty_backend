from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.gift.domain.gift_redemption_entity import GiftRedemption
from app.modules.gift.domain.gift_type_entity import GiftType
from app.modules.gift.domain.repository import GiftRedemptionRepository, GiftTypeRepository
from app.modules.customer.infrastructure.model import CustomerModel
from app.shared.tenancy import can_access_owner, owner_match

from .mapper import GiftRedemptionMapper, GiftTypeMapper
from .model import GiftRedemptionModel, GiftTypeModel


class SqlAlchemyGiftTypeRepository(GiftTypeRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, gift_type: GiftType) -> None:
        self.session.add(GiftTypeMapper.to_model(gift_type))

    async def update(self, gift_type: GiftType) -> None:
        model = await self.session.get(GiftTypeModel, gift_type.id)
        if model is None:
            return
        if not can_access_owner(model.owner_id):
            return
        model.name = gift_type.name
        model.icon_key = gift_type.icon_key
        model.sort_order = gift_type.sort_order
        model.is_active = gift_type.is_active
        model.updated_at = gift_type.updated_at

    async def get_by_id(self, gift_type_id: UUID) -> GiftType | None:
        stmt = select(GiftTypeModel).where(
            GiftTypeModel.id == gift_type_id,
            owner_match(GiftTypeModel.owner_id),
        )
        result = await self.session.execute(stmt.limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return GiftTypeMapper.to_domain(model)

    async def list(self, *, active_only: bool | None = None) -> list[GiftType]:
        stmt = select(GiftTypeModel).where(owner_match(GiftTypeModel.owner_id))
        if active_only is True:
            stmt = stmt.where(GiftTypeModel.is_active.is_(True))
        elif active_only is False:
            stmt = stmt.where(GiftTypeModel.is_active.is_(False))
        result = await self.session.execute(
            stmt.order_by(GiftTypeModel.sort_order.asc(), GiftTypeModel.name.asc())
        )
        return [GiftTypeMapper.to_domain(model) for model in result.scalars().all()]


class SqlAlchemyGiftRedemptionRepository(GiftRedemptionRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, redemption: GiftRedemption) -> None:
        self.session.add(GiftRedemptionMapper.to_model(redemption))

    async def update(self, redemption: GiftRedemption) -> None:
        model = await self.session.get(GiftRedemptionModel, redemption.id)
        if model is None:
            return
        model.gift_type_id = redemption.gift_type_id
        model.gift_type_name = redemption.gift_type_name
        model.gift_type_icon = redemption.gift_type_icon
        model.status = redemption.status
        model.balance_deducted = redemption.balance_deducted
        model.delivered_at = redemption.delivered_at
        model.updated_at = redemption.updated_at

    async def get_by_id(self, redemption_id: UUID) -> GiftRedemption | None:
        stmt = select(GiftRedemptionModel).where(
            GiftRedemptionModel.id == redemption_id
        ).join(
            CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id
        ).where(owner_match(CustomerModel.owner_id))
        result = await self.session.execute(stmt.limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return GiftRedemptionMapper.to_domain(model)

    async def list(
        self,
        *,
        skip: int,
        limit: int,
        customer_id: UUID | None,
        status: str | None,
        exclude_cancelled: bool,
    ) -> tuple[list[GiftRedemption], int]:
        filters = [owner_match(CustomerModel.owner_id)]
        if customer_id is not None:
            filters.append(GiftRedemptionModel.customer_id == customer_id)
        if status is not None:
            filters.append(GiftRedemptionModel.status == status)
        if exclude_cancelled:
            filters.append(GiftRedemptionModel.status != "cancelled")

        count_stmt = (
            select(func.count())
            .select_from(GiftRedemptionModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
        )
        list_stmt = (
            select(GiftRedemptionModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
        )
        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)

        total = await self.session.scalar(count_stmt) or 0
        result = await self.session.execute(
            list_stmt.order_by(GiftRedemptionModel.created_at.desc()).offset(skip).limit(limit)
        )
        items = [GiftRedemptionMapper.to_domain(model) for model in result.scalars().all()]
        return items, int(total)

    async def has_pending_for_track(self, customer_id: UUID, reward_track: str) -> bool:
        stmt = (
            select(func.count())
            .select_from(GiftRedemptionModel)
            .where(
                GiftRedemptionModel.customer_id == customer_id,
                GiftRedemptionModel.reward_track == reward_track,
                GiftRedemptionModel.status == "pending",
            )
        )
        count = await self.session.scalar(stmt) or 0
        return count > 0
