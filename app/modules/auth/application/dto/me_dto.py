from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class SubscriptionSummaryDto(BaseModel):
    id: UUID
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    days_remaining: int

    model_config = ConfigDict(from_attributes=True)


class MeDto(BaseModel):
    id: UUID
    username: str
    full_name: str
    email: str
    phone: str | None = None
    national_id: str | None = None
    is_active: bool
    permissions: list[str] = []
    roles: list[str] = []
    is_super_admin: bool = False
    subscription: SubscriptionSummaryDto | None = None
