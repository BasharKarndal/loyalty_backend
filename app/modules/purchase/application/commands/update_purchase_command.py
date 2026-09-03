from decimal import Decimal

from pydantic import BaseModel, Field


class UpdatePurchaseCommand(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    notes: str | None = Field(default=None, max_length=500)
