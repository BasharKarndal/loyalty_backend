from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PurchaseDto(BaseModel):
    id: UUID
    customer_id: UUID
    amount: Decimal
    points_earned: int
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseDetailDto(PurchaseDto):
    customer_name: str
    customer_phone: str
    owner_id: UUID | None = None


class PurchaseListDto(BaseModel):
    items: list[PurchaseDetailDto]
    total: int
    total_amount: Decimal = Field(default=Decimal("0"))
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
