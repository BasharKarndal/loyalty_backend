from datetime import datetime, timezone
from uuid import UUID

from fastapi import status

from app.core.exceptions import AppException
from app.modules.gift.application.commands.deliver_gift_command import DeliverGiftCommand
from app.modules.gift.application.dto.gift_dto import GiftRedemptionDto
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork
from app.shared.loyalty.service import LoyaltyService


class DeliverGiftHandler:

    def __init__(self, uow: GiftUnitOfWork, loyalty: LoyaltyService | None = None):
        self.uow = uow
        self.loyalty = loyalty or LoyaltyService()

    async def handle(self, redemption_id: UUID, command: DeliverGiftCommand) -> GiftRedemptionDto:
        redemption = await self.uow.gift_redemptions.get_by_id(redemption_id)
        if redemption is None:
            raise AppException(
                message="Gift redemption not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_NOT_FOUND"],
            )

        gift_type = await self.uow.gift_types.get_by_id(command.gift_type_id)
        if gift_type is None or not gift_type.is_active:
            raise AppException(
                message="Gift type not found or inactive.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_TYPE_INACTIVE"],
            )

        customer = await self.uow.customers.get_by_id(redemption.customer_id)
        if customer is None or not customer.is_active:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        now = datetime.now(timezone.utc)
        redemption.assign_gift_type(
            gift_type_id=gift_type.id,
            name=gift_type.name,
            icon=gift_type.icon_key,
            updated_at=now,
        )

        # Deduct balance only at delivery (skip for legacy gifts already deducted on create).
        if not redemption.balance_deducted:
            try:
                if redemption.is_visit_track:
                    customer.redeem_visit_gift(redemption.points_used, now)
                else:
                    customer.redeem_points_gift(redemption.points_used, now)
            except ValueError as exc:
                raise AppException(
                    message="Customer no longer has enough balance to deliver this gift.",
                    status_code=status.HTTP_409_CONFLICT,
                    errors=["INSUFFICIENT_BALANCE"],
                ) from exc

        try:
            redemption.mark_delivered(now)
        except ValueError as exc:
            raise AppException(
                message="Gift is not pending.",
                status_code=status.HTTP_409_CONFLICT,
                errors=["GIFT_NOT_PENDING"],
            ) from exc

        await self.uow.gift_redemptions.update(redemption)
        await self.uow.customers.update(customer)
        await self.uow.commit()
        return GiftRedemptionDto.model_validate(redemption)


class CancelGiftHandler:

    def __init__(self, uow: GiftUnitOfWork):
        self.uow = uow

    async def handle(self, redemption_id: UUID) -> GiftRedemptionDto:
        redemption = await self.uow.gift_redemptions.get_by_id(redemption_id)
        if redemption is None:
            raise AppException(
                message="Gift redemption not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_NOT_FOUND"],
            )

        customer = await self.uow.customers.get_by_id(redemption.customer_id)
        if customer is None:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        now = datetime.now(timezone.utc)
        try:
            redemption.cancel(now)
        except ValueError as exc:
            raise AppException(
                message="Gift is not pending.",
                status_code=status.HTTP_409_CONFLICT,
                errors=["GIFT_NOT_PENDING"],
            ) from exc

        # Restore only if balance was already deducted (legacy pending gifts).
        if redemption.balance_deducted:
            if redemption.is_visit_track:
                customer.restore_visit_gift(redemption.points_used, now)
            else:
                customer.restore_points_gift(redemption.points_used, now)
            redemption.balance_deducted = False

        await self.uow.gift_redemptions.update(redemption)
        await self.uow.customers.update(customer)
        await self.uow.commit()
        return GiftRedemptionDto.model_validate(redemption)
