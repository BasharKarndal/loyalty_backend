from datetime import datetime, timezone
from uuid import UUID

from fastapi import status

from app.core.exceptions import AppException
from app.modules.purchase.application.commands.update_purchase_command import (
    UpdatePurchaseCommand,
)
from app.modules.purchase.application.dto.purchase_dto import PurchaseDto
from app.modules.purchase.domain.unit_of_work import PurchaseUnitOfWork
from app.shared.loyalty.auto_pending_gift import (
    cancel_ineligible_pending_gifts,
    sync_pending_gifts_for_customer,
)
from app.shared.loyalty.service import LoyaltyService


class UpdatePurchaseHandler:

    def __init__(self, uow: PurchaseUnitOfWork, loyalty: LoyaltyService | None = None):
        self.uow = uow
        self.loyalty = loyalty or LoyaltyService()

    async def handle(self, purchase_id: UUID, command: UpdatePurchaseCommand) -> PurchaseDto:
        purchase = await self.uow.purchases.get_by_id(purchase_id)
        if purchase is None:
            raise AppException(
                message="Purchase not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["PURCHASE_NOT_FOUND"],
            )

        customer = await self.uow.customers.get_by_id(purchase.customer_id)
        if customer is None or not customer.is_active:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        new_points = self.loyalty.points_for_purchase(command.amount)
        delta_points = new_points - purchase.points_earned
        delta_amount = command.amount - purchase.amount
        now = datetime.now(timezone.utc)

        try:
            customer.adjust_purchase(
                delta_amount=delta_amount,
                delta_points=delta_points,
                updated_at=now,
            )
        except ValueError as exc:
            code = str(exc)
            if code == "insufficient_points":
                raise AppException(
                    message="Insufficient customer points for this update.",
                    status_code=status.HTTP_409_CONFLICT,
                    errors=["INSUFFICIENT_POINTS"],
                ) from exc
            raise AppException(
                message="Invalid purchase amount.",
                status_code=status.HTTP_409_CONFLICT,
                errors=["INVALID_AMOUNT"],
            ) from exc

        purchase.update(
            amount=command.amount,
            points_earned=new_points,
            product_type=command.product_type,
            notes=command.notes,
            updated_at=now,
        )

        # If amount correction makes customer ineligible, cancel pending gifts
        # without touching points (points are deducted only on delivery).
        await cancel_ineligible_pending_gifts(
            customer=customer,
            loyalty=self.loyalty,
            gift_repo=self.uow.gift_redemptions,
            now=now,
        )
        await sync_pending_gifts_for_customer(
            customer=customer,
            loyalty=self.loyalty,
            gift_repo=self.uow.gift_redemptions,
            now=now,
        )

        await self.uow.purchases.update(purchase)
        await self.uow.customers.update(customer)
        await self.uow.commit()
        return PurchaseDto.model_validate(purchase)
