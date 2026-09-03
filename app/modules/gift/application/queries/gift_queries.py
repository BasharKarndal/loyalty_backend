from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class GetGiftTypeQuery:
    gift_type_id: UUID


@dataclass(slots=True)
class ListGiftTypesQuery:
    active_only: bool | None = None


@dataclass(slots=True)
class GetGiftRedemptionQuery:
    redemption_id: UUID


@dataclass(slots=True)
class ListGiftRedemptionsQuery:
    skip: int
    limit: int
    customer_id: UUID | None = None
    status: str | None = None
    exclude_cancelled: bool = True
