from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    id: UUID
    owner_id: UUID | None = None
    name: str
    phone: str
    notes: str | None = None
    points: int
    visit_count: int
    total_spent: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
