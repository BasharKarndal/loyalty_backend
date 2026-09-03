from datetime import datetime
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.infrastructure.model import CustomerModel
from app.modules.gift.infrastructure.model import GiftRedemptionModel
from app.modules.purchase.infrastructure.model import PurchaseModel
from app.shared.tenancy import owner_match
from app.modules.reports.application.dto.report_dto import (
    DailySalesPointDto,
    ReportStatsDto,
    TopCustomerSpendDto,
)


class ReportRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _owner_purchase_filters(self) -> list:
        return [owner_match(CustomerModel.owner_id)]

    async def get_stats(self, *, from_date: datetime, to_date: datetime) -> ReportStatsDto:
        owner_filters = self._owner_purchase_filters()
        purchase_filters = [
            PurchaseModel.created_at >= from_date,
            PurchaseModel.created_at <= to_date,
            *owner_filters,
        ]
        gift_filters = [
            GiftRedemptionModel.created_at >= from_date,
            GiftRedemptionModel.created_at <= to_date,
            GiftRedemptionModel.status != "cancelled",
            *owner_filters,
        ]

        total_sales = await self.session.scalar(
            select(func.coalesce(func.sum(PurchaseModel.amount), 0))
            .select_from(PurchaseModel)
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
            .where(*purchase_filters)
        ) or Decimal("0")

        purchases_count = await self.session.scalar(
            select(func.count())
            .select_from(PurchaseModel)
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
            .where(*purchase_filters)
        ) or 0

        gifts_count = await self.session.scalar(
            select(func.count())
            .select_from(GiftRedemptionModel)
            .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
            .where(*gift_filters)
        ) or 0

        pending_gifts_count = await self._count_gifts(
            from_date, to_date, status="pending"
        )
        delivered_gifts_count = await self._count_gifts(
            from_date, to_date, status="delivered"
        )
        visit_track_gifts_count = await self._count_gifts(
            from_date, to_date, reward_track="visits"
        )
        points_track_gifts_count = await self._count_gifts(
            from_date, to_date, reward_track="amount"
        )

        average_purchase = (
            Decimal(str(total_sales)) / purchases_count if purchases_count else Decimal("0")
        )

        daily_sales = await self._daily_sales(from_date, to_date)
        top_customers = await self._top_customers(from_date, to_date)

        return ReportStatsDto(
            total_sales=Decimal(str(total_sales)),
            purchases_count=int(purchases_count),
            gifts_count=int(gifts_count),
            pending_gifts_count=int(pending_gifts_count),
            delivered_gifts_count=int(delivered_gifts_count),
            visit_track_gifts_count=int(visit_track_gifts_count),
            points_track_gifts_count=int(points_track_gifts_count),
            average_purchase=average_purchase,
            top_customers=top_customers,
            daily_sales=daily_sales,
            from_date=from_date,
            to_date=to_date,
        )

    async def _count_gifts(
        self,
        from_date: datetime,
        to_date: datetime,
        *,
        status: str | None = None,
        reward_track: str | None = None,
    ) -> int:
        filters = [
            GiftRedemptionModel.created_at >= from_date,
            GiftRedemptionModel.created_at <= to_date,
            GiftRedemptionModel.status != "cancelled",
            *self._owner_purchase_filters(),
        ]
        if status is not None:
            filters.append(GiftRedemptionModel.status == status)
        if reward_track is not None:
            filters.append(GiftRedemptionModel.reward_track == reward_track)
        return int(
            await self.session.scalar(
                select(func.count())
                .select_from(GiftRedemptionModel)
                .join(CustomerModel, CustomerModel.id == GiftRedemptionModel.customer_id)
                .where(*filters)
            )
            or 0
        )

    async def _daily_sales(
        self, from_date: datetime, to_date: datetime
    ) -> list[DailySalesPointDto]:
        day_col = cast(func.date_trunc("day", PurchaseModel.created_at), Date)
        result = await self.session.execute(
            select(day_col.label("day"), func.coalesce(func.sum(PurchaseModel.amount), 0))
            .join(CustomerModel, CustomerModel.id == PurchaseModel.customer_id)
            .where(
                PurchaseModel.created_at >= from_date,
                PurchaseModel.created_at <= to_date,
                *self._owner_purchase_filters(),
            )
            .group_by(day_col)
            .order_by(day_col)
        )
        return [
            DailySalesPointDto(day=row.day, total=Decimal(str(row[1])))
            for row in result.all()
        ]

    async def _top_customers(
        self, from_date: datetime, to_date: datetime, limit: int = 5
    ) -> list[TopCustomerSpendDto]:
        result = await self.session.execute(
            select(
                CustomerModel.id,
                CustomerModel.name,
                CustomerModel.phone,
                func.coalesce(func.sum(PurchaseModel.amount), 0).label("spent"),
            )
            .join(PurchaseModel, PurchaseModel.customer_id == CustomerModel.id)
            .where(
                PurchaseModel.created_at >= from_date,
                PurchaseModel.created_at <= to_date,
                *self._owner_purchase_filters(),
            )
            .group_by(CustomerModel.id, CustomerModel.name, CustomerModel.phone)
            .order_by(func.sum(PurchaseModel.amount).desc())
            .limit(limit)
        )
        return [
            TopCustomerSpendDto(
                customer_id=row.id,
                customer_name=row.name,
                customer_phone=row.phone,
                spent=Decimal(str(row.spent)),
            )
            for row in result.all()
        ]
