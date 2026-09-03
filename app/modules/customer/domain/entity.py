from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class Customer:
    id: UUID
    owner_id: UUID
    name: str
    phone: str
    notes: str | None
    points: int
    visit_count: int
    total_spent: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def update_profile(
        self,
        name: str,
        phone: str,
        notes: str | None,
        updated_at: datetime,
    ) -> None:
        self.name = name.strip()
        self.phone = phone.strip()
        self.notes = notes.strip() if notes and notes.strip() else None
        self.updated_at = updated_at

    def activate(self, updated_at: datetime) -> None:
        self.is_active = True
        self.updated_at = updated_at

    def deactivate(self, updated_at: datetime) -> None:
        self.is_active = False
        self.updated_at = updated_at

    def apply_purchase(
        self,
        *,
        amount: Decimal,
        points_earned: int,
        updated_at: datetime,
    ) -> None:
        self.points += points_earned
        self.visit_count += 1
        self.total_spent += amount
        self.updated_at = updated_at

    def adjust_purchase(
        self,
        *,
        delta_amount: Decimal,
        delta_points: int,
        updated_at: datetime,
    ) -> None:
        new_points = self.points + delta_points
        new_total = self.total_spent + delta_amount
        if new_points < 0:
            raise ValueError("insufficient_points")
        if new_total < 0:
            raise ValueError("invalid_amount")
        self.points = new_points
        self.total_spent = new_total
        self.updated_at = updated_at

    def redeem_visit_gift(self, cost: int, updated_at: datetime) -> None:
        if self.visit_count < cost:
            raise ValueError("not_eligible")
        self.visit_count -= cost
        self.updated_at = updated_at

    def redeem_points_gift(self, cost: int, updated_at: datetime) -> None:
        if self.points < cost:
            raise ValueError("not_eligible")
        self.points -= cost
        self.updated_at = updated_at

    def restore_visit_gift(self, amount: int, updated_at: datetime) -> None:
        self.visit_count += amount
        self.updated_at = updated_at

    def restore_points_gift(self, amount: int, updated_at: datetime) -> None:
        self.points += amount
        self.updated_at = updated_at
