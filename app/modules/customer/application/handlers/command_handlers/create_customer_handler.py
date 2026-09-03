from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import status

from app.core.exceptions import AppException
from app.modules.customer.application.commands.create_customer_command import (
    CreateCustomerCommand,
)
from app.modules.customer.application.dto.customer_dto import CustomerDto
from app.modules.customer.domain.entity import Customer
from app.modules.customer.domain.unit_of_work import CustomerUnitOfWork
from app.shared.tenancy import require_owner_id


class CreateCustomerHandler:

    def __init__(self, uow: CustomerUnitOfWork):
        self.uow = uow

    async def handle(self, command: CreateCustomerCommand) -> CustomerDto:
        phone = command.phone.strip()
        existing = await self.uow.customers.get_by_phone(
            phone,
            active_only=True,
        )
        if existing is not None:
            raise AppException(
                message="Phone number already exists for an active customer.",
                status_code=status.HTTP_409_CONFLICT,
                errors=["PHONE_EXISTS"],
            )

        now = datetime.now(timezone.utc)
        customer = Customer(
            id=uuid4(),
            owner_id=require_owner_id(),
            name=command.name.strip(),
            phone=phone,
            notes=command.notes.strip() if command.notes and command.notes.strip() else None,
            points=0,
            visit_count=0,
            total_spent=Decimal("0"),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        await self.uow.customers.add(customer)
        await self.uow.commit()
        return CustomerDto.model_validate(customer)
