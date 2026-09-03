from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def period_bounds(period: str | None) -> tuple[datetime | None, datetime | None]:
    """UTC period windows aligned with purchases list filters."""
    if not period or period == "all":
        return None, None

    now = utc_now()
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "today":
        return start_today, None

    if period == "week":
        week_start = start_today - timedelta(days=start_today.weekday())
        return week_start, None

    if period == "month":
        month_start = start_today.replace(day=1)
        return month_start, None

    return None, None


def normalize_range(from_date: datetime, to_date: datetime) -> tuple[datetime, datetime]:
    if from_date.tzinfo is None:
        from_date = from_date.replace(tzinfo=timezone.utc)
    if to_date.tzinfo is None:
        to_date = to_date.replace(tzinfo=timezone.utc)
    if from_date > to_date:
        from_date, to_date = to_date, from_date
    if (
        to_date.hour == 0
        and to_date.minute == 0
        and to_date.second == 0
        and to_date.microsecond == 0
    ):
        to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    return from_date, to_date
