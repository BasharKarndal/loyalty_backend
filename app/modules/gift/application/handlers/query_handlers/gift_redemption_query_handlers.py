from app.modules.gift.application.dto.gift_dto import (
    GiftRedemptionDetailDto,
    GiftRedemptionDto,
    GiftRedemptionListDto,
)
from app.modules.gift.application.queries.gift_queries import (
    GetGiftRedemptionQuery,
    ListGiftRedemptionsQuery,
)
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork


class GetGiftRedemptionHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetGiftRedemptionQuery) -> GiftRedemptionDetailDto:
        from fastapi import status

        from app.core.exceptions import AppException

        redemption = await self.uow.gift_redemptions.get_by_id(query.redemption_id)
        if redemption is None:
            raise AppException(
                message="Gift redemption not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_NOT_FOUND"],
            )

        customer = await self.uow.customers.get_by_id(redemption.customer_id)
        return GiftRedemptionDetailDto(
            **GiftRedemptionDto.model_validate(redemption).model_dump(),
            customer_name=customer.name if customer else "",
            customer_phone=customer.phone if customer else "",
            owner_id=customer.owner_id if customer else None,
        )


class ListGiftRedemptionsHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, query: ListGiftRedemptionsQuery) -> GiftRedemptionListDto:
        redemptions, total = await self.uow.gift_redemptions.list(
            skip=query.skip,
            limit=query.limit,
            customer_id=query.customer_id,
            status=query.status,
            exclude_cancelled=query.exclude_cancelled,
        )

        pending_count = await self._count_by_status(query.customer_id, "pending")
        delivered_count = await self._count_by_status(query.customer_id, "delivered")

        customer_cache: dict = {}
        items: list[GiftRedemptionDetailDto] = []

        for redemption in redemptions:
            if redemption.customer_id not in customer_cache:
                customer_cache[redemption.customer_id] = await self.uow.customers.get_by_id(
                    redemption.customer_id
                )
            customer = customer_cache[redemption.customer_id]
            items.append(
                GiftRedemptionDetailDto(
                    **GiftRedemptionDto.model_validate(redemption).model_dump(),
                    customer_name=customer.name if customer else "",
                    customer_phone=customer.phone if customer else "",
                    owner_id=customer.owner_id if customer else None,
                )
            )

        return GiftRedemptionListDto(
            items=items,
            total=total,
            skip=query.skip,
            limit=query.limit,
            pending_count=pending_count,
            delivered_count=delivered_count,
        )

    async def _count_by_status(self, customer_id, status: str) -> int:
        _, count = await self.uow.gift_redemptions.list(
            skip=0,
            limit=1,
            customer_id=customer_id,
            status=status,
            exclude_cancelled=True,
        )
        return count
