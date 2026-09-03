from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class SubscriptionSummaryResponse(BaseModel):
    id: UUID
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    days_remaining: int

    model_config = ConfigDict(from_attributes=True)


class MeResponse(BaseModel):
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
    subscription: SubscriptionSummaryResponse | None = None

    model_config = ConfigDict(from_attributes=True)
