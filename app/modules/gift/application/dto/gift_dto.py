from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GiftTypeDto(BaseModel):
    id: UUID
    owner_id: UUID | None = None
    name: str
    icon_key: str
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GiftRedemptionDto(BaseModel):
    id: UUID
    customer_id: UUID
    gift_type_id: UUID | None
    gift_type_name: str
    gift_type_icon: str
    points_used: int
    reward_track: str
    notes: str | None
    status: str
    created_at: datetime
    delivered_at: datetime | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GiftRedemptionDetailDto(GiftRedemptionDto):
    customer_name: str
    customer_phone: str
    owner_id: UUID | None = None


class GiftRedemptionListDto(BaseModel):
    items: list[GiftRedemptionDetailDto]
    total: int
    skip: int
    limit: int
    pending_count: int
    delivered_count: int

    model_config = ConfigDict(from_attributes=True)
