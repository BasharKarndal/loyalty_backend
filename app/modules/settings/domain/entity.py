from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class UserSettings:
    id: UUID
    user_id: UUID
    cafe_name: str
    logo_path: str | None
    currency: str
    visit_reward_target: int
    points_reward_target: int
    currency_per_point: Decimal
    created_at: datetime
    updated_at: datetime

    def update(
        self,
        *,
        cafe_name: str,
        currency: str,
        visit_reward_target: int,
        points_reward_target: int,
        currency_per_point: Decimal,
        updated_at: datetime,
    ) -> None:
        self.cafe_name = cafe_name.strip()
        self.currency = currency.strip()
        self.visit_reward_target = visit_reward_target
        self.points_reward_target = points_reward_target
        self.currency_per_point = currency_per_point
        self.updated_at = updated_at

    def set_logo(self, logo_path: str | None, updated_at: datetime) -> None:
        self.logo_path = logo_path
        self.updated_at = updated_at
