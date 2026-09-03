from fastapi import status

from app.core.exceptions import AppException
from app.modules.purchase.application.dto.purchase_dto import PurchaseDetailDto, PurchaseDto
from app.modules.purchase.application.queries.purchase_queries import GetPurchaseQuery
from app.modules.purchase.domain.unit_of_work import PurchaseUnitOfWork


class GetPurchaseHandler:

    def __init__(self, uow: PurchaseUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetPurchaseQuery) -> PurchaseDetailDto:
        purchase = await self.uow.purchases.get_by_id(query.purchase_id)
        if purchase is None:
            raise AppException(
                message="Purchase not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["PURCHASE_NOT_FOUND"],
            )

        customer = await self.uow.customers.get_by_id(purchase.customer_id)
        return PurchaseDetailDto(
            **PurchaseDto.model_validate(purchase).model_dump(),
            customer_name=customer.name if customer else "",
            customer_phone=customer.phone if customer else "",
            owner_id=customer.owner_id if customer else None,
        )
