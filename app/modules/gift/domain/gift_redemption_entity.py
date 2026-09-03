from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

GIFT_STATUS_PENDING = "pending"
GIFT_STATUS_DELIVERED = "delivered"
GIFT_STATUS_CANCELLED = "cancelled"

REWARD_TRACK_VISITS = "visits"
REWARD_TRACK_AMOUNT = "amount"


@dataclass(slots=True)
class GiftRedemption:
    id: UUID
    customer_id: UUID
    gift_type_id: UUID | None
    gift_type_name: str
    gift_type_icon: str
    points_used: int
    reward_track: str
    notes: str | None
    status: str
    created_at: datetime
    delivered_at: datetime | None
    updated_at: datetime
    # True for legacy pending gifts that already deducted balance on create.
    balance_deducted: bool = False

    @property
    def is_pending(self) -> bool:
        return self.status == GIFT_STATUS_PENDING

    @property
    def is_visit_track(self) -> bool:
        return self.reward_track == REWARD_TRACK_VISITS

    def mark_delivered(self, updated_at: datetime) -> None:
        if not self.is_pending:
            raise ValueError("gift_not_pending")
        self.status = GIFT_STATUS_DELIVERED
        self.delivered_at = updated_at
        self.updated_at = updated_at
        self.balance_deducted = True

    def assign_gift_type(
        self,
        *,
        gift_type_id: UUID,
        name: str,
        icon: str,
        updated_at: datetime,
    ) -> None:
        self.gift_type_id = gift_type_id
        self.gift_type_name = name
        self.gift_type_icon = icon
        self.updated_at = updated_at

    def cancel(self, updated_at: datetime) -> None:
        if not self.is_pending:
            raise ValueError("gift_not_pending")
        self.status = GIFT_STATUS_CANCELLED
        self.updated_at = updated_at
