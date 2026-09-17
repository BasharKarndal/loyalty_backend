from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PurchaseResponse(BaseModel):
    id: UUID
    customer_id: UUID
    amount: Decimal
    points_earned: int
    product_type: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseDetailResponse(PurchaseResponse):
    customer_name: str
    customer_phone: str
    owner_id: UUID | None = None


class PurchaseListResponse(BaseModel):
    items: list[PurchaseDetailResponse]
    total: int
    total_amount: Decimal
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
