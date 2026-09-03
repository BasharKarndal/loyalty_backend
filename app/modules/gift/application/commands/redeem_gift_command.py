from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.modules.gift.domain.gift_redemption_entity import REWARD_TRACK_AMOUNT, REWARD_TRACK_VISITS


class RedeemGiftCommand(BaseModel):
    customer_id: UUID
    gift_type_id: UUID
    reward_track: str = Field(pattern="^(visits|amount)$")
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("reward_track")
    @classmethod
    def validate_track(cls, value: str) -> str:
        if value not in {REWARD_TRACK_VISITS, REWARD_TRACK_AMOUNT}:
            raise ValueError("Invalid reward track.")
        return value
