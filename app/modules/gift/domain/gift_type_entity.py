from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class GiftType:
    id: UUID
    owner_id: UUID
    name: str
    icon_key: str
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def update(
        self,
        *,
        name: str,
        icon_key: str,
        sort_order: int,
        updated_at: datetime,
    ) -> None:
        self.name = name.strip()
        self.icon_key = icon_key.strip() or "card_giftcard"
        self.sort_order = sort_order
        self.updated_at = updated_at

    def activate(self, updated_at: datetime) -> None:
        self.is_active = True
        self.updated_at = updated_at

    def deactivate(self, updated_at: datetime) -> None:
        self.is_active = False
        self.updated_at = updated_at
