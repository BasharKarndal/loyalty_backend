from pydantic import BaseModel, Field


class UpdateCustomerCommand(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=3, max_length=20)
    notes: str | None = Field(default=None, max_length=500)
