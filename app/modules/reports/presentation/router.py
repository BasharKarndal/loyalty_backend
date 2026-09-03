from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.responses import ResponseBuilder
from app.core.security import Permissions, require_permission
from app.modules.reports.application.dto.report_dto import ReportStatsDto
from app.modules.reports.infrastructure.repository import ReportRepository
from app.modules.user.domain.entity import User
from app.shared.date_ranges import normalize_range, period_bounds, utc_now

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/stats")
async def get_report_stats(
    period: str | None = Query(default="month", pattern="^(today|week|month|custom)$"),
    from_date: datetime | None = Query(default=None, description="Custom range start"),
    to_date: datetime | None = Query(default=None, description="Custom range end"),
    _: User = Depends(require_permission(Permissions.PURCHASES_READ)),
    session: AsyncSession = Depends(get_session),
):
    if period == "custom":
        if from_date is None or to_date is None:
            raise HTTPException(status_code=422, detail="from_date and to_date are required for custom period")
        range_from, range_to = normalize_range(from_date, to_date)
    else:
        range_from, range_to = period_bounds(period)
        if range_from is None:
            range_from = utc_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        range_to = utc_now()

    repo = ReportRepository(session)
    result = await repo.get_stats(from_date=range_from, to_date=range_to)
    payload = ReportStatsDto.model_validate(result).model_dump(mode="json")
    return ResponseBuilder.success(data=payload)
