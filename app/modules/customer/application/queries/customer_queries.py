from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class GetCustomerQuery:
    customer_id: UUID


@dataclass(slots=True)
class ListCustomersQuery:
    skip: int
    limit: int
    search: str | None
    active_only: bool = True
    inactive_only: bool = False
