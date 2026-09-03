from datetime import datetime, timezone
from uuid import UUID

from fastapi import status

from app.core.exceptions import AppException
from app.modules.customer.application.commands.update_customer_command import (
    UpdateCustomerCommand,
)
from app.modules.customer.application.dto.customer_dto import CustomerDto
from app.modules.customer.domain.unit_of_work import CustomerUnitOfWork


class UpdateCustomerHandler:

    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def handle(
        self,
        customer_id: UUID,
        command: UpdateCustomerCommand,
    ) -> CustomerDto:
        customer = await self.uow.customers.get_by_id(customer_id)
        if customer is None or not customer.is_active:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        phone = command.phone.strip()
        existing = await self.uow.customers.get_by_phone(
            phone,
            exclude_id=customer_id,
            active_only=True,
        )
        if existing is not None:
            raise AppException(
                message="Phone number already exists for an active customer.",
                status_code=status.HTTP_409_CONFLICT,
                errors=["PHONE_EXISTS"],
            )

        customer.update_profile(
            name=command.name,
            phone=phone,
            notes=command.notes,
            updated_at=datetime.now(timezone.utc),
        )
        await self.uow.customers.update(customer)
        await self.uow.commit()
        return CustomerDto.model_validate(customer)
