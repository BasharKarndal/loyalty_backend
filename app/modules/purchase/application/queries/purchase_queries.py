from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class GetPurchaseQuery:
    purchase_id: UUID


@dataclass(slots=True)
class ListPurchasesQuery:
    skip: int
    limit: int
    customer_id: UUID | None = None
    search: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
