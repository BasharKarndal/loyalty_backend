from app.modules.customer.application.dto.customer_dto import CustomerDto, CustomerListDto
from app.modules.customer.application.queries.customer_queries import ListCustomersQuery
from app.modules.customer.domain.unit_of_work import CustomerUnitOfWork


class ListCustomersHandler:

    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def handle(self, query: ListCustomersQuery) -> CustomerListDto:
        items, total = await self.uow.customers.list(
            skip=query.skip,
            limit=query.limit,
            search=query.search,
            active_only=query.active_only,
            inactive_only=query.inactive_only,
        )
        return CustomerListDto(
            items=[CustomerDto.model_validate(item) for item in items],
            total=total,
            skip=query.skip,
            limit=query.limit,
        )
