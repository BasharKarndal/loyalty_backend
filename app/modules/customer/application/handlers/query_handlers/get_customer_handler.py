from fastapi import status

from app.core.exceptions import AppException
from app.modules.customer.application.dto.customer_dto import CustomerDto
from app.modules.customer.application.queries.customer_queries import GetCustomerQuery
from app.modules.customer.domain.unit_of_work import CustomerUnitOfWork


class GetCustomerHandler:

    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def handle(self, query: GetCustomerQuery) -> CustomerDto:
        customer = await self.uow.customers.get_by_id(query.customer_id)
        if customer is None:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )
        return CustomerDto.model_validate(customer)
