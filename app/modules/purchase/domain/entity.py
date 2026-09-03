from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class Purchase:
    id: UUID
    customer_id: UUID
    amount: Decimal
    points_earned: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    def update(
        self,
        *,
        amount: Decimal,
        points_earned: int,
        notes: str | None,
        updated_at: datetime,
    ) -> None:
        self.amount = amount
        self.points_earned = points_earned
        self.notes = notes.strip() if notes and notes.strip() else None
        self.updated_at = updated_at
