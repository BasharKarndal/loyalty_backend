from datetime import datetime
from uuid import uuid4

from app.modules.customer.domain.entity import Customer
from app.modules.gift.domain.gift_redemption_entity import (
    GIFT_STATUS_PENDING,
    REWARD_TRACK_AMOUNT,
    REWARD_TRACK_VISITS,
    GiftRedemption,
)
from app.modules.gift.domain.repository import GiftRedemptionRepository
from app.shared.loyalty.service import LoyaltyService

AUTO_PENDING_GIFT_NAME = "هدية ولاء"
AUTO_PENDING_GIFT_ICON = "card_giftcard"


async def _create_visit_pending(
    *,
    customer: Customer,
    loyalty: LoyaltyService,
    gift_repo: GiftRedemptionRepository,
    now: datetime,
) -> bool:
    if not loyalty.is_visit_gift_eligible(customer.visit_count):
        return False
    if await gift_repo.has_pending_for_track(customer.id, REWARD_TRACK_VISITS):
        return False

    cost = loyalty.visit_cost()
    # Balance is deducted only when the gift is delivered.
    await gift_repo.add(
        GiftRedemption(
            id=uuid4(),
            customer_id=customer.id,
            gift_type_id=None,
            gift_type_name=AUTO_PENDING_GIFT_NAME,
            gift_type_icon=AUTO_PENDING_GIFT_ICON,
            points_used=cost,
            reward_track=REWARD_TRACK_VISITS,
            notes=None,
            status=GIFT_STATUS_PENDING,
            created_at=now,
            delivered_at=None,
            updated_at=now,
            balance_deducted=False,
        )
    )
    return True


async def _create_points_pending(
    *,
    customer: Customer,
    loyalty: LoyaltyService,
    gift_repo: GiftRedemptionRepository,
    now: datetime,
) -> bool:
    if not loyalty.is_points_gift_eligible(customer.points):
        return False
    if await gift_repo.has_pending_for_track(customer.id, REWARD_TRACK_AMOUNT):
        return False

    cost = loyalty.points_cost()
    # Balance is deducted only when the gift is delivered.
    await gift_repo.add(
        GiftRedemption(
            id=uuid4(),
            customer_id=customer.id,
            gift_type_id=None,
            gift_type_name=AUTO_PENDING_GIFT_NAME,
            gift_type_icon=AUTO_PENDING_GIFT_ICON,
            points_used=cost,
            reward_track=REWARD_TRACK_AMOUNT,
            notes=None,
            status=GIFT_STATUS_PENDING,
            created_at=now,
            delivered_at=None,
            updated_at=now,
            balance_deducted=False,
        )
    )
    return True


async def cancel_ineligible_pending_gifts(
    *,
    customer: Customer,
    loyalty: LoyaltyService,
    gift_repo: GiftRedemptionRepository,
    now: datetime,
) -> int:
    """Cancel pending gifts the customer no longer qualifies for (e.g. after purchase edit)."""
    pending, _ = await gift_repo.list(
        skip=0,
        limit=100,
        customer_id=customer.id,
        status=GIFT_STATUS_PENDING,
        exclude_cancelled=False,
    )
    cancelled = 0
    for redemption in pending:
        still_eligible = (
            loyalty.is_visit_gift_eligible(customer.visit_count)
            if redemption.is_visit_track
            else loyalty.is_points_gift_eligible(customer.points)
        )
        if still_eligible:
            continue

        redemption.cancel(now)
        if redemption.balance_deducted:
            if redemption.is_visit_track:
                customer.restore_visit_gift(redemption.points_used, now)
            else:
                customer.restore_points_gift(redemption.points_used, now)
            redemption.balance_deducted = False
        await gift_repo.update(redemption)
        cancelled += 1
    return cancelled


async def sync_pending_gifts_for_customer(
    *,
    customer: Customer,
    loyalty: LoyaltyService,
    gift_repo: GiftRedemptionRepository,
    now: datetime,
) -> int:
    """Register pending gifts for every reward track the customer currently qualifies for."""
    created = 0
    if await _create_visit_pending(
        customer=customer, loyalty=loyalty, gift_repo=gift_repo, now=now
    ):
        created += 1
    if await _create_points_pending(
        customer=customer, loyalty=loyalty, gift_repo=gift_repo, now=now
    ):
        created += 1
    return created


async def ensure_pending_gifts_after_purchase(
    *,
    customer: Customer,
    loyalty: LoyaltyService,
    visit_eligible_before: bool,
    points_eligible_before: bool,
    gift_repo: GiftRedemptionRepository,
    now: datetime,
) -> None:
    """Creates pending gift rows when a purchase newly unlocks a reward track."""
    visit_eligible_after = loyalty.is_visit_gift_eligible(customer.visit_count)
    points_eligible_after = loyalty.is_points_gift_eligible(customer.points)

    if not visit_eligible_before and visit_eligible_after:
        await _create_visit_pending(
            customer=customer, loyalty=loyalty, gift_repo=gift_repo, now=now
        )

    if not points_eligible_before and points_eligible_after:
        await _create_points_pending(
            customer=customer, loyalty=loyalty, gift_repo=gift_repo, now=now
        )
