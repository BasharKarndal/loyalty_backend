from pydantic import BaseModel, Field


class CreateGiftTypeCommand(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    icon_key: str = Field(default="card_giftcard", max_length=100)
    sort_order: int = Field(default=0, ge=0)


class UpdateGiftTypeCommand(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    icon_key: str = Field(default="card_giftcard", max_length=100)
    sort_order: int = Field(default=0, ge=0)
