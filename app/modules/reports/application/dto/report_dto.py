from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DailySalesPointDto(BaseModel):
    day: date
    total: Decimal = Field(default=Decimal("0"))


class TopCustomerSpendDto(BaseModel):
    customer_id: UUID
    customer_name: str
    customer_phone: str
    spent: Decimal = Field(default=Decimal("0"))


class ReportStatsDto(BaseModel):
    total_sales: Decimal = Field(default=Decimal("0"))
    purchases_count: int = 0
    gifts_count: int = 0
    pending_gifts_count: int = 0
    delivered_gifts_count: int = 0
    visit_track_gifts_count: int = 0
    points_track_gifts_count: int = 0
    average_purchase: Decimal = Field(default=Decimal("0"))
    top_customers: list[TopCustomerSpendDto] = Field(default_factory=list)
    daily_sales: list[DailySalesPointDto] = Field(default_factory=list)
    from_date: datetime
    to_date: datetime

    model_config = ConfigDict(from_attributes=True)
