from datetime import datetime, timezone
from uuid import uuid4

from fastapi import status

from app.core.exceptions import AppException
from app.modules.gift.application.commands.redeem_gift_command import RedeemGiftCommand
from app.modules.gift.application.dto.gift_dto import GiftRedemptionDto
from app.modules.gift.domain.gift_redemption_entity import (
    GIFT_STATUS_PENDING,
    REWARD_TRACK_VISITS,
    GiftRedemption,
)
from app.modules.gift.domain.unit_of_work import GiftUnitOfWork
from app.shared.loyalty.service import LoyaltyService


class RedeemGiftHandler:

    def __init__(self, uow: GiftUnitOfWork, loyalty: LoyaltyService | None = None):
        self.uow = uow
        self.loyalty = loyalty or LoyaltyService()

    async def handle(self, command: RedeemGiftCommand) -> GiftRedemptionDto:
        customer = await self.uow.customers.get_by_id(command.customer_id)
        if customer is None or not customer.is_active:
            raise AppException(
                message="Customer not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["CUSTOMER_NOT_FOUND"],
            )

        gift_type = await self.uow.gift_types.get_by_id(command.gift_type_id)
        if gift_type is None or not gift_type.is_active:
            raise AppException(
                message="Gift type not found or inactive.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors=["GIFT_TYPE_INACTIVE"],
            )

        now = datetime.now(timezone.utc)
        track = command.reward_track

        if track == REWARD_TRACK_VISITS:
            if not self.loyalty.is_visit_gift_eligible(customer.visit_count):
                raise AppException(
                    message="Customer is not eligible for this gift track.",
                    status_code=status.HTTP_409_CONFLICT,
                    errors=["NOT_ELIGIBLE"],
                )
            cost = self.loyalty.visit_cost()
        else:
            if not self.loyalty.is_points_gift_eligible(customer.points):
                raise AppException(
                    message="Customer is not eligible for this gift track.",
                    status_code=status.HTTP_409_CONFLICT,
                    errors=["NOT_ELIGIBLE"],
                )
            cost = self.loyalty.points_cost()

        if await self.uow.gift_redemptions.has_pending_for_track(customer.id, track):
            raise AppException(
                message="Customer already has a pending gift for this track.",
                status_code=status.HTTP_409_CONFLICT,
                errors=["PENDING_GIFT_EXISTS"],
            )

        # Create pending only — points/visits are deducted on delivery confirmation.
        redemption = GiftRedemption(
            id=uuid4(),
            customer_id=command.customer_id,
            gift_type_id=gift_type.id,
            gift_type_name=gift_type.name,
            gift_type_icon=gift_type.icon_key,
            points_used=cost,
            reward_track=track,
            notes=command.notes.strip() if command.notes and command.notes.strip() else None,
            status=GIFT_STATUS_PENDING,
            created_at=now,
            delivered_at=None,
            updated_at=now,
            balance_deducted=False,
        )

        await self.uow.gift_redemptions.add(redemption)
        await self.uow.commit()
        return GiftRedemptionDto.model_validate(redemption)
