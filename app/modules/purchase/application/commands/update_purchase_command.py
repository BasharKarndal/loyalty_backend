from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class UpdatePurchaseCommand(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    product_type: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("product_type", "notes", mode="before")
    @classmethod
    def blank_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            return _empty_to_none(value)
        return value
