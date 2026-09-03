from datetime import datetime, timezone
from uuid import UUID

from fastapi import status

from app.core.exceptions import AppException
from app.modules.customer.domain.unit_of_work import CustomerUnitOfWork


class DeleteCustomerHandler:

    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def handle(self, customer_id: UUID) -> None:
        customer = await self.uow.customers.get_by_id(customer_id)
        if customer is None or not customer.is_active:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        customer.deactivate(updated_at=datetime.now(timezone.utc))
        await self.uow.customers.update(customer)
        await self.uow.commit()
