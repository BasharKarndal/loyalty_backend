from app.modules.purchase.application.dto.purchase_dto import PurchaseDetailDto, PurchaseDto, PurchaseListDto
from app.modules.purchase.application.queries.purchase_queries import ListPurchasesQuery
from app.modules.purchase.domain.unit_of_work import PurchaseUnitOfWork


class ListPurchasesHandler:

    def __init__(self, uow: PurchaseUnitOfWork):
        self.uow = uow

    async def handle(self, query: ListPurchasesQuery) -> PurchaseListDto:
        purchases, total = await self.uow.purchases.list(
            skip=query.skip,
            limit=query.limit,
            customer_id=query.customer_id,
            search=query.search,
            from_date=query.from_date,
            to_date=query.to_date,
        )
        total_amount = await self.uow.purchases.sum_amount(
            customer_id=query.customer_id,
            search=query.search,
            from_date=query.from_date,
            to_date=query.to_date,
        )

        customer_cache: dict = {}
        items: list[PurchaseDetailDto] = []

        for purchase in purchases:
            if purchase.customer_id not in customer_cache:
                customer_cache[purchase.customer_id] = await self.uow.customers.get_by_id(
                    purchase.customer_id
                )
            customer = customer_cache[purchase.customer_id]
            items.append(
                PurchaseDetailDto(
                    **PurchaseDto.model_validate(purchase).model_dump(),
            customer_name=customer.name if customer else "",
            customer_phone=customer.phone if customer else "",
            owner_id=customer.owner_id if customer else None,
                )
            )

        return PurchaseListDto(
            items=items,
            total=total,
            total_amount=total_amount,
            skip=query.skip,
            limit=query.limit,
        )
