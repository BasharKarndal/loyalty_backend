from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@dataclass(slots=True)
class Purchase:
    id: UUID
    customer_id: UUID
    amount: Decimal
    points_earned: int
    product_type: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    def update(
        self,
        *,
        amount: Decimal,
        points_earned: int,
        product_type: str | None,
        notes: str | None,
        updated_at: datetime,
    ) -> None:
        self.amount = amount
        self.points_earned = points_earned
        self.product_type = _clean_optional(product_type)
        self.notes = _clean_optional(notes)
        self.updated_at = updated_at
