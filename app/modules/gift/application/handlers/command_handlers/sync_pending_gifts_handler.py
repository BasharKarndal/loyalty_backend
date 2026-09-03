from datetime import datetime, timezone

from app.modules.gift.domain.unit_of_work import GiftUnitOfWork
from app.shared.loyalty.auto_pending_gift import sync_pending_gifts_for_customer
from app.shared.loyalty.service import LoyaltyService


class SyncPendingGiftsHandler:

    def __init__(self, uow: GiftUnitOfWork, loyalty: LoyaltyService):
        self.uow = uow
        self.loyalty = loyalty

    async def handle(self) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        customers, _ = await self.uow.customers.list(
            skip=0,
            limit=5000,
            search=None,
            active_only=True,
        )

        gifts_created = 0
        customers_updated = 0

        for customer in customers:
            created = await sync_pending_gifts_for_customer(
                customer=customer,
                loyalty=self.loyalty,
                gift_repo=self.uow.gift_redemptions,
                now=now,
            )
            if created > 0:
                gifts_created += created
                customers_updated += 1
                await self.uow.customers.update(customer)

        await self.uow.commit()
        return {
            "gifts_created": gifts_created,
            "customers_updated": customers_updated,
        }
