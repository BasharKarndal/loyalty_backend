from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserSettingsDto(BaseModel):
    id: UUID
    user_id: UUID
    cafe_name: str
    logo_url: str | None = None
    currency: str
    visit_reward_target: int
    points_reward_target: int
    currency_per_point: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateUserSettingsCommand(BaseModel):
    cafe_name: str = Field(default="", max_length=255)
    currency: str = Field(default="د.ع", min_length=1, max_length=50)
    visit_reward_target: int = Field(default=10, gt=0, le=10000)
    points_reward_target: int = Field(default=100, gt=0, le=1000000)
    currency_per_point: Decimal = Field(default=Decimal("1000"), gt=0, max_digits=12, decimal_places=2)
