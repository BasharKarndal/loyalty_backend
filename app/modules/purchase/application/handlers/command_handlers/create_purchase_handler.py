from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.core.exceptions import AppException
from app.modules.purchase.application.commands.create_purchase_command import (
    CreatePurchaseCommand,
)
from app.modules.purchase.application.dto.purchase_dto import PurchaseDto
from app.modules.purchase.domain.entity import Purchase
from app.modules.purchase.domain.unit_of_work import PurchaseUnitOfWork
from app.shared.loyalty.auto_pending_gift import ensure_pending_gifts_after_purchase
from app.shared.loyalty.service import LoyaltyService


class CreatePurchaseHandler:

    def __init__(self, uow: PurchaseUnitOfWork, loyalty: LoyaltyService | None = None):
        self.uow = uow
        self.loyalty = loyalty or LoyaltyService()

    async def handle(self, command: CreatePurchaseCommand) -> PurchaseDto:
        customer = await self.uow.customers.get_by_id(command.customer_id)
        if customer is None or not customer.is_active:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        visit_eligible_before = self.loyalty.is_visit_gift_eligible(customer.visit_count)
        points_eligible_before = self.loyalty.is_points_gift_eligible(customer.points)

        points_earned = self.loyalty.points_for_purchase(command.amount)
        now = datetime.now(timezone.utc)

        purchase = Purchase(
            id=uuid4(),
            customer_id=command.customer_id,
            amount=command.amount,
            points_earned=points_earned,
            product_type=command.product_type,
            notes=command.notes,
            created_at=now,
            updated_at=now,
        )

        customer.apply_purchase(
            amount=command.amount,
            points_earned=points_earned,
            updated_at=now,
        )

        await ensure_pending_gifts_after_purchase(
            customer=customer,
            loyalty=self.loyalty,
            visit_eligible_before=visit_eligible_before,
            points_eligible_before=points_eligible_before,
            gift_repo=self.uow.gift_redemptions,
            now=now,
        )

        await self.uow.purchases.add(purchase)
        await self.uow.customers.update(customer)
        await self.uow.commit()
        return PurchaseDto.model_validate(purchase)
