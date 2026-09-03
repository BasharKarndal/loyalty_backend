from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Subscription:
    id: UUID
    user_id: UUID
    starts_at: datetime
    ends_at: datetime
    notes: str | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
